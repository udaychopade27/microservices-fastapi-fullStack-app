import { useParams, Navigate, useNavigate } from 'react-router-dom';
import { apiFetch } from '../../api/client';
import { useEffect, useState } from 'react';
import { useAuth } from '../../auth/useAuth';

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
  const navigate = useNavigate();
  const { user } = useAuth(); // ✅ FIXED: hook inside component

  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [showReturn, setShowReturn] = useState(false);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (!id) {
      setError('Invalid order id');
      setLoading(false);
      return;
    }

    apiFetch<Order>(`/api/orders/by-id/${id}`)
      .then(setOrder)
      .catch(err => setError(err.message || 'Failed to load receipt'))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) return <Navigate to="/orders" replace />;
  if (loading) return <p className="text-gray-500">Loading receipt…</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!order) return <p className="text-gray-500">Order not found.</p>;

  const totalItems = order.items.reduce((s, i) => s + i.qty, 0);

  const handleFullReturn = async () => {
    setProcessing(true);
    try {
      await apiFetch(`/api/orders/refund/${order.id}`, {
        method: 'POST'
      });

      alert('Order refunded successfully');
      navigate('/orders');
    } catch (e: any) {
      alert(e.message || 'Refund failed');
    } finally {
      setProcessing(false);
      setShowReturn(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white border rounded p-6 space-y-6 shadow">
      <h2 className="text-xl font-semibold">Payment Receipt</h2>

      <div className="text-sm text-gray-700 space-y-1">
        <p><strong>Order ID:</strong> {order.id}</p>
        <p>
          <strong>Status:</strong>{' '}
          <span className={order.status === 'PAID'
            ? 'text-green-600 font-semibold'
            : 'text-red-600 font-semibold'}>
            {order.status}
          </span>
        </p>
        <p><strong>Date:</strong> {new Date(order.created_at).toLocaleString()}</p>
      </div>

      <table className="w-full border text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Product</th>
            <th className="p-2 text-left">SKU</th>
            <th className="p-2 text-right">Qty</th>
            <th className="p-2 text-right">Unit Price</th>
            <th className="p-2 text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          {order.items.map(i => (
            <tr key={i.product_id} className="border-t">
              <td className="p-2">{i.product_name}</td>
              <td className="p-2 text-gray-500">#{i.product_id}</td>
              <td className="p-2 text-right">{i.qty}</td>
              <td className="p-2 text-right">${i.price.toFixed(2)}</td>
              <td className="p-2 text-right font-semibold">
                ${i.line_total.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex justify-between font-medium">
        <span>Total Items</span>
        <span>{totalItems}</span>
      </div>

      <div className="flex justify-between text-lg font-bold">
        <span>Amount Paid</span>
        <span>${order.total.toFixed(2)}</span>
      </div>

      {/* CLIENT ONLY */}
      {user?.role === 'CLIENT' && order.status === 'PAID' && (
        <button
          onClick={() => setShowReturn(true)}
          className="btn-danger w-full"
        >
          Return Order
        </button>
      )}

      {showReturn && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
          <div className="bg-white p-6 rounded w-96 space-y-4">
            <h3 className="font-semibold text-lg">
              Return Order #{order.id}
            </h3>

            <p className="text-sm text-gray-600">
              This will refund the full order and restore inventory.
            </p>

            <div className="flex justify-end gap-2">
              <button
                className="btn-secondary"
                onClick={() => setShowReturn(false)}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                disabled={processing}
                onClick={handleFullReturn}
              >
                {processing ? 'Processing…' : 'Confirm Return'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="pt-4 text-green-700 font-semibold text-center">
        Thank you for your purchase
      </div>
    </div>
  );
}
