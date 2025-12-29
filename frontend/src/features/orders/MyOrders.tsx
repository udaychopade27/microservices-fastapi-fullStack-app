import { useEffect, useState } from 'react';
import { apiFetch } from '../../api/client';
import { useAuth } from '../../auth/useAuth';
import { useNavigate } from 'react-router-dom';

type Order = {
  id: number;
  status: string;
  total: number;
  created_at: string;
};

export default function MyOrders() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) return;

    apiFetch<Order[]>(`/orders/${user.id}`)
      .then(setOrders)
      .catch(err => setError(err.message || 'Failed to load orders'))
      .finally(() => setLoading(false));
  }, [user]);

  if (loading) return <p className="text-gray-500">Loading orders…</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!orders.length) return <p>No orders yet.</p>;

  return (
    <div className="space-y-4">
      {orders.map(o => (
        <div
          key={o.id}
          onClick={() => navigate(`/receipt/${o.id}`)}
          className="border rounded p-4 bg-white cursor-pointer hover:bg-gray-50 transition"
        >
          <div className="flex justify-between">
            <div>
              <p className="font-medium">Order #{o.id}</p>
              <p className="text-sm text-gray-600">
                {new Date(o.created_at).toLocaleString()}
              </p>
            </div>

            <div className="text-right">
              <p className="font-semibold">${o.total}</p>
              <p
                className={`text-sm ${
                  o.status === 'PAID'
                    ? 'text-green-600'
                    : 'text-red-600'
                }`}
              >
                {o.status}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
