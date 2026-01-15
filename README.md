# Payment Settlement RDBMS - Pesapal Junior Dev Challenge 2026

A complete relational database management system (RDBMS) built from scratch with:
- **Backend**: Python/Flask with custom SQL parser and storage engine
- **Frontend**: React Router with shadcn/ui components
- **Demo App**: Payment settlement management system

## 🎯 Challenge Requirements Met

✅ **RDBMS Implementation**
- Custom storage engine (JSON file-based)
- SQL parser supporting CREATE, INSERT, SELECT, UPDATE, DELETE, DROP
- Data types: INT, VARCHAR, BOOL, DECIMAL, DATETIME
- Constraints: PRIMARY KEY, UNIQUE, NOT NULL
- Basic indexing for performance

✅ **REPL/Interactive Mode**
- Command-line SQL console (`repl.py`)
- Interactive query execution
- Table exploration and schema viewing

✅ **JOIN Support**
- INNER JOIN implementation
- Merchant report demonstrates JOIN functionality

✅ **Web Application**
- Payment settlement dashboard
- Full CRUD operations for merchants and transactions
- Real-world business use case (Pesapal's domain!)

## 📁 Project Structure

```
├── backend/
│   ├── storage.py          # Storage engine with indexing
│   ├── parser.py          # SQL parser
│   ├── executor.py        # Query executor with JOIN
│   ├── repl.py           # Interactive CLI
│   ├── app.py            # Flask REST API
│   ├── requirements.txt   # Python dependencies
│   └── data/             # Database files (auto-created)
│
└── frontend/
    ├── app/
    │   ├── routes/
    │   │   ├── home.tsx      # Payment dashboard
    │   │   └── console.tsx   # SQL console
    │   ├── components/ui/    # shadcn components
    │   ├── lib/
    │   │   └── api.ts       # API client
    │   └── routes.ts        # Route configuration
    ├── .env                  # Environment config
    └── package.json
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend:**
```bash
cd backend
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
pip install flask-cors
```

3. **Test the REPL (optional):**
```bash
python repl.py
```

4. **Start the Flask API:**
```bash
python app.py
```

The API will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create `.env` file:**
```bash
echo "VITE_API_URL=http://localhost:5000/api" > .env
```

4. **Start the dev server:**
```bash
npm run dev
```

The app will run on `http://localhost:5173`

## 💻 Usage

### Option 1: Web Interface

1. Open `http://localhost:5173` in your browser
2. **Dashboard** - Manage merchants and transactions
3. **SQL Console** - Execute SQL queries interactively

### Option 2: Command Line (REPL)

```bash
cd backend
python repl.py
```

Example session:
```sql
sql> CREATE TABLE merchants (
...     id INT PRIMARY KEY,
...     name VARCHAR(255) NOT NULL,
...     email VARCHAR(255) UNIQUE
... );
✓ Table 'merchants' created successfully

sql> INSERT INTO merchants (id, name, email) VALUES (1, 'Safaricom', 'payments@safaricom.co.ke');
✓ Row inserted successfully with ID 1

sql> SELECT * FROM merchants;
✓ Query returned 1 row(s)

_id | id | name       | email
----|----|------------|----------------------
1   | 1  | Safaricom  | payments@safaricom.co.ke

sql> \tables
Tables (3):
  - merchants
  - transactions
  - settlements

sql> \desc merchants
=== Table: merchants ===

Columns:
Column         | Type    | Constraints
---------------|---------|------------------
id             | INT     | PRIMARY KEY
name           | VARCHAR | NOT NULL
email          | VARCHAR | UNIQUE

sql> \exit
Goodbye!
```

### Option 3: REST API

```bash
# Execute SQL query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM merchants"}'

# List all tables
curl http://localhost:5000/api/tables

# Get table schema
curl http://localhost:5000/api/tables/merchants

# Insert a merchant
curl -X POST http://localhost:5000/api/tables/merchants/rows \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "name": "Acme Corp", "email": "info@acme.com", "status": "active"}'

# Get merchant report (demonstrates JOIN)
curl http://localhost:5000/api/merchants/report
```

## 📊 Features Demonstrated

### 1. Storage Engine
- File-based persistence (JSON)
- Table creation and management
- Row insertion with auto-incrementing IDs
- Index creation for primary keys and unique constraints

### 2. SQL Parser
- CREATE TABLE with column definitions and constraints
- INSERT INTO with VALUES
- SELECT with WHERE conditions
- UPDATE with WHERE clause
- DELETE with WHERE clause
- DROP TABLE

### 3. Query Executor
- CRUD operations
- INNER JOIN between tables
- Constraint validation
- Index utilization

### 4. Payment Settlement Use Case
- **Merchants**: Store merchant information
- **Transactions**: Track payment transactions
- **Settlements**: Manage settlement batches
- **Reports**: JOIN merchants with transactions for analytics

## 🧪 Sample Data

The system auto-creates three tables on startup:

```sql
-- Merchants
CREATE TABLE merchants (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    account_number VARCHAR(50),
    status VARCHAR(20)
);

-- Transactions
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    merchant_id INT NOT NULL,
    amount DECIMAL NOT NULL,
    currency VARCHAR(10),
    status VARCHAR(20),
    transaction_date DATETIME
);

-- Settlements
CREATE TABLE settlements (
    id INT PRIMARY KEY,
    merchant_id INT NOT NULL,
    total_amount DECIMAL NOT NULL,
    status VARCHAR(20),
    settlement_date DATETIME
);
```

## 🎓 Technical Highlights

### Why This Approach?

1. **Payment Domain**: Relevant to Pesapal's business
2. **Real-World Use Case**: Demonstrates practical application
3. **JOIN Operations**: Shows complex query capabilities
4. **Modern Stack**: Industry-standard technologies
5. **Clean Architecture**: Separation of concerns (storage, parsing, execution)

### Key Design Decisions

- **File-based storage**: Simple, transparent, inspectable
- **JSON format**: Human-readable, easy to debug
- **Indexing**: Primary keys and unique constraints are indexed
- **Safety measures**: No UPDATE/DELETE without WHERE clause
- **Type conversion**: Automatic parsing of SQL values

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/query` | Execute SQL query |
| GET | `/api/tables` | List all tables |
| GET | `/api/tables/<name>` | Get table schema |
| GET | `/api/tables/<name>/rows` | Get table rows |
| POST | `/api/tables/<name>/rows` | Insert row |
| PUT | `/api/tables/<name>/rows` | Update rows |
| DELETE | `/api/tables/<name>/rows` | Delete rows |
| POST | `/api/join` | Execute JOIN query |
| GET | `/api/merchants/report` | Merchant transaction report |

## 🔍 Testing the RDBMS

### Test Basic Operations

```sql
-- Create a table
CREATE TABLE test (id INT PRIMARY KEY, name VARCHAR(255) NOT NULL);

-- Insert data
INSERT INTO test (id, name) VALUES (1, 'Test 1');
INSERT INTO test (id, name) VALUES (2, 'Test 2');

-- Query data
SELECT * FROM test;
SELECT * FROM test WHERE id = 1;

-- Update data
UPDATE test SET name = 'Updated' WHERE id = 1;

-- Delete data
DELETE FROM test WHERE id = 2;

-- Drop table
DROP TABLE test;
```

### Test Constraints

```sql
-- Test PRIMARY KEY (should fail on duplicate)
INSERT INTO merchants (id, name, email) VALUES (1, 'Merchant 1', 'test1@example.com');
INSERT INTO merchants (id, name, email) VALUES (1, 'Merchant 2', 'test2@example.com');
-- Error: Primary key constraint violation

-- Test UNIQUE (should fail on duplicate email)
INSERT INTO merchants (id, name, email) VALUES (2, 'Merchant 2', 'test1@example.com');
-- Error: Unique constraint violation

-- Test NOT NULL (should fail)
INSERT INTO merchants (id, email) VALUES (3, 'test3@example.com');
-- Error: Column 'name' cannot be NULL
```

### Test JOIN

```sql
-- Add merchants
INSERT INTO merchants (id, name, email, status) VALUES (1, 'Acme Corp', 'acme@example.com', 'active');
INSERT INTO merchants (id, name, email, status) VALUES (2, 'TechCo', 'tech@example.com', 'active');

-- Add transactions
INSERT INTO transactions (id, merchant_id, amount, currency, status) VALUES (1, 1, 5000, 'KES', 'completed');
INSERT INTO transactions (id, merchant_id, amount, currency, status) VALUES (2, 1, 3000, 'KES', 'pending');
INSERT INTO transactions (id, merchant_id, amount, currency, status) VALUES (3, 2, 7500, 'KES', 'completed');

-- View merchant report (uses JOIN internally)
-- Access via API: GET /api/merchants/report
```

## 🎨 Screenshots

### SQL Console
- Interactive query execution
- Table explorer with schema viewing
- Query history with success/error indicators
- Syntax highlighting for SQL

### Payment Dashboard
- Merchant management (CRUD)
- Transaction tracking
- Status updates (pending → completed/cancelled)
- Merchant report with transaction summaries

## 🏆 What Makes This Submission Stand Out

1. **Domain Expertise**: Payment settlement is Pesapal's core business
2. **Complete Solution**: Both backend RDBMS and frontend demo app
3. **Modern Tech Stack**: Industry-standard tools (Flask, React, TypeScript)
4. **Real-World Ready**: Production-quality code structure
5. **Well-Documented**: Comprehensive README and inline comments
6. **Testable**: Multiple ways to interact (CLI, API, Web UI)
7. **Extensible**: Clean architecture allows easy additions

## 📦 Deployment Considerations

### Backend
- Can be deployed to Heroku, Railway, or any Python host
- Data persistence through mounted volumes
- Environment variables for configuration

### Frontend
- Deploy to Vercel, Netlify, or Cloudflare Pages
- Update `VITE_API_URL` to production API

## 🤝 Credits

Built for the Pesapal Junior Developer Challenge 2026.

This project demonstrates:
- Systems programming (building a database from scratch)
- Web development (full-stack application)
- Software engineering (clean code, architecture)
- Domain knowledge (payment processing)

## 📄 License

This project is submitted for the Pesapal Junior Developer Challenge 2026.
