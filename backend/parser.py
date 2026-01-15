import re
from typing import Dict, List, Any, Optional, Tuple

class SQLParser:
    """
    Simple SQL parser for basic CREATE, INSERT, SELECT, UPDATE, DELETE, and DROP statements.
    Supports payment settlement use cases.
    """

    # Data type mappings
    DATA_TYPES = {
        'INT': 'INT',
        'INTEGER': 'INT',
        'VARCHAR': 'VARCHAR',
        'TEXT': 'VARCHAR',
        'BOOL': 'BOOL',
        'BOOLEAN': 'BOOL',
        'DECIMAL': 'DECIMAL',
        'FLOAT': 'DECIMAL',
        'DATETIME': 'DATETIME',
        'TIMESTAMP': 'DATETIME'
    }

    def __init__(self):
        pass

    def parse(self, sql: str) -> Dict[str, Any]:
        """
        Parse SQL statement and return a structured command.
        Returns: {
            'type': 'CREATE_TABLE'|'INSERT'|'SELECT'|'UPDATE'|'DELETE'|'DROP_TABLE',
            ... other command-specific fields
        }
        """
        sql = sql.strip()

        # Remove trailing semicolon
        if sql.endswith(';'):
            sql = sql[:-1].strip()

        # Determine statement type
        sql_upper = sql.upper()

        if sql_upper.startswith('CREATE TABLE'):
            return self._parse_create_table(sql)
        elif sql_upper.startswith('INSERT INTO'):
            return self._parse_insert(sql)
        elif sql_upper.startswith('SELECT'):
            return self._parse_select(sql)
        elif sql_upper.startswith('UPDATE'):
            return self._parse_update(sql)
        elif sql_upper.startswith('DELETE FROM'):
            return self._parse_delete(sql)
        elif sql_upper.startswith('DROP TABLE'):
            return self._parse_drop_table(sql)
        else:
            raise ValueError(f"Unsupported SQL statement: {sql[:50]}")

    def _parse_create_table(self, sql: str) -> Dict[str, Any]:
        """
        Parse CREATE TABLE statement.
        Example: CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(255) NOT NULL, email VARCHAR(255) UNIQUE)
        """
        # Extract table name and column definitions
        match = re.match(r'CREATE TABLE\s+(\w+)\s*\((.*)\)', sql, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")

        table_name = match.group(1)
        columns_str = match.group(2)

        # Parse columns
        columns = {}
        column_defs = self._split_columns(columns_str)

        for col_def in column_defs:
            col_name, col_props = self._parse_column_definition(col_def)
            columns[col_name] = col_props

        return {
            'type': 'CREATE_TABLE',
            'table_name': table_name,
            'schema': {
                'columns': columns
            }
        }

    def _split_columns(self, columns_str: str) -> List[str]:
        """Split column definitions, handling nested parentheses"""
        columns = []
        current = []
        paren_depth = 0

        for char in columns_str:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                columns.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        if current:
            columns.append(''.join(current).strip())

        return columns

    def _parse_column_definition(self, col_def: str) -> Tuple[str, Dict]:
        """Parse a single column definition"""
        parts = col_def.strip().split()
        if len(parts) < 2:
            raise ValueError(f"Invalid column definition: {col_def}")

        col_name = parts[0]

        # Extract data type (may include size like VARCHAR(255))
        data_type_match = re.match(r'(\w+)(?:\((\d+)\))?', parts[1], re.IGNORECASE)
        if not data_type_match:
            raise ValueError(f"Invalid data type: {parts[1]}")

        data_type = data_type_match.group(1).upper()
        size = data_type_match.group(2)

        # Normalize data type
        if data_type not in self.DATA_TYPES:
            raise ValueError(f"Unsupported data type: {data_type}")

        col_props = {
            'type': self.DATA_TYPES[data_type],
            'nullable': True,
            'unique': False,
            'primary_key': False
        }

        if size:
            col_props['size'] = int(size)

        # Parse constraints
        rest = ' '.join(parts[2:]).upper()

        if 'PRIMARY KEY' in rest:
            col_props['primary_key'] = True
            col_props['nullable'] = False

        if 'UNIQUE' in rest:
            col_props['unique'] = True

        if 'NOT NULL' in rest:
            col_props['nullable'] = False

        return col_name, col_props

    def _parse_insert(self, sql: str) -> Dict[str, Any]:
        """
        Parse INSERT statement.
        Example: INSERT INTO users (name, email) VALUES ('John', 'john@example.com')
        """
        # Extract table name, columns, and values
        match = re.match(
            r'INSERT INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)',
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            raise ValueError("Invalid INSERT syntax")

        table_name = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)

        # Parse columns
        columns = [col.strip() for col in columns_str.split(',')]

        # Parse values
        values = self._parse_values(values_str)

        if len(columns) != len(values):
            raise ValueError("Column count doesn't match value count")

        row_data = dict(zip(columns, values))

        return {
            'type': 'INSERT',
            'table_name': table_name,
            'data': row_data
        }

    def _parse_values(self, values_str: str) -> List[Any]:
        """Parse VALUES clause"""
        values = []
        current = []
        in_string = False
        string_char = None

        for char in values_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                values.append(''.join(current))
                current = []
                string_char = None
            elif char == ',' and not in_string:
                if current:
                    value_str = ''.join(current).strip()
                    values.append(self._convert_value(value_str))
                    current = []
            else:
                if in_string or char not in ('"', "'"):
                    current.append(char)

        if current:
            value_str = ''.join(current).strip()
            values.append(self._convert_value(value_str))

        return values

    def _convert_value(self, value_str: str) -> Any:
        """Convert string value to appropriate Python type"""
        value_str = value_str.strip()

        if value_str.upper() == 'NULL':
            return None
        elif value_str.upper() == 'TRUE':
            return True
        elif value_str.upper() == 'FALSE':
            return False
        elif value_str.replace('.', '').replace('-', '').isdigit():
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        else:
            return value_str

    def _parse_select(self, sql: str) -> Dict[str, Any]:
        """
        Parse SELECT statement.
        Example: SELECT * FROM users WHERE id = 1
        Example: SELECT name, email FROM users
        """
        # Extract columns
        select_match = re.match(r'SELECT\s+(.*?)\s+FROM\s+(\w+)', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            raise ValueError("Invalid SELECT syntax")

        columns_str = select_match.group(1).strip()
        table_name = select_match.group(2)

        # Parse columns
        if columns_str == '*':
            columns = None  # Select all columns
        else:
            columns = [col.strip() for col in columns_str.split(',')]

        # Parse WHERE clause if present
        conditions = None
        where_match = re.search(r'WHERE\s+(.*?)(?:ORDER BY|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            conditions = self._parse_where_clause(where_match.group(1).strip())

        return {
            'type': 'SELECT',
            'table_name': table_name,
            'columns': columns,
            'conditions': conditions
        }

    def _parse_where_clause(self, where_str: str) -> Dict[str, Any]:
        """Parse WHERE clause (simple equality conditions only)"""
        conditions = {}

        # Split by AND (simple implementation)
        and_parts = re.split(r'\s+AND\s+', where_str, flags=re.IGNORECASE)

        for part in and_parts:
            # Match column = value
            match = re.match(r'(\w+)\s*=\s*(.+)', part.strip())
            if match:
                col_name = match.group(1)
                value_str = match.group(2).strip()

                # Remove quotes if present
                if value_str.startswith(("'", '"')) and value_str.endswith(("'", '"')):
                    value_str = value_str[1:-1]

                conditions[col_name] = self._convert_value(value_str)

        return conditions

    def _parse_update(self, sql: str) -> Dict[str, Any]:
        """
        Parse UPDATE statement.
        Example: UPDATE users SET name = 'Jane' WHERE id = 1
        """
        # Extract table name
        match = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*?))?$', sql, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Invalid UPDATE syntax")

        table_name = match.group(1)
        set_clause = match.group(2).strip()
        where_clause = match.group(3)

        # Parse SET clause
        updates = {}
        set_parts = set_clause.split(',')
        for part in set_parts:
            col_match = re.match(r'(\w+)\s*=\s*(.+)', part.strip())
            if col_match:
                col_name = col_match.group(1)
                value_str = col_match.group(2).strip()

                # Remove quotes if present
                if value_str.startswith(("'", '"')) and value_str.endswith(("'", '"')):
                    value_str = value_str[1:-1]

                updates[col_name] = self._convert_value(value_str)

        # Parse WHERE clause
        conditions = {}
        if where_clause:
            conditions = self._parse_where_clause(where_clause)

        return {
            'type': 'UPDATE',
            'table_name': table_name,
            'updates': updates,
            'conditions': conditions
        }

    def _parse_delete(self, sql: str) -> Dict[str, Any]:
        """
        Parse DELETE statement.
        Example: DELETE FROM users WHERE id = 1
        """
        match = re.match(r'DELETE FROM\s+(\w+)(?:\s+WHERE\s+(.*?))?$', sql, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Invalid DELETE syntax")

        table_name = match.group(1)
        where_clause = match.group(2)

        conditions = {}
        if where_clause:
            conditions = self._parse_where_clause(where_clause)

        return {
            'type': 'DELETE',
            'table_name': table_name,
            'conditions': conditions
        }

    def _parse_drop_table(self, sql: str) -> Dict[str, Any]:
        """
        Parse DROP TABLE statement.
        Example: DROP TABLE users
        """
        match = re.match(r'DROP TABLE\s+(\w+)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")

        return {
            'type': 'DROP_TABLE',
            'table_name': match.group(1)
        }
