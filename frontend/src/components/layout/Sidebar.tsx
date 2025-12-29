import { NavLink } from 'react-router-dom';
import { useAuth } from '../../auth/useAuth';

export default function Sidebar() {
  const { user } = useAuth();
  const link =
    'block px-3 py-2 rounded hover:bg-gray-100';

  return (
    <aside className="w-64 border-r p-4 space-y-2">
      {/* CLIENT */}
      <NavLink to="/products" className={link}>
        Products
      </NavLink>
      <NavLink to="/cart" className={link}>
        Cart
      </NavLink>
      <NavLink to="/orders" className={link}>
        My Orders
      </NavLink>

      {/* OWNER */}
      {user?.role === 'OWNER' && (
        <>
          <hr />
          <NavLink to="/inventory" className={link}>
            Inventory
          </NavLink>
          <NavLink to="/all-orders" className={link}>
            All Orders
          </NavLink>
        </>
      )}
    </aside>
  );
}
