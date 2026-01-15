# Payment Settlement RDBMS - Backend

A simple relational database management system built in Python with Flask API, designed for payment settlement operations.

## Features

✅ **Core RDBMS Functionality:**
- SQL parser supporting CREATE, INSERT, SELECT, UPDATE, DELETE, DROP
- File-based storage engine (JSON)
- Primary key and unique constraints
- Basic indexing for faster lookups
- NOT NULL constraints
- INNER JOIN support

✅ **Data Types:**
- INT/INTEGER
- VARCHAR/TEXT
- BOOL/BOOLEAN
- DECIMAL/FLOAT
- DATETIME/TIMESTAMP

✅ **Interactive REPL:**
- Command-line SQL console
- Multi-line query support
- Special commands (\tables, \desc, \help)

✅ **REST API:**
- Full CRUD operations
- SQL query execution endpoint
- Table management
- JOIN operations
- Merchant reporting (demo feature)

## Project Structure

```
backend/
├── storage.py          # Storage engine (file-based)
├── parser.py          # SQL parser
├── executor.py        # Query executor with JOIN support
├── repl.py           # Interactive command-line interface
├── app.py            # Flask REST API
├── requirements.txt   # Python dependencies
└── data/             # Database files (auto-created)
```

## Installation

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Add Flask-CORS to requirements.txt:**
```bash
echo "flask-cors==5.0.0" >> requirements.txt
pip install flask-cors
```

## Usage

### Option 1: Interactive REPL (Command Line)

```bash
python repl.py
```

Example session:
```sql
sql> CREATE TABLE merchants (
...     id INT PRIMARY KEY,
...     name VARCHAR(255) NOT NULL,
...     email VARCHAR(255) UNIQUE
... );

sql> INSERT INTO merchants (id, name, email) VALUES (1, 'Acme Corp', 'info@acme.com');

sql> SELECT * FROM merchants;

sql> \tables

sql> \desc merchants

sql> \exit
```

### Option 2: Flask API Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Core Operations

**Execute SQL Query:**
```bash
POST /api/query
Content-Type: application/json

{
  "sql": "SELECT * FROM merchants WHERE status = 'active'"
}
```

**List All Tables:**
```bash
GET /api/tables
```

**Describe Table Schema:**
```bash
GET /api/tables/merchants
```

### CRUD Operations

**Get Table Rows:**
```bash
GET /api/tables/merchants/rows
GET /api/tables/merchants/rows?status=active
```

**Insert Row:**
```bash
POST /api/tables/merchants/rows
Content-Type: application/json

{
  "id": 1,
  "name": "Acme Corp",
  "email": "info@acme.com",
  "status": "active"
}
```

**Update Rows:**
```bash
PUT /api/tables/merchants/rows
Content-Type: application/json

{
  "conditions": {"id": 1},
  "updates": {"status": "inactive"}
}
```

**Delete Rows:**
```bash
DELETE /api/tables/merchants/rows
Content-Type: application/json

{
  "conditions": {"id": 1}
}
```

### JOIN Operations

**Execute JOIN Query:**
```bash
POST /api/join
Content-Type: application/json

{
  "left_table": "transactions",
  "right_table": "merchants",
  "left_key": "merchant_id",
  "right_key": "id",
  "columns": ["transactions.amount", "merchants.name"],
  "conditions": {"transactions.status": "completed"}
}
```

**Merchant Report (Demo):**
```bash
GET /api/merchants/report
```

Returns merchant transaction summaries with totals.

## Sample Data

The system auto-creates these tables on startup:

### merchants
```sql
CREATE TABLE merchants (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    account_number VARCHAR(50),
    status VARCHAR(20)
);
```

### transactions
```sql
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    merchant_id INT NOT NULL,
    amount DECIMAL NOT NULL,
    currency VARCHAR(10),
    status VARCHAR(20),
    transaction_date DATETIME
);
```

### settlements
```sql
CREATE TABLE settlements (
    id INT PRIMARY KEY,
    merchant_id INT NOT NULL,
    total_amount DECIMAL NOT NULL,
    status VARCHAR(20),
    settlement_date DATETIME
);
```

## Example Queries

### Create a merchant:
```sql
INSERT INTO merchants (id, name, email, account_number, status)
VALUES (1, 'Safaricom Ltd', 'payments@safaricom.co.ke', 'ACC001', 'active');
```

### Add transactions:
```sql
INSERT INTO transactions (id, merchant_id, amount, currency, status, transaction_date)
VALUES (1, 1, 5000.00, 'KES', 'completed', '2026-01-15 10:30:00');
```

### Query with JOIN:
```sql
SELECT merchants.name, transactions.amount, transactions.status
FROM transactions
JOIN merchants ON transactions.merchant_id = merchants.id
WHERE transactions.status = 'completed';
```

### Update transaction status:
```sql
UPDATE transactions SET status = 'settled' WHERE id = 1;
```

### Delete old records:
```sql
DELETE FROM transactions WHERE status = 'cancelled';
```

## File Storage

- All tables are stored as JSON files in the `data/` directory
- Indexes are stored in `data/indexes/`
- Each table is a single `.json` file
- Simple, transparent, easy to inspect

## Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:5000/api/health

# List tables
curl http://localhost:5000/api/tables

# Execute query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM merchants"}'

# Insert merchant
curl -X POST http://localhost:5000/api/tables/merchants/rows \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "name": "Test Merchant", "email": "test@example.com", "status": "active"}'
```

## Architecture

```
┌─────────────────┐
│   Flask API     │
│   (app.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Executor  │  ◄── Handles JOIN operations
│  (executor.py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQL Parser    │  ◄── Parses SQL statements
│   (parser.py)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Storage Engine  │  ◄── File-based persistence
│  (storage.py)   │      + Indexing
└─────────────────┘
```

## Next Steps

Connect this backend to your React frontend to create the complete payment settlement application!
