import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { api, type QueryResult, type TableSchema } from '../lib/api';

export default function Console() {
  const [ sql, setSql ] = useState('SELECT * FROM merchants;');
  const [ result, setResult ] = useState<QueryResult | null>(null);
  const [ loading, setLoading ] = useState(false);
  const [ tables, setTables ] = useState<string[]>([]);
  const [ selectedTable, setSelectedTable ] = useState<string>('');
  const [ tableSchema, setTableSchema ] = useState<TableSchema | null>(null);
  const [ queryHistory, setQueryHistory ] = useState<Array<{ sql: string; timestamp: Date; success: boolean }>>([]);

  useEffect(() => {
    loadTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      loadTableSchema(selectedTable);
    }
  }, [ selectedTable ]);

  const loadTables = async () => {
    try {
      const result = await api.getTables();
      if (result.success && result.data) {
        setTables(result.data);
        if (result.data.length > 0 && !selectedTable) {
          setSelectedTable(result.data[ 0 ]);
        }
      }
    } catch (error) {
      console.error('Error loading tables:', error);
    }
  };

  const loadTableSchema = async (tableName: string) => {
    try {
      const schema = await api.getTableSchema(tableName);
      setTableSchema(schema);
    } catch (error) {
      console.error('Error loading schema:', error);
    }
  };

  const executeQuery = async () => {
    if (!sql.trim()) return;

    setLoading(true);
    try {
      const queryResult = await api.executeQuery(sql);
      setResult(queryResult);
      setQueryHistory(prev => [
        { sql, timestamp: new Date(), success: queryResult.success },
        ...prev.slice(0, 9) // Keep last 10 queries
      ]);

      // Refresh tables list if CREATE/DROP was executed
      if (sql.toUpperCase().includes('CREATE TABLE') || sql.toUpperCase().includes('DROP TABLE')) {
        await loadTables();
      }
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      executeQuery();
    }
  };

  const insertSampleQuery = (query: string) => {
    setSql(query);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Payment Settlement RDBMS</h1>
          <p className="text-muted-foreground">Interactive SQL Console</p>
        </div>
        <Badge variant="outline" className="text-sm">
          {tables.length} table{tables.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SQL Console */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>SQL Console</CardTitle>
              <CardDescription>
                Enter your SQL queries below (Cmd/Ctrl + Enter to execute)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <textarea
                  value={sql}
                  onChange={(e) => setSql(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-full h-32 p-3 font-mono text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="SELECT * FROM merchants WHERE status = 'active';"
                />
              </div>

              <Button onClick={executeQuery} disabled={loading} className="w-full">
                {loading ? 'Executing...' : '▶ Run Query'}
              </Button>

              {/* Sample Queries */}
              <div className="space-y-2">
                <p className="text-sm font-medium">Quick Examples:</p>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => insertSampleQuery('SELECT * FROM merchants;')}
                  >
                    Select Merchants
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => insertSampleQuery('SELECT * FROM transactions WHERE status = \'completed\';')}
                  >
                    Completed Transactions
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => insertSampleQuery('INSERT INTO merchants (id, name, email, status) VALUES (101, \'New Merchant\', \'new@example.com\', \'active\');')}
                  >
                    Insert Merchant
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Query Result */}
          {result && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Query Result
                  <Badge variant={result.success ? 'default' : 'destructive'}>
                    {result.success ? '✓ Success' : '✗ Error'}
                  </Badge>
                </CardTitle>
                <CardDescription>{result.message}</CardDescription>
              </CardHeader>
              <CardContent>
                {result.success && result.data && result.data.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-sm">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          {Object.keys(result.data[ 0 ]).map((key) => (
                            <th key={key} className="px-4 py-2 text-left font-medium">
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.data.map((row, idx) => (
                          <tr key={idx} className="border-b hover:bg-muted/50">
                            {Object.values(row).map((value, cellIdx) => (
                              <td key={cellIdx} className="px-4 py-2">
                                {value === null ? (
                                  <span className="text-muted-foreground italic">NULL</span>
                                ) : (
                                  String(value)
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="mt-4 text-sm text-muted-foreground">
                      {result.row_count} row{result.row_count !== 1 ? 's' : ''} returned
                    </p>
                  </div>
                ) : result.success && result.data && result.data.length === 0 ? (
                  <p className="text-muted-foreground">No rows returned</p>
                ) : result.affected_rows !== undefined ? (
                  <p className="text-muted-foreground">
                    {result.affected_rows} row{result.affected_rows !== 1 ? 's' : ''} affected
                  </p>
                ) : result.inserted_id !== undefined ? (
                  <p className="text-muted-foreground">
                    Row inserted with ID: {result.inserted_id}
                  </p>
                ) : null}
              </CardContent>
            </Card>
          )}

          {/* Query History */}
          {queryHistory.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Query History</CardTitle>
                <CardDescription>Recent query execution log</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {queryHistory.map((entry, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2 p-2 rounded border hover:bg-muted/50 cursor-pointer"
                      onClick={() => setSql(entry.sql)}
                    >
                      <Badge variant={entry.success ? 'default' : 'destructive'} className="mt-1">
                        {entry.success ? '✓' : '✗'}
                      </Badge>
                      <div className="flex-1 min-w-0">
                        <p className="font-mono text-xs truncate">{entry.sql}</p>
                        <p className="text-xs text-muted-foreground">
                          {entry.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Table Explorer */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Table Explorer</CardTitle>
              <CardDescription>Browse database tables</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Select Table</label>
                <select
                  value={selectedTable}
                  onChange={(e) => setSelectedTable(e.target.value)}
                  className="w-full p-2 border rounded-md"
                >
                  {tables.map((table) => (
                    <option key={table} value={table}>
                      {table}
                    </option>
                  ))}
                </select>
              </div>

              {tableSchema?.success && tableSchema.data && (
                <div>
                  <h4 className="font-medium mb-2">Columns</h4>
                  <div className="space-y-2">
                    {Object.entries(tableSchema.data.columns).map(([ name, def ]) => (
                      <div key={name} className="p-2 border rounded text-sm">
                        <div className="font-medium">{name}</div>
                        <div className="text-xs text-muted-foreground">
                          {def.type}
                          {def.primary_key && ' • PRIMARY KEY'}
                          {def.unique && ' • UNIQUE'}
                          {!def.nullable && ' • NOT NULL'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Button
                variant="outline"
                className="w-full"
                onClick={() => insertSampleQuery(`SELECT * FROM ${selectedTable};`)}
              >
                Query This Table
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => insertSampleQuery('CREATE TABLE example (id INT PRIMARY KEY, name VARCHAR(255) NOT NULL);')}
              >
                Create Table
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => window.location.href = '/'}
              >
                View Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
