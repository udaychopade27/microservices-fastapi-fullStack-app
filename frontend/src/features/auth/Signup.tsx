import { useState } from 'react';
import { apiFetch } from '../../api/client';
import { useAuth } from '../../auth/useAuth';

export default function Signup() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const submit = async () => {
    try {
      const res = await apiFetch<any>('/api/auth/register', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({
          username,
          password,
          role: 'CLIENT', // enforced by frontend
        }),
      });

      // Auto-login after register
      login(res.access_token, {
        id: res.user_id,
        role: res.role,
      });
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-24 space-y-4">
      <h2 className="text-xl font-semibold">Sign Up</h2>

      {error && <p className="text-red-600">{error}</p>}

      <input
        className="input"
        placeholder="Username"
        onChange={e => setUsername(e.target.value)}
      />
      <input
        className="input"
        type="password"
        placeholder="Password"
        onChange={e => setPassword(e.target.value)}
      />

      <button className="btn-primary w-full" onClick={submit}>
        Create Account
      </button>
    </div>
  );
}
