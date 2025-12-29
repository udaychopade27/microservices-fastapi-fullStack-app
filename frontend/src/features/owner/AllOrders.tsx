import { useEffect, useState } from 'react';
import { apiFetch } from '../../api/client';
import { Order } from '../../types';
import { useNavigate } from 'react-router-dom';

export default function AllOrders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    apiFetch<Order[]>(`/orders/all`)
      .then(setOrders)
      .catch(err => setError(err.message || 'Failed to load orders'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Loading orders…</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  const revenue = orders
    .filter(o => o.status === 'PAID')
    .reduce((sum, o) => sum + o.total, 0);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">
        Total Revenue: ${revenue.toFixed(2)}
      </h2>

      <div className="space-y-2">
        {orders.map(o => (
          <div
            key={o.id}
            onClick={() => navigate(`/receipt/${o.id}`)}
            className="border rounded p-3 flex justify-between cursor-pointer hover:bg-gray-50"
          >
            <div>
              <div className="font-medium">Order #{o.id}</div>
              <div className="text-sm text-gray-600">
                {new Date(o.created_at).toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">
                User: {o.user_id}
              </div>
            </div>

            <div className="text-right">
              <div className="font-semibold">${o.total}</div>
              <div
                className={`text-sm ${
                  o.status === 'PAID' ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {o.status}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
