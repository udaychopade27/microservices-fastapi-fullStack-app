import { useCart } from '../../hooks/useCart';
import { useNavigate } from 'react-router-dom';

export default function Cart() {
  const { items, total, increase, decrease, remove } = useCart();
  const navigate = useNavigate();

  if (!items.length) {
    return <p className="text-gray-500">Your cart is empty.</p>;
  }

  return (
    <div className="max-w-lg space-y-4">
      <h2 className="text-xl font-semibold">Your Cart</h2>

      {items.map(i => (
        <div key={i.id} className="border p-3 rounded flex justify-between">
          <div>
            <div className="font-medium">{i.name}</div>
            <div>${i.price}</div>
            <div className="flex items-center gap-2 mt-2">
              <button onClick={() => decrease(i.id)} className="btn">−</button>
              <span>{i.quantity}</span>
              <button onClick={() => increase(i.id)} className="btn">+</button>
              <button
                onClick={() => remove(i.id)}
                className="text-red-600 ml-4"
              >
                Remove
              </button>
            </div>
          </div>
          <div className="font-semibold">
            ${(i.price * i.quantity).toFixed(2)}
          </div>
        </div>
      ))}

      <div className="flex justify-between text-lg font-semibold">
        <span>Total</span>
        <span>${total.toFixed(2)}</span>
      </div>

      <button
        onClick={() => navigate('/checkout')}
        className="btn-primary w-full"
      >
        Checkout
      </button>
    </div>
  );
}
