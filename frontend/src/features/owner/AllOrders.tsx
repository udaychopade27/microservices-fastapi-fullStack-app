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
    apiFetch<Order[]>('/api/orders/all')
      .then(setOrders)
      .catch(err => setError(err.message || 'Failed to load orders'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Loading orders…</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  const totalRevenue = orders
    .filter(o => o.status === 'PAID')
    .reduce((sum, o) => sum + o.total, 0);

  const refundedAmount = orders
    .filter(o => o.status === 'REFUNDED')
    .reduce((sum, o) => sum + o.total, 0);

  const netRevenue = totalRevenue - refundedAmount;

  const stats = {
    paid: orders.filter(o => o.status === 'PAID').length,
    refunded: orders.filter(o => o.status === 'REFUNDED').length,
    failed: orders.filter(o => o.status === 'FAILED').length,
  };

  return (
    <div className="space-y-6">
      {/* ================= METRICS ================= */}
      <div className="grid grid-cols-4 gap-4">
        <Metric label="Total Revenue" value={`$${totalRevenue.toFixed(2)}`} />
        <Metric label="Refunded" value={`$${refundedAmount.toFixed(2)}`} />
        <Metric label="Net Revenue" value={`$${netRevenue.toFixed(2)}`} />
        <Metric label="Paid Orders" value={stats.paid} />
      </div>

      {/* ================= INVENTORY HEALTH ================= */}
      <div className="border rounded p-4 bg-yellow-50 text-sm">
        <strong>Inventory Health:</strong>{' '}
        <span className="text-gray-700">
          Monitoring enabled. Low-stock alerts ready to connect.
        </span>
      </div>

      {/* ================= ORDERS ================= */}
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
                  o.status === 'PAID'
                    ? 'text-green-600'
                    : o.status === 'REFUNDED'
                    ? 'text-gray-500'
                    : 'text-red-600'
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

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border rounded p-4 bg-white">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-xl font-semibold">{value}</div>
    </div>
  );
}
