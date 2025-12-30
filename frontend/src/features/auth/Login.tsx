import { useState } from 'react';
import { apiFetch } from '../../api/client';
import { useAuth } from '../../auth/useAuth';
import { Link } from 'react-router-dom';

export default function Login() {
  const { login } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setError('');
    setLoading(true);

    try {
      const res = await apiFetch<{
        access_token: string;
        user_id: string;
        role: 'CLIENT' | 'OWNER';
      }>('/api/auth/login', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({ username, password }),
      });

      // ✅ THIS triggers redirect in AuthContext
      login(res.access_token, {
        id: res.user_id,
        role: res.role,
      });
    } catch (e: any) {
      setError(e.message || 'Login failed');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-24 space-y-4">
      <h2 className="text-xl font-semibold">Login</h2>

      {error && <p className="text-red-600">{error}</p>}

      <input
        className="input"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />

      <input
        className="input"
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />

      <button
        className="btn-primary w-full"
        onClick={submit}
        disabled={loading}
      >
        {loading ? 'Logging in…' : 'Login'}
      </button>

      <p className="text-sm text-center">
        Don’t have an account?{' '}
        <Link to="/signup" className="text-blue-600 underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
