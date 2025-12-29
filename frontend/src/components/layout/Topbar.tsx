import { useAuth } from '../../auth/useAuth';
import { useCart } from '../../hooks/useCart';

export default function Topbar() {
  const { user, logout } = useAuth();
  const { count } = useCart();

  return (
    <header className="flex justify-between px-6 py-3 border-b bg-white">
      <h1 className="font-bold">MicroStore</h1>

      <div className="flex items-center gap-4">
        <span>{user?.role}</span>
        <span>🛒 {count}</span>
        <button onClick={logout} className="text-red-600">
          Logout
        </button>
      </div>
    </header>
  );
}
