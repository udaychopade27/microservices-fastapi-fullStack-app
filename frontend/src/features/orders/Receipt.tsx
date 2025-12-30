import { useParams, Navigate } from 'react-router-dom';
import { apiFetch } from '../../api/client';
import { useEffect, useState } from 'react';

type OrderItem = {
  product_id: number;
  product_name: string;
  qty: number;
  price: number;
  line_total: number;
};

type Order = {
  id: number;
  status: string;
  total: number;
  created_at: string;
  items: OrderItem[];
};

export default function Receipt() {
  const { id } = useParams<{ id: string }>();

  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) {
      setError('Invalid order id');
      setLoading(false);
      return;
    }

    apiFetch<Order>(`/api/orders/by-id/${id}`)
      .then(res => {
        if (!res || !res.id) {
          throw new Error('Order not found');
        }
        setOrder(res);
      })
      .catch(err => setError(err.message || 'Failed to load receipt'))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return <Navigate to="/orders" replace />;
  }

  if (loading) {
    return <p className="text-gray-500">Loading receipt…</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!order) {
    return <p className="text-gray-500">Order not found.</p>;
  }

  const totalItems = order.items.reduce((sum, i) => sum + i.qty, 0);

  return (
    <div className="max-w-2xl mx-auto bg-white border rounded p-6 space-y-6 shadow">
      <h2 className="text-xl font-semibold">Payment Receipt</h2>

      {/* META */}
      <div className="text-sm text-gray-700 space-y-1">
        <p><strong>Order ID:</strong> {order.id}</p>
        <p>
          <strong>Status:</strong>{' '}
          <span className={order.status === 'PAID' ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
            {order.status}
          </span>
        </p>
        <p>
          <strong>Date:</strong>{' '}
          {new Date(order.created_at).toLocaleString()}
        </p>
      </div>

      {/* ITEMS */}
      <table className="w-full border text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Product</th>
            <th className="p-2 text-left">SKU</th>
            <th className="p-2 text-right">Qty</th>
            <th className="p-2 text-right">Unit Price</th>
            <th className="p-2 text-right">Total Price</th>
          </tr>
        </thead>
        <tbody>
          {order.items.map(item => (
            <tr key={item.product_id} className="border-t">
              <td className="p-2">
                {item.product_name || `Product #${item.product_id}`}
              </td>
              <td className="p-2 text-gray-500">
                #{item.product_id}
              </td>
              <td className="p-2 text-right">{item.qty}</td>
              <td className="p-2 text-right">${item.price.toFixed(2)}</td>
              <td className="p-2 text-right font-semibold">
                ${item.line_total.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* SUMMARY */}
      <div className="flex justify-between font-medium">
        <span>Total Items</span>
        <span>{totalItems}</span>
      </div>

      <div className="flex justify-between text-lg font-bold">
        <span>Amount Paid</span>
        <span>${order.total.toFixed(2)}</span>
      </div>

      <div className="pt-4 text-green-700 font-semibold text-center">
        Thank you for your purchase
      </div>
    </div>
  );
}
