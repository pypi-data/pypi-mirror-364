"""
DBAPI implementation for Cloudflare D1 REST API.
"""

from typing import Any, Dict, List, Optional, Sequence, Union
import httpx


# DBAPI Exception hierarchy
class Error(Exception):
    """Base exception for DBAPI errors."""

    pass


class Warning(Exception):
    """Warning exception."""

    pass


class InterfaceError(Error):
    """Error related to the database interface."""

    pass


class DatabaseError(Error):
    """Error related to the database."""

    pass


class DataError(DatabaseError):
    """Error due to problems with the processed data."""

    pass


class OperationalError(DatabaseError):
    """Error related to the database's operation."""

    pass


class IntegrityError(DatabaseError):
    """Error when the relational integrity is affected."""

    pass


class InternalError(DatabaseError):
    """Error when the database encounters an internal error."""

    pass


class ProgrammingError(DatabaseError):
    """Error due to programming error."""

    pass


class NotSupportedError(DatabaseError):
    """Error when a not supported method or API is used."""

    pass


class Row:
    """Row object that behaves like both a tuple and has named access."""

    def __init__(self, data: Dict[str, Any], description: List[tuple]):
        """Initialize row with data and column descriptions."""
        self._data = data
        self._description = description
        self._keys = (
            [desc[0] for desc in description] if description else list(data.keys())
        )
        self._values = [data.get(key) for key in self._keys]

    def __getitem__(self, key: Union[int, str]) -> Any:
        """Get item by index or column name."""
        if isinstance(key, int):
            return self._values[key]
        elif isinstance(key, str):
            return self._data[key]
        else:
            raise TypeError("Key must be int or str")

    def __iter__(self):
        """Iterate over values."""
        return iter(self._values)

    def __len__(self):
        """Get number of columns."""
        return len(self._values)

    def __bool__(self):
        """Check if row has data."""
        return bool(self._values)

    def __repr__(self):
        """String representation of the row."""
        return f"Row({dict(zip(self._keys, self._values))})"

    def keys(self):
        """Get column names."""
        return self._keys

    def values(self):
        """Get values."""
        return self._values

    def items(self):
        """Get (key, value) pairs."""
        return zip(self._keys, self._values)

    # Add attribute access for compatibility
    def __getattr__(self, name: str) -> Any:
        """Allow attribute access to column values."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'Row' object has no attribute '{name}'")


class Cursor:
    """DBAPI-compatible cursor for D1 connections."""

    def __init__(self, connection: "Connection"):
        """Initialize cursor with connection reference."""
        self.connection = connection
        self._result_data = None
        self._description = None
        self._rowcount = -1
        self._arraysize = 1
        self._closed = False
        self._position = 0
        self._last_result_meta = {}

    def execute(
        self, operation: str, parameters: Optional[Sequence] = None
    ) -> "Cursor":
        """Execute a database operation."""
        if self._closed:
            raise ProgrammingError("Cursor is closed")

        try:
            result = self.connection._execute_query(operation, parameters)
            self._result_data = result.get("results", [])
            self._last_result_meta = result.get("meta", {})
            self._rowcount = self._last_result_meta.get(
                "changes", len(self._result_data)
            )

            # Always set description for SELECT-like statements
            # Check if this looks like a SELECT statement or any statement that might return rows
            operation_upper = operation.strip().upper()
            if (
                operation_upper.startswith(("SELECT", "PRAGMA", "WITH"))
                or "RETURNING" in operation_upper
            ):
                if self._result_data:
                    # Build description from first row if available
                    first_row = self._result_data[0]
                    self._description = [
                        (name, None, None, None, None, None, None)
                        for name in first_row.keys()
                    ]
                else:
                    # Even if no results, we need to indicate this was a SELECT-like query
                    # We can't know the column names without results, so we'll set an empty description
                    # that still indicates this is a row-returning statement
                    self._description = []
            else:
                # For non-SELECT statements (INSERT, UPDATE, DELETE, etc.), description should be None
                self._description = None

            self._position = 0
            return self

        except Exception as e:
            raise OperationalError(f"Execute failed: {e}")

    def executemany(
        self, operation: str, seq_of_parameters: Sequence[Sequence]
    ) -> "Cursor":
        """Execute operation multiple times."""
        if self._closed:
            raise ProgrammingError("Cursor is closed")

        total_rowcount = 0
        for parameters in seq_of_parameters:
            self.execute(operation, parameters)
            if self._rowcount >= 0:
                total_rowcount += self._rowcount

        self._rowcount = total_rowcount
        return self

    def fetchone(self) -> Optional[tuple]:
        """Fetch next row as a tuple."""
        if self._closed:
            raise ProgrammingError("Cursor is closed")

        if not self._result_data or self._position >= len(self._result_data):
            return None

        row_data = self._result_data[self._position]
        self._position += 1

        # Return a tuple of values in the order they appear in the description
        if self._description:
            column_names = [desc[0] for desc in self._description]
            return tuple(row_data.get(name) for name in column_names)
        else:
            # If no description, return values in the order they appear in the dict
            return tuple(row_data.values())

    def fetchmany(self, size: Optional[int] = None) -> List[tuple]:
        """Fetch multiple rows."""
        if self._closed:
            raise ProgrammingError("Cursor is closed")

        if size is None:
            size = self._arraysize

        rows = []
        for _ in range(size):
            row = self.fetchone()
            if row is None:
                break
            rows.append(row)

        return rows

    def fetchall(self) -> List[tuple]:
        """Fetch all remaining rows."""
        if self._closed:
            raise ProgrammingError("Cursor is closed")

        rows = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            rows.append(row)

        return rows

    def close(self) -> None:
        """Close the cursor."""
        self._closed = True
        self._result_data = None
        self._description = None

    @property
    def description(self) -> Optional[List[tuple]]:
        """Get column descriptions.

        Returns:
            List of 7-tuples (name, type_code, display_size, internal_size,
            precision, scale, null_ok) for each column, or None for non-SELECT statements.
        """
        return self._description

    @property
    def rowcount(self) -> int:
        """Get number of affected rows."""
        return self._rowcount

    @property
    def arraysize(self) -> int:
        """Get/set array size for fetchmany."""
        return self._arraysize

    @arraysize.setter
    def arraysize(self, size: int) -> None:
        """Set array size for fetchmany."""
        self._arraysize = size

    @property
    def lastrowid(self) -> Optional[int]:
        """Get the ID of the last inserted row."""
        if hasattr(self, "_last_result_meta"):
            return self._last_result_meta.get("last_row_id")
        return None

    def __iter__(self):
        """Make cursor iterable."""
        return self

    def __next__(self):
        """Get next row for iteration."""
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row


class Connection:
    """DBAPI-compatible connection for Cloudflare D1."""

    def __init__(self, account_id: str, database_id: str, api_token: str, **kwargs):
        """Initialize D1 connection."""
        self.account_id = account_id
        self.database_id = database_id
        self.api_token = api_token

        # Build the D1 REST API URL
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}"

        # HTTP client
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        # Connection state
        self._closed = False

    def cursor(self) -> Cursor:
        """Create a cursor."""
        if self._closed:
            raise InterfaceError("Connection is closed")
        return Cursor(self)

    def close(self) -> None:
        """Close the connection."""
        if not self._closed:
            self.client.close()
            self._closed = True

    def commit(self) -> None:
        """Commit transaction (no-op for D1)."""
        # D1 auto-commits each query
        pass

    def rollback(self) -> None:
        """Rollback transaction (not supported by D1)."""
        # D1 doesn't support explicit transactions via REST API
        pass

    def execute(self, operation: str, parameters: Optional[Sequence] = None):
        """Execute operation directly on connection (convenience method)."""
        cursor = self.cursor()
        cursor.execute(operation, parameters)
        return cursor

    def _execute_query(
        self, query: str, parameters: Optional[Sequence] = None
    ) -> Dict[str, Any]:
        """Internal method to execute SQL query via D1 REST API."""
        if self._closed:
            raise InterfaceError("Connection is closed")

        # Prepare the request payload
        payload = {"sql": query}

        if parameters:
            # Convert parameters to list for D1 API
            if isinstance(parameters, (tuple, list)):
                payload["params"] = list(parameters)
            elif isinstance(parameters, dict):
                # Handle named parameters by converting to positional
                # This is a simple implementation - more complex queries might need better handling
                payload["params"] = list(parameters.values())
            else:
                payload["params"] = [parameters]

        try:
            # Make the request to D1 REST API
            response = self.client.post(f"{self.base_url}/query", json=payload)
            response.raise_for_status()

            # Parse response
            data = response.json()

            if not data.get("success", False):
                errors = data.get("errors", [])
                if errors:
                    error_msg = errors[0].get("message", "Unknown error")
                    raise OperationalError(f"D1 API error: {error_msg}")
                else:
                    raise OperationalError("D1 API request failed")

            # Extract result data
            result_data = data.get("result", [])
            if result_data:
                query_result = result_data[0]
                return {
                    "results": query_result.get("results", []),
                    "meta": query_result.get("meta", {}),
                    "success": query_result.get("success", True),
                }
            else:
                return {"results": [], "meta": {}, "success": True}

        except httpx.RequestError as e:
            raise OperationalError(f"HTTP request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise OperationalError(
                f"HTTP error {e.response.status_code}: {e.response.text}"
            )

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed


# DBAPI module interface
class CloudflareD1DBAPI:
    """DBAPI module for Cloudflare D1."""

    # DBAPI 2.0 required module attributes
    apilevel = "2.0"
    threadsafety = 1
    paramstyle = "qmark"

    # Exception classes
    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    DataError = DataError
    OperationalError = OperationalError
    IntegrityError = IntegrityError
    InternalError = InternalError
    ProgrammingError = ProgrammingError
    NotSupportedError = NotSupportedError

    @staticmethod
    def connect(**kwargs) -> Connection:
        """Create a new database connection."""
        return Connection(**kwargs)


# For backwards compatibility, provide module-level access
apilevel = CloudflareD1DBAPI.apilevel
threadsafety = CloudflareD1DBAPI.threadsafety
paramstyle = CloudflareD1DBAPI.paramstyle


def connect(**kwargs) -> Connection:
    """Create a new database connection."""
    return CloudflareD1DBAPI.connect(**kwargs)
