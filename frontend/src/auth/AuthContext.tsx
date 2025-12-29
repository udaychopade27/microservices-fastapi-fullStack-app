import { createContext, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export type User = {
  id: string;
  role: 'CLIENT' | 'OWNER';
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('token')
  );

  const login = (token: string, user: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));

    setToken(token);
    setUser(user);

    // ✅ ROLE-BASED REDIRECT (CRITICAL FIX)
    if (user.role === 'OWNER') {
      navigate('/inventory', { replace: true });
    } else {
      navigate('/products', { replace: true });
    }
  };

  const logout = () => {
    localStorage.removeItem('cart'); // ✅ CLEAR CART
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    setUser(null);
    setToken(null);

    navigate('/login', { replace: true });
  };


  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
