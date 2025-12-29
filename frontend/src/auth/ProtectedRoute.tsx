import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';

export default function ProtectedRoute({
  children,
  role,
}: {
  children: JSX.Element;
  role?: 'CLIENT' | 'OWNER';
}) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // OWNER landing redirect
  if (user.role === 'OWNER' && location.pathname === '/') {
    return <Navigate to="/inventory" replace />;
  }

  if (role && user.role !== role) {
    return <Navigate to="/" replace />;
  }

  return children;
}
