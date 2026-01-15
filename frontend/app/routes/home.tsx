import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { api } from '../lib/api';

interface Merchant {
  _id: number;
  id: number;
  name: string;
  email: string;
  account_number?: string;
  status: string;
}

interface Transaction {
  _id: number;
  id: number;
  merchant_id: number;
  amount: number;
  currency: string;
  status: string;
  transaction_date?: string;
}

interface MerchantReport {
  merchant_id: number;
  merchant_name: string;
  email: string;
  status: string;
  total_amount: number;
  transaction_count: number;
  pending_count: number;
  completed_count: number;
}

export default function Home() {
  const [ merchants, setMerchants ] = useState<Merchant[]>([]);
  const [ transactions, setTransactions ] = useState<Transaction[]>([]);
  const [ report, setReport ] = useState<MerchantReport[]>([]);
  const [ loading, setLoading ] = useState(false);
  const [ activeTab, setActiveTab ] = useState<'merchants' | 'transactions' | 'report'>('report');

  // New merchant form
  const [ newMerchant, setNewMerchant ] = useState({
    id: '',
    name: '',
    email: '',
    account_number: '',
    status: 'active'
  });

  // New transaction form
  const [ newTransaction, setNewTransaction ] = useState({
    id: '',
    merchant_id: '',
    amount: '',
    currency: 'KES',
    status: 'pending',
    transaction_date: new Date().toISOString()
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ merchantsRes, transactionsRes, reportRes ] = await Promise.all([
        api.getTableRows('merchants'),
        api.getTableRows('transactions'),
        api.getMerchantReport()
      ]);

      if (merchantsRes.success && merchantsRes.data) {
        setMerchants(merchantsRes.data);
      }

      if (transactionsRes.success && transactionsRes.data) {
        setTransactions(transactionsRes.data);
      }

      if (reportRes.success && reportRes.data) {
        setReport(reportRes.data);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const addMerchant = async () => {
    try {
      const result = await api.insertRow('merchants', {
        id: parseInt(newMerchant.id),
        name: newMerchant.name,
        email: newMerchant.email,
        account_number: newMerchant.account_number,
        status: newMerchant.status
      });

      if (result.success) {
        alert('Merchant added successfully!');
        setNewMerchant({ id: '', name: '', email: '', account_number: '', status: 'active' });
        loadData();
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error}`);
    }
  };

  const addTransaction = async () => {
    try {
      const result = await api.insertRow('transactions', {
        id: parseInt(newTransaction.id),
        merchant_id: parseInt(newTransaction.merchant_id),
        amount: parseFloat(newTransaction.amount),
        currency: newTransaction.currency,
        status: newTransaction.status,
        transaction_date: newTransaction.transaction_date
      });

      if (result.success) {
        alert('Transaction added successfully!');
        setNewTransaction({
          id: '',
          merchant_id: '',
          amount: '',
          currency: 'KES',
          status: 'pending',
          transaction_date: new Date().toISOString()
        });
        loadData();
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error}`);
    }
  };

  const updateTransactionStatus = async (id: number, newStatus: string) => {
    try {
      const result = await api.updateRows('transactions', { id }, { status: newStatus });
      if (result.success) {
        loadData();
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error}`);
    }
  };

  const deleteMerchant = async (id: number) => {
    if (!confirm('Are you sure you want to delete this merchant?')) return;

    try {
      const result = await api.deleteRows('merchants', { id });
      if (result.success) {
        loadData();
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'default';
      case 'completed': return 'default';
      case 'pending': return 'secondary';
      case 'cancelled': return 'destructive';
      case 'inactive': return 'outline';
      default: return 'outline';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Payment Settlement System</h1>
          <p className="text-muted-foreground">Manage merchants, transactions, and settlements</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.location.href = '/console'}>
            SQL Console
          </Button>
          <Button onClick={loadData} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Merchants</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{merchants.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{transactions.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {transactions.filter(t => t.status === 'pending').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {transactions.filter(t => t.status === 'completed').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'report' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
          onClick={() => setActiveTab('report')}
        >
          Merchant Report
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'merchants' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
          onClick={() => setActiveTab('merchants')}
        >
          Merchants
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'transactions' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
          onClick={() => setActiveTab('transactions')}
        >
          Transactions
        </button>
      </div>

      {/* Merchant Report Tab */}
      {activeTab === 'report' && (
        <Card>
          <CardHeader>
            <CardTitle>Merchant Transaction Report</CardTitle>
            <CardDescription>Overview of all merchant transactions (demonstrates JOIN functionality)</CardDescription>
          </CardHeader>
          <CardContent>
            {report.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3 font-medium">Merchant</th>
                      <th className="text-left p-3 font-medium">Email</th>
                      <th className="text-left p-3 font-medium">Status</th>
                      <th className="text-right p-3 font-medium">Total Amount</th>
                      <th className="text-right p-3 font-medium">Transactions</th>
                      <th className="text-right p-3 font-medium">Pending</th>
                      <th className="text-right p-3 font-medium">Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.map((item) => (
                      <tr key={item.merchant_id} className="border-b hover:bg-muted/50">
                        <td className="p-3 font-medium">{item.merchant_name}</td>
                        <td className="p-3">{item.email}</td>
                        <td className="p-3">
                          <Badge variant={getStatusColor(item.status)}>
                            {item.status}
                          </Badge>
                        </td>
                        <td className="p-3 text-right font-mono">
                          {item.total_amount.toFixed(2)}
                        </td>
                        <td className="p-3 text-right">{item.transaction_count}</td>
                        <td className="p-3 text-right">{item.pending_count}</td>
                        <td className="p-3 text-right">{item.completed_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">No data available</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Merchants Tab */}
      {activeTab === 'merchants' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Merchants</CardTitle>
                <CardDescription>All registered merchants</CardDescription>
              </CardHeader>
              <CardContent>
                {merchants.length > 0 ? (
                  <div className="space-y-3">
                    {merchants.map((merchant) => (
                      <div key={merchant._id} className="border rounded-lg p-4 hover:bg-muted/50">
                        <div className="flex items-start justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h3 className="font-semibold">{merchant.name}</h3>
                              <Badge variant={getStatusColor(merchant.status)}>
                                {merchant.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">{merchant.email}</p>
                            {merchant.account_number && (
                              <p className="text-xs text-muted-foreground">
                                Account: {merchant.account_number}
                              </p>
                            )}
                          </div>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => deleteMerchant(merchant.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">No merchants found</p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Add Merchant</CardTitle>
              <CardDescription>Register a new merchant</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>ID</Label>
                <Input
                  type="number"
                  value={newMerchant.id}
                  onChange={(e) => setNewMerchant({ ...newMerchant, id: e.target.value })}
                  placeholder="1"
                />
              </div>
              <div className="space-y-2">
                <Label>Name</Label>
                <Input
                  value={newMerchant.name}
                  onChange={(e) => setNewMerchant({ ...newMerchant, name: e.target.value })}
                  placeholder="Acme Corp"
                />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={newMerchant.email}
                  onChange={(e) => setNewMerchant({ ...newMerchant, email: e.target.value })}
                  placeholder="contact@acme.com"
                />
              </div>
              <div className="space-y-2">
                <Label>Account Number</Label>
                <Input
                  value={newMerchant.account_number}
                  onChange={(e) => setNewMerchant({ ...newMerchant, account_number: e.target.value })}
                  placeholder="ACC001"
                />
              </div>
              <div className="space-y-2">
                <Label>Status</Label>
                <select
                  value={newMerchant.status}
                  onChange={(e) => setNewMerchant({ ...newMerchant, status: e.target.value })}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
              <Button onClick={addMerchant} className="w-full">
                Add Merchant
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Transactions Tab */}
      {activeTab === 'transactions' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Transactions</CardTitle>
                <CardDescription>All payment transactions</CardDescription>
              </CardHeader>
              <CardContent>
                {transactions.length > 0 ? (
                  <div className="space-y-3">
                    {transactions.map((txn) => (
                      <div key={txn._id} className="border rounded-lg p-4 hover:bg-muted/50">
                        <div className="flex items-start justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-semibold">
                                {txn.currency} {txn.amount.toFixed(2)}
                              </span>
                              <Badge variant={getStatusColor(txn.status)}>
                                {txn.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              Merchant ID: {txn.merchant_id}
                            </p>
                            {txn.transaction_date && (
                              <p className="text-xs text-muted-foreground">
                                {new Date(txn.transaction_date).toLocaleString()}
                              </p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            {txn.status === 'pending' && (
                              <Button
                                size="sm"
                                onClick={() => updateTransactionStatus(txn.id, 'completed')}
                              >
                                Complete
                              </Button>
                            )}
                            {txn.status === 'pending' && (
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => updateTransactionStatus(txn.id, 'cancelled')}
                              >
                                Cancel
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">No transactions found</p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Add Transaction</CardTitle>
              <CardDescription>Create a new transaction</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>ID</Label>
                <Input
                  type="number"
                  value={newTransaction.id}
                  onChange={(e) => setNewTransaction({ ...newTransaction, id: e.target.value })}
                  placeholder="1"
                />
              </div>
              <div className="space-y-2">
                <Label>Merchant ID</Label>
                <Input
                  type="number"
                  value={newTransaction.merchant_id}
                  onChange={(e) => setNewTransaction({ ...newTransaction, merchant_id: e.target.value })}
                  placeholder="1"
                />
              </div>
              <div className="space-y-2">
                <Label>Amount</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                  placeholder="1000.00"
                />
              </div>
              <div className="space-y-2">
                <Label>Currency</Label>
                <select
                  value={newTransaction.currency}
                  onChange={(e) => setNewTransaction({ ...newTransaction, currency: e.target.value })}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="KES">KES</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Status</Label>
                <select
                  value={newTransaction.status}
                  onChange={(e) => setNewTransaction({ ...newTransaction, status: e.target.value })}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
              <Button onClick={addTransaction} className="w-full">
                Add Transaction
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
