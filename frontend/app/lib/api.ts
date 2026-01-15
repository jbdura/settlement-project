const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export interface QueryResult {
  success: boolean;
  message: string;
  data?: any[];
  row_count?: number;
  affected_rows?: number;
  inserted_id?: number;
}

export interface TableSchema {
  success: boolean;
  message: string;
  data?: {
    columns: {
      [key: string]: {
        type: string;
        nullable: boolean;
        unique: boolean;
        primary_key: boolean;
        size?: number;
      };
    };
  };
}

export const api = {
  // Execute SQL query
  async executeQuery(sql: string): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sql }),
    });
    return response.json();
  },

  // Get all tables
  async getTables(): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/tables`);
    return response.json();
  },

  // Get table schema
  async getTableSchema(tableName: string): Promise<TableSchema> {
    const response = await fetch(`${API_BASE_URL}/tables/${tableName}`);
    return response.json();
  },

  // Get table rows
  async getTableRows(
    tableName: string,
    conditions?: Record<string, any>
  ): Promise<QueryResult> {
    const params = conditions ? new URLSearchParams(conditions).toString() : "";
    const url = `${API_BASE_URL}/tables/${tableName}/rows${params ? `?${params}` : ""}`;
    const response = await fetch(url);
    return response.json();
  },

  // Insert row
  async insertRow(
    tableName: string,
    data: Record<string, any>
  ): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/tables/${tableName}/rows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  // Update rows
  async updateRows(
    tableName: string,
    conditions: Record<string, any>,
    updates: Record<string, any>
  ): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/tables/${tableName}/rows`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ conditions, updates }),
    });
    return response.json();
  },

  // Delete rows
  async deleteRows(
    tableName: string,
    conditions: Record<string, any>
  ): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/tables/${tableName}/rows`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ conditions }),
    });
    return response.json();
  },

  // Execute JOIN
  async executeJoin(params: {
    left_table: string;
    right_table: string;
    left_key: string;
    right_key: string;
    columns?: string[];
    conditions?: Record<string, any>;
  }): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/join`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    });
    return response.json();
  },

  // Get merchant report
  async getMerchantReport(): Promise<QueryResult> {
    const response = await fetch(`${API_BASE_URL}/merchants/report`);
    return response.json();
  },

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },
};
