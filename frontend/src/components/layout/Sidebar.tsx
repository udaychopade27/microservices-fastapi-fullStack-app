import { NavLink } from 'react-router-dom';
import { useAuth } from '../../auth/useAuth';

export default function Sidebar() {
  const { user } = useAuth();

  const link =
    'block px-3 py-2 rounded hover:bg-gray-100 transition';

  const active =
    'font-semibold bg-gray-100';

  return (
    <aside className="w-64 border-r p-4 space-y-4 bg-white">
      {/* CLIENT */}
      <div>
        <p className="text-xs text-gray-500 mb-2 uppercase">Client</p>

        <NavLink to="/products" className={({ isActive }) => `${link} ${isActive ? active : ''}`}>
          Products
        </NavLink>

        <NavLink to="/cart" className={({ isActive }) => `${link} ${isActive ? active : ''}`}>
          Cart
        </NavLink>

        <NavLink to="/orders" className={({ isActive }) => `${link} ${isActive ? active : ''}`}>
          My Orders
        </NavLink>
      </div>

      {/* OWNER */}
      {user?.role === 'OWNER' && (
        <div>
          <p className="text-xs text-gray-500 mb-2 uppercase">Owner</p>

          <NavLink to="/inventory" className={({ isActive }) => `${link} ${isActive ? active : ''}`}>
            Inventory
          </NavLink>

          <NavLink to="/all-orders" className={({ isActive }) => `${link} ${isActive ? active : ''}`}>
            Orders & Revenue
          </NavLink>
        </div>
      )}
    </aside>
  );
}
