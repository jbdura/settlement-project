from typing import Dict, List, Any, Optional
from storage import StorageEngine
from parser import SQLParser

class QueryExecutor:
    """
    Executes parsed SQL commands using the storage engine.
    Supports JOIN operations for payment settlement queries.
    """

    def __init__(self, storage: StorageEngine):
        self.storage = storage
        self.parser = SQLParser()

    def execute(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL statement and return results.
        Returns: {
            'success': True/False,
            'message': str,
            'data': List[Dict] (for SELECT),
            'affected_rows': int (for UPDATE/DELETE)
        }
        """
        try:
            # Parse SQL
            command = self.parser.parse(sql)

            # Execute based on command type
            if command['type'] == 'CREATE_TABLE':
                return self._execute_create_table(command)
            elif command['type'] == 'INSERT':
                return self._execute_insert(command)
            elif command['type'] == 'SELECT':
                return self._execute_select(command)
            elif command['type'] == 'UPDATE':
                return self._execute_update(command)
            elif command['type'] == 'DELETE':
                return self._execute_delete(command)
            elif command['type'] == 'DROP_TABLE':
                return self._execute_drop_table(command)
            else:
                return {
                    'success': False,
                    'message': f"Unsupported command type: {command['type']}"
                }

        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    def _execute_create_table(self, command: Dict) -> Dict[str, Any]:
        """Execute CREATE TABLE command"""
        table_name = command['table_name']
        schema = command['schema']

        if self.storage.table_exists(table_name):
            return {
                'success': False,
                'message': f"Table '{table_name}' already exists"
            }

        success = self.storage.create_table(table_name, schema)

        return {
            'success': success,
            'message': f"Table '{table_name}' created successfully" if success else "Failed to create table"
        }

    def _execute_insert(self, command: Dict) -> Dict[str, Any]:
        """Execute INSERT command"""
        table_name = command['table_name']
        data = command['data']

        try:
            row_id = self.storage.insert_row(table_name, data)

            if row_id is None:
                return {
                    'success': False,
                    'message': f"Table '{table_name}' does not exist"
                }

            return {
                'success': True,
                'message': f"Row inserted successfully with ID {row_id}",
                'inserted_id': row_id
            }

        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }

    def _execute_select(self, command: Dict) -> Dict[str, Any]:
        """Execute SELECT command"""
        table_name = command['table_name']
        columns = command.get('columns')
        conditions = command.get('conditions')

        # Check for JOIN in table_name (simple INNER JOIN support)
        if 'JOIN' in table_name.upper():
            return self._execute_join(command)

        rows = self.storage.select_rows(table_name, conditions, columns)

        return {
            'success': True,
            'message': f"Query returned {len(rows)} row(s)",
            'data': rows,
            'row_count': len(rows)
        }

    def _execute_join(self, command: Dict) -> Dict[str, Any]:
        """
        Execute simple INNER JOIN queries.
        Example: SELECT * FROM transactions JOIN merchants ON transactions.merchant_id = merchants.id
        """
        # This is a simplified JOIN implementation
        # For the challenge, we'll parse the JOIN clause manually

        # Extract join information from the original SQL
        # This is a basic implementation - you can enhance it

        return {
            'success': False,
            'message': "JOIN queries should be parsed separately (see execute_join method)"
        }

    def execute_join(self, left_table: str, right_table: str,
                     left_key: str, right_key: str,
                     columns: Optional[List[str]] = None,
                     conditions: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute an INNER JOIN between two tables.

        Args:
            left_table: Name of the left table
            right_table: Name of the right table
            left_key: Column name in left table to join on
            right_key: Column name in right table to join on
            columns: List of columns to return (None = all)
            conditions: WHERE conditions to apply
        """
        # Get all rows from both tables
        left_rows = self.storage.select_rows(left_table, conditions)
        right_rows = self.storage.select_rows(right_table)

        # Build index on right table for faster lookup
        right_index = {}
        for row in right_rows:
            key_value = row.get(right_key)
            if key_value not in right_index:
                right_index[key_value] = []
            right_index[key_value].append(row)

        # Perform join
        joined_rows = []
        for left_row in left_rows:
            left_key_value = left_row.get(left_key)

            if left_key_value in right_index:
                for right_row in right_index[left_key_value]:
                    # Merge rows with table prefix
                    joined_row = {}

                    for key, value in left_row.items():
                        joined_row[f"{left_table}.{key}"] = value

                    for key, value in right_row.items():
                        joined_row[f"{right_table}.{key}"] = value

                    joined_rows.append(joined_row)

        # Filter columns if specified
        if columns:
            filtered_rows = []
            for row in joined_rows:
                filtered_row = {}
                for col in columns:
                    if col in row:
                        filtered_row[col] = row[col]
                    # Also check without table prefix
                    for key in row:
                        if key.endswith(f".{col}"):
                            filtered_row[col] = row[key]
                            break
                filtered_rows.append(filtered_row)
            joined_rows = filtered_rows

        return {
            'success': True,
            'message': f"JOIN returned {len(joined_rows)} row(s)",
            'data': joined_rows,
            'row_count': len(joined_rows)
        }

    def _execute_update(self, command: Dict) -> Dict[str, Any]:
        """Execute UPDATE command"""
        table_name = command['table_name']
        updates = command['updates']
        conditions = command['conditions']

        if not conditions:
            return {
                'success': False,
                'message': "UPDATE without WHERE clause is not allowed (safety measure)"
            }

        affected_rows = self.storage.update_rows(table_name, conditions, updates)

        return {
            'success': True,
            'message': f"Updated {affected_rows} row(s)",
            'affected_rows': affected_rows
        }

    def _execute_delete(self, command: Dict) -> Dict[str, Any]:
        """Execute DELETE command"""
        table_name = command['table_name']
        conditions = command['conditions']

        if not conditions:
            return {
                'success': False,
                'message': "DELETE without WHERE clause is not allowed (safety measure)"
            }

        affected_rows = self.storage.delete_rows(table_name, conditions)

        return {
            'success': True,
            'message': f"Deleted {affected_rows} row(s)",
            'affected_rows': affected_rows
        }

    def _execute_drop_table(self, command: Dict) -> Dict[str, Any]:
        """Execute DROP TABLE command"""
        table_name = command['table_name']

        success = self.storage.drop_table(table_name)

        if success:
            return {
                'success': True,
                'message': f"Table '{table_name}' dropped successfully"
            }
        else:
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

    def list_tables(self) -> Dict[str, Any]:
        """List all tables in the database"""
        tables = self.storage.list_tables()

        return {
            'success': True,
            'message': f"Found {len(tables)} table(s)",
            'data': tables
        }

    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table"""
        schema = self.storage.get_table_schema(table_name)

        if schema is None:
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

        return {
            'success': True,
            'message': f"Schema for table '{table_name}'",
            'data': schema
        }
