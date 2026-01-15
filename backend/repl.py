#!/usr/bin/env python3
"""
Interactive REPL for the Payment Settlement RDBMS.
Provides a command-line interface for executing SQL queries.
"""

import sys
import json
from storage import StorageEngine
from executor import QueryExecutor

class REPL:
    """Interactive Read-Eval-Print Loop for SQL queries"""

    def __init__(self):
        self.storage = StorageEngine()
        self.executor = QueryExecutor(self.storage)
        self.running = True

    def print_banner(self):
        """Print welcome banner"""
        print("=" * 60)
        print("  Payment Settlement RDBMS - Interactive Console")
        print("=" * 60)
        print("\nType your SQL queries or special commands:")
        print("  \\help     - Show available commands")
        print("  \\tables   - List all tables")
        print("  \\desc <table> - Describe table schema")
        print("  \\exit     - Exit the console")
        print("  \\quit     - Exit the console")
        print("\nExample queries:")
        print("  CREATE TABLE merchants (id INT PRIMARY KEY, name VARCHAR(255) NOT NULL);")
        print("  INSERT INTO merchants (id, name) VALUES (1, 'Acme Corp');")
        print("  SELECT * FROM merchants;")
        print("")

    def print_help(self):
        """Print help information"""
        print("\n=== Available Commands ===")
        print("\\help          - Show this help message")
        print("\\tables        - List all tables in the database")
        print("\\desc <table>  - Show schema for a specific table")
        print("\\exit, \\quit   - Exit the REPL")
        print("\n=== SQL Statements Supported ===")
        print("CREATE TABLE  - Create a new table")
        print("INSERT INTO   - Insert a new row")
        print("SELECT        - Query data")
        print("UPDATE        - Update existing rows")
        print("DELETE FROM   - Delete rows")
        print("DROP TABLE    - Delete a table")
        print("\n=== Data Types ===")
        print("INT, INTEGER, VARCHAR, TEXT, BOOL, BOOLEAN, DECIMAL, FLOAT, DATETIME")
        print("\n=== Constraints ===")
        print("PRIMARY KEY, UNIQUE, NOT NULL")
        print("")

    def format_table(self, data: list, headers: list = None) -> str:
        """Format data as a table"""
        if not data:
            return "No rows returned."

        # Get headers from first row if not provided
        if headers is None:
            headers = list(data[0].keys())

        # Calculate column widths
        col_widths = {h: len(str(h)) for h in headers}
        for row in data:
            for header in headers:
                value = str(row.get(header, ''))
                col_widths[header] = max(col_widths[header], len(value))

        # Build table
        lines = []

        # Header
        header_line = " | ".join(str(h).ljust(col_widths[h]) for h in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))

        # Rows
        for row in data:
            row_line = " | ".join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers)
            lines.append(row_line)

        return "\n".join(lines)

    def handle_special_command(self, command: str) -> bool:
        """
        Handle special REPL commands (starting with backslash).
        Returns True if a special command was handled, False otherwise.
        """
        command = command.strip()

        if command in ['\\exit', '\\quit']:
            print("Goodbye!")
            self.running = False
            return True

        elif command == '\\help':
            self.print_help()
            return True

        elif command == '\\tables':
            result = self.executor.list_tables()
            if result['success']:
                tables = result['data']
                if tables:
                    print(f"\nTables ({len(tables)}):")
                    for table in tables:
                        print(f"  - {table}")
                else:
                    print("\nNo tables found.")
            else:
                print(f"Error: {result['message']}")
            print("")
            return True

        elif command.startswith('\\desc '):
            table_name = command[6:].strip()
            result = self.executor.describe_table(table_name)

            if result['success']:
                schema = result['data']
                print(f"\n=== Table: {table_name} ===")
                print("\nColumns:")

                columns_data = []
                for col_name, col_def in schema['columns'].items():
                    constraints = []
                    if col_def.get('primary_key'):
                        constraints.append('PRIMARY KEY')
                    if col_def.get('unique'):
                        constraints.append('UNIQUE')
                    if not col_def.get('nullable', True):
                        constraints.append('NOT NULL')

                    columns_data.append({
                        'Column': col_name,
                        'Type': col_def['type'],
                        'Constraints': ', '.join(constraints) if constraints else '-'
                    })

                print(self.format_table(columns_data))
            else:
                print(f"Error: {result['message']}")
            print("")
            return True

        return False

    def execute_query(self, sql: str):
        """Execute a SQL query and display results"""
        if not sql.strip():
            return

        result = self.executor.execute(sql)

        if result['success']:
            print(f"✓ {result['message']}")

            # Display data if available
            if 'data' in result and result['data']:
                print("")
                print(self.format_table(result['data']))

            # Display affected rows count
            if 'affected_rows' in result:
                print(f"Affected rows: {result['affected_rows']}")

            # Display inserted ID
            if 'inserted_id' in result:
                print(f"Inserted ID: {result['inserted_id']}")
        else:
            print(f"✗ Error: {result['message']}")

        print("")

    def run(self):
        """Run the REPL"""
        self.print_banner()

        current_query = []

        while self.running:
            try:
                # Prompt
                if current_query:
                    prompt = "... "
                else:
                    prompt = "sql> "

                line = input(prompt).strip()

                # Handle special commands
                if line.startswith('\\'):
                    if self.handle_special_command(line):
                        current_query = []
                        continue

                # Accumulate multi-line queries
                current_query.append(line)

                # Execute when we see a semicolon
                full_query = ' '.join(current_query)
                if ';' in full_query:
                    self.execute_query(full_query)
                    current_query = []

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type \\exit to quit.")
                current_query = []

            except EOFError:
                print("\nGoodbye!")
                break

            except Exception as e:
                print(f"Error: {e}")
                current_query = []

def main():
    """Main entry point"""
    repl = REPL()
    repl.run()

if __name__ == '__main__':
    main()
