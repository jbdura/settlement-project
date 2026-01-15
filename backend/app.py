from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import StorageEngine
from executor import QueryExecutor
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize RDBMS components
storage = StorageEngine(data_dir=os.path.join(os.path.dirname(__file__), 'data'))
executor = QueryExecutor(storage)

# Initialize with sample payment settlement tables
def init_sample_tables():
    """Create sample tables for payment settlement if they don't exist"""

    # Merchants table
    if not storage.table_exists('merchants'):
        executor.execute("""
            CREATE TABLE merchants (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                account_number VARCHAR(50),
                status VARCHAR(20)
            )
        """)
        print("✓ Created 'merchants' table")

    # Transactions table
    if not storage.table_exists('transactions'):
        executor.execute("""
            CREATE TABLE transactions (
                id INT PRIMARY KEY,
                merchant_id INT NOT NULL,
                amount DECIMAL NOT NULL,
                currency VARCHAR(10),
                status VARCHAR(20),
                transaction_date DATETIME
            )
        """)
        print("✓ Created 'transactions' table")

    # Settlements table
    if not storage.table_exists('settlements'):
        executor.execute("""
            CREATE TABLE settlements (
                id INT PRIMARY KEY,
                merchant_id INT NOT NULL,
                total_amount DECIMAL NOT NULL,
                status VARCHAR(20),
                settlement_date DATETIME
            )
        """)
        print("✓ Created 'settlements' table")

# Initialize tables on startup
with app.app_context():
    init_sample_tables()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Payment Settlement RDBMS API is running'
    })

@app.route('/api/query', methods=['POST'])
def execute_query():
    """
    Execute a SQL query.
    Request body: {
        "sql": "SELECT * FROM merchants"
    }
    """
    data = request.get_json()

    if not data or 'sql' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing SQL query in request body'
        }), 400

    sql = data['sql']
    result = executor.execute(sql)

    return jsonify(result)

@app.route('/api/tables', methods=['GET'])
def list_tables():
    """List all tables in the database"""
    result = executor.list_tables()
    return jsonify(result)

@app.route('/api/tables/<table_name>', methods=['GET'])
def describe_table(table_name):
    """Get schema information for a specific table"""
    result = executor.describe_table(table_name)
    return jsonify(result)

@app.route('/api/tables/<table_name>/rows', methods=['GET'])
def get_table_rows(table_name):
    """Get all rows from a table with optional filtering"""
    # Get query parameters for filtering
    conditions = {}
    for key, value in request.args.items():
        # Try to convert to appropriate type
        if value.isdigit():
            conditions[key] = int(value)
        elif value.replace('.', '').isdigit():
            conditions[key] = float(value)
        elif value.lower() == 'true':
            conditions[key] = True
        elif value.lower() == 'false':
            conditions[key] = False
        elif value.lower() == 'null':
            conditions[key] = None
        else:
            conditions[key] = value

    rows = storage.select_rows(table_name, conditions if conditions else None)

    return jsonify({
        'success': True,
        'data': rows,
        'row_count': len(rows)
    })

@app.route('/api/tables/<table_name>/rows', methods=['POST'])
def insert_row(table_name):
    """
    Insert a new row into a table.
    Request body: {
        "column1": "value1",
        "column2": "value2"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'Missing row data in request body'
        }), 400

    try:
        row_id = storage.insert_row(table_name, data)

        if row_id is None:
            return jsonify({
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }), 404

        return jsonify({
            'success': True,
            'message': f"Row inserted successfully",
            'inserted_id': row_id
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/tables/<table_name>/rows', methods=['PUT'])
def update_rows(table_name):
    """
    Update rows in a table.
    Request body: {
        "conditions": {"id": 1},
        "updates": {"status": "completed"}
    }
    """
    data = request.get_json()

    if not data or 'conditions' not in data or 'updates' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing conditions or updates in request body'
        }), 400

    conditions = data['conditions']
    updates = data['updates']

    if not conditions:
        return jsonify({
            'success': False,
            'message': 'UPDATE without conditions is not allowed'
        }), 400

    affected_rows = storage.update_rows(table_name, conditions, updates)

    return jsonify({
        'success': True,
        'message': f"Updated {affected_rows} row(s)",
        'affected_rows': affected_rows
    })

@app.route('/api/tables/<table_name>/rows', methods=['DELETE'])
def delete_rows(table_name):
    """
    Delete rows from a table.
    Request body: {
        "conditions": {"id": 1}
    }
    """
    data = request.get_json()

    if not data or 'conditions' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing conditions in request body'
        }), 400

    conditions = data['conditions']

    if not conditions:
        return jsonify({
            'success': False,
            'message': 'DELETE without conditions is not allowed'
        }), 400

    affected_rows = storage.delete_rows(table_name, conditions)

    return jsonify({
        'success': True,
        'message': f"Deleted {affected_rows} row(s)",
        'affected_rows': affected_rows
    })

@app.route('/api/join', methods=['POST'])
def execute_join():
    """
    Execute a JOIN query between two tables.
    Request body: {
        "left_table": "transactions",
        "right_table": "merchants",
        "left_key": "merchant_id",
        "right_key": "id",
        "columns": ["transactions.amount", "merchants.name"],
        "conditions": {"transactions.status": "completed"}
    }
    """
    data = request.get_json()

    required = ['left_table', 'right_table', 'left_key', 'right_key']
    if not all(k in data for k in required):
        return jsonify({
            'success': False,
            'message': f'Missing required fields: {required}'
        }), 400

    result = executor.execute_join(
        left_table=data['left_table'],
        right_table=data['right_table'],
        left_key=data['left_key'],
        right_key=data['right_key'],
        columns=data.get('columns'),
        conditions=data.get('conditions')
    )

    return jsonify(result)

@app.route('/api/merchants/report', methods=['GET'])
def merchant_report():
    """
    Get a report of merchant transactions (demonstrates JOIN functionality).
    Returns merchants with their transaction totals.
    """
    # Get all merchants
    merchants = storage.select_rows('merchants')

    # Get all transactions
    transactions = storage.select_rows('transactions')

    # Calculate totals for each merchant
    merchant_totals = {}
    for txn in transactions:
        merchant_id = txn.get('merchant_id')
        amount = txn.get('amount', 0)

        if merchant_id not in merchant_totals:
            merchant_totals[merchant_id] = {
                'total_amount': 0,
                'transaction_count': 0,
                'pending_count': 0,
                'completed_count': 0
            }

        merchant_totals[merchant_id]['total_amount'] += amount
        merchant_totals[merchant_id]['transaction_count'] += 1

        status = txn.get('status', '').lower()
        if status == 'pending':
            merchant_totals[merchant_id]['pending_count'] += 1
        elif status == 'completed':
            merchant_totals[merchant_id]['completed_count'] += 1

    # Combine merchant info with totals
    report = []
    for merchant in merchants:
        merchant_id = merchant.get('id')
        totals = merchant_totals.get(merchant_id, {
            'total_amount': 0,
            'transaction_count': 0,
            'pending_count': 0,
            'completed_count': 0
        })

        report.append({
            'merchant_id': merchant_id,
            'merchant_name': merchant.get('name'),
            'email': merchant.get('email'),
            'status': merchant.get('status'),
            **totals
        })

    return jsonify({
        'success': True,
        'data': report,
        'row_count': len(report)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Payment Settlement RDBMS API Server")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  GET    /api/health")
    print("  POST   /api/query")
    print("  GET    /api/tables")
    print("  GET    /api/tables/<name>")
    print("  GET    /api/tables/<name>/rows")
    print("  POST   /api/tables/<name>/rows")
    print("  PUT    /api/tables/<name>/rows")
    print("  DELETE /api/tables/<name>/rows")
    print("  POST   /api/join")
    print("  GET    /api/merchants/report")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
