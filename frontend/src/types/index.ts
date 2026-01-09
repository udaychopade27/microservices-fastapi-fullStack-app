export type Role = 'CLIENT' | 'OWNER';

export type User = {
  id: string;
  username?: string;
  role: Role;
};

export type Product = {
  id: number;
  name: string;
  price: number;
  stock: number;
};

/* ================= CART ================= */

export type CartItem = {
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  line_total: number;
};

/* ================= ORDERS ================= */

export type OrderItem = {
  product_id: number;
  product_name: string;
  qty: number;
  price: number;
  line_total: number;
};

export type OrderStatus = 'PENDING' | 'PAID' | 'FAILED' | 'REFUNDED';

export type Order = {
  id: number;
  user_id: string;
  status: OrderStatus;
  total: number;
  created_at: string;
  items?: OrderItem[]; // present in receipt
};

/* ================= METRICS ================= */

export type RevenueMetrics = {
  total_revenue: number;
  refunded_amount: number;
  net_revenue: number;
  paid_orders: number;
};
