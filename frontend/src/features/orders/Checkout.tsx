import { useState } from 'react';
import { useCart } from '../../hooks/useCart';
import { useAuth } from '../../auth/useAuth';
import { apiFetch } from '../../api/client';
import { useNavigate } from 'react-router-dom';

export default function Checkout() {
  const { items, total, clear } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const checkout = async () => {
    if (!user || items.length === 0 || loading) return;

    setLoading(true);
    setError('');

    try {
      const payload = {
        user_id: user.id,
        items: items.map(i => ({
          product_id: Number(i.id),
          qty: i.quantity
        }))
      };

      const res = await apiFetch<{
        order_id: number;
        status: string;
        total: number;
      }>('/orders/checkout', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      // ❌ Payment failed → do NOT clear cart
      if (!res || res.status !== 'PAID') {
        throw new Error('Payment failed. No money was charged.');
      }

      // ✅ Payment success → clear cart first
      clear();

      // Then navigate
      navigate(`/receipt/${res.order_id}`);
    } catch (err: any) {
      setError(err.message || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  if (!items.length) {
    return <p className="text-gray-500">Your cart is empty.</p>;
  }

  return (
    <div className="max-w-lg space-y-4">
      <h2 className="text-xl font-semibold">Checkout</h2>

      <div className="border rounded p-4 space-y-2">
        {items.map(i => (
          <div key={i.id} className="flex justify-between">
            <span>{i.name} × {i.quantity}</span>
            <span>${(i.price * i.quantity).toFixed(2)}</span>
          </div>
        ))}
      </div>

      <div className="flex justify-between font-semibold text-lg">
        <span>Total</span>
        <span>${total.toFixed(2)}</span>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded">
          {error}
        </div>
      )}

      <button
        onClick={checkout}
        disabled={loading}
        className={`btn-primary w-full ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {loading ? 'Processing Payment…' : `Pay $${total.toFixed(2)}`}
      </button>
    </div>
  );
}
