import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class StorageEngine:
    """
    File-based storage engine for the RDBMS.
    Each table is stored as a JSON file.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.indexes_dir = os.path.join(data_dir, "indexes")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.indexes_dir, exist_ok=True)

    def _get_table_path(self, table_name: str) -> str:
        """Get the file path for a table"""
        return os.path.join(self.data_dir, f"{table_name}.json")

    def _get_index_path(self, table_name: str, column_name: str) -> str:
        """Get the file path for an index"""
        return os.path.join(self.indexes_dir, f"{table_name}_{column_name}.json")

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        return os.path.exists(self._get_table_path(table_name))

    def create_table(self, table_name: str, schema: Dict[str, Any]) -> bool:
        """
        Create a new table with the given schema.
        Schema format: {
            'columns': {
                'column_name': {
                    'type': 'INT|VARCHAR|BOOL|DECIMAL|DATETIME',
                    'nullable': True/False,
                    'unique': True/False,
                    'primary_key': True/False
                }
            }
        }
        """
        if self.table_exists(table_name):
            return False

        table_data = {
            'schema': schema,
            'rows': [],
            'next_id': 1
        }

        with open(self._get_table_path(table_name), 'w') as f:
            json.dump(table_data, f, indent=2)

        # Create indexes for primary key and unique columns
        for col_name, col_def in schema['columns'].items():
            if col_def.get('primary_key') or col_def.get('unique'):
                self._create_index(table_name, col_name)

        return True

    def _create_index(self, table_name: str, column_name: str):
        """Create an index for a column"""
        index_data = {}
        with open(self._get_index_path(table_name, column_name), 'w') as f:
            json.dump(index_data, f, indent=2)

    def _update_index(self, table_name: str, column_name: str, value: Any, row_id: int):
        """Update an index with a new value"""
        index_path = self._get_index_path(table_name, column_name)
        if not os.path.exists(index_path):
            return

        with open(index_path, 'r') as f:
            index = json.load(f)

        key = str(value)
        if key not in index:
            index[key] = []
        index[key].append(row_id)

        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)

    def _remove_from_index(self, table_name: str, column_name: str, value: Any, row_id: int):
        """Remove a value from an index"""
        index_path = self._get_index_path(table_name, column_name)
        if not os.path.exists(index_path):
            return

        with open(index_path, 'r') as f:
            index = json.load(f)

        key = str(value)
        if key in index and row_id in index[key]:
            index[key].remove(row_id)
            if not index[key]:
                del index[key]

        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)

    def _lookup_index(self, table_name: str, column_name: str, value: Any) -> List[int]:
        """Lookup row IDs from an index"""
        index_path = self._get_index_path(table_name, column_name)
        if not os.path.exists(index_path):
            return []

        with open(index_path, 'r') as f:
            index = json.load(f)

        return index.get(str(value), [])

    def drop_table(self, table_name: str) -> bool:
        """Delete a table"""
        table_path = self._get_table_path(table_name)
        if not os.path.exists(table_path):
            return False

        # Remove table file
        os.remove(table_path)

        # Remove associated indexes
        for filename in os.listdir(self.indexes_dir):
            if filename.startswith(f"{table_name}_"):
                os.remove(os.path.join(self.indexes_dir, filename))

        return True

    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get the schema of a table"""
        if not self.table_exists(table_name):
            return None

        with open(self._get_table_path(table_name), 'r') as f:
            table_data = json.load(f)

        return table_data['schema']

    def insert_row(self, table_name: str, row_data: Dict[str, Any]) -> Optional[int]:
        """Insert a new row into a table"""
        if not self.table_exists(table_name):
            return None

        with open(self._get_table_path(table_name), 'r') as f:
            table_data = json.load(f)

        schema = table_data['schema']

        # Validate and prepare row
        row = {'_id': table_data['next_id']}

        for col_name, col_def in schema['columns'].items():
            value = row_data.get(col_name)

            # Check nullable constraint
            if value is None and not col_def.get('nullable', True):
                raise ValueError(f"Column '{col_name}' cannot be NULL")

            # Check unique constraint
            if value is not None and col_def.get('unique'):
                existing_ids = self._lookup_index(table_name, col_name, value)
                if existing_ids:
                    raise ValueError(f"Unique constraint violation on column '{col_name}'")

            row[col_name] = value

        # Add row
        table_data['rows'].append(row)
        row_id = table_data['next_id']
        table_data['next_id'] += 1

        # Update indexes
        for col_name, col_def in schema['columns'].items():
            if col_def.get('primary_key') or col_def.get('unique'):
                value = row.get(col_name)
                if value is not None:
                    self._update_index(table_name, col_name, value, row_id)

        # Save table
        with open(self._get_table_path(table_name), 'w') as f:
            json.dump(table_data, f, indent=2)

        return row_id

    def select_rows(self, table_name: str, conditions: Optional[Dict] = None,
                    columns: Optional[List[str]] = None) -> List[Dict]:
        """
        Select rows from a table.
        conditions: {'column_name': value} - simple equality conditions
        columns: list of column names to return (None = all columns)
        """
        if not self.table_exists(table_name):
            return []

        with open(self._get_table_path(table_name), 'r') as f:
            table_data = json.load(f)

        rows = table_data['rows']

        # Apply conditions (simple equality filter)
        if conditions:
            filtered_rows = []
            for row in rows:
                match = True
                for col, value in conditions.items():
                    if row.get(col) != value:
                        match = False
                        break
                if match:
                    filtered_rows.append(row)
            rows = filtered_rows

        # Select specific columns
        if columns:
            rows = [{col: row.get(col) for col in columns if col in row or col == '_id'}
                    for row in rows]

        return rows

    def update_rows(self, table_name: str, conditions: Dict, updates: Dict) -> int:
        """Update rows matching conditions"""
        if not self.table_exists(table_name):
            return 0

        with open(self._get_table_path(table_name), 'r') as f:
            table_data = json.load(f)

        schema = table_data['schema']
        count = 0

        for row in table_data['rows']:
            # Check if row matches conditions
            match = True
            for col, value in conditions.items():
                if row.get(col) != value:
                    match = False
                    break

            if match:
                # Update indexed columns
                for col_name, col_def in schema['columns'].items():
                    if (col_def.get('primary_key') or col_def.get('unique')) and col_name in updates:
                        old_value = row.get(col_name)
                        if old_value is not None:
                            self._remove_from_index(table_name, col_name, old_value, row['_id'])

                # Apply updates
                for col, value in updates.items():
                    if col in schema['columns']:
                        row[col] = value

                # Update indexes
                for col_name, col_def in schema['columns'].items():
                    if (col_def.get('primary_key') or col_def.get('unique')) and col_name in updates:
                        new_value = row.get(col_name)
                        if new_value is not None:
                            self._update_index(table_name, col_name, new_value, row['_id'])

                count += 1

        # Save table
        with open(self._get_table_path(table_name), 'w') as f:
            json.dump(table_data, f, indent=2)

        return count

    def delete_rows(self, table_name: str, conditions: Dict) -> int:
        """Delete rows matching conditions"""
        if not self.table_exists(table_name):
            return 0

        with open(self._get_table_path(table_name), 'r') as f:
            table_data = json.load(f)

        schema = table_data['schema']
        rows_to_keep = []
        count = 0

        for row in table_data['rows']:
            # Check if row matches conditions
            match = True
            for col, value in conditions.items():
                if row.get(col) != value:
                    match = False
                    break

            if match:
                # Remove from indexes
                for col_name, col_def in schema['columns'].items():
                    if col_def.get('primary_key') or col_def.get('unique'):
                        value = row.get(col_name)
                        if value is not None:
                            self._remove_from_index(table_name, col_name, value, row['_id'])
                count += 1
            else:
                rows_to_keep.append(row)

        table_data['rows'] = rows_to_keep

        # Save table
        with open(self._get_table_path(table_name), 'w') as f:
            json.dump(table_data, f, indent=2)

        return count

    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        tables = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json') and os.path.isfile(os.path.join(self.data_dir, filename)):
                tables.append(filename[:-5])  # Remove .json extension
        return tables
