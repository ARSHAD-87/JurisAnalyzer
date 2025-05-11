import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './auth.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
  
    const response = await fetch('/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });
  
    const result = await response.json();
    if (response.ok) {
      alert(result.message);
  
      // Store token based on "Remember Me" state
      if (rememberMe) {
        localStorage.setItem('userToken', result.token || 'true'); // Persistent storage
      } else {
        sessionStorage.setItem('userToken', result.token || 'true'); // Temporary storage
      }
  
      navigate('/');
    } else {
      alert(result.error);
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <label>
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          Remember Me
        </label>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginPage;
