export type Role = 'CLIENT' | 'OWNER';

export type User = {
  id: string;
  username?: string;
  role: Role;
};

export type Product = {
  id: string;
  name: string;
  price: number;
  stock: number;
};

export type CartItem = {
  product: Product;
  quantity: number;
};

export type OrderItem = {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
};

export type Order = {
  id: number;
  user_id: string;
  status: string;
  total: number;
  created_at: string;
};


