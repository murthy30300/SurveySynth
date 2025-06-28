import { useState } from 'react';

function App() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [mode, setMode] = useState('login');
  const [loggedIn, setLoggedIn] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const baseUrl = 'https://mngp6096cl.execute-api.us-east-1.amazonaws.com/Prod';
    const endpoint = mode === 'login'
      ? `${baseUrl}/login`
      : `${baseUrl}/register`;
    const res = await fetch(endpoint, {
      method: 'POST',
      body: JSON.stringify(form),
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    alert(JSON.stringify(data));
    if (mode === 'login' && data.message === 'Login successful') {
      setLoggedIn(true);
      localStorage.setItem("user_id", data.user_id); // 💾 store for file uploads
      localStorage.setItem("email", form.email); // 💾 store email for uploads
    }
  };

  // File upload handler
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = reader.result.split(',')[1];
      const email = localStorage.getItem("email");
      const API_BASE = 'https://mngp6096cl.execute-api.us-east-1.amazonaws.com/Prod';
      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          file: base64,
          filename: file.name
        })
      });
      const result = await response.json();
      alert(result.message || JSON.stringify(result));
      setUploading(false);
    };
    reader.readAsDataURL(file);
  };

  // Simple file upload page
  if (loggedIn) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Upload your file</h2>
        <input type="file" onChange={handleFileUpload} disabled={uploading} />
        {uploading && <p>Uploading...</p>}
      </div>
    );
  }

  return (
    <div style={{ padding: 40 }}>
      <h2>{mode === 'login' ? 'Login' : 'Register'} to SurveySynth</h2>
      <form onSubmit={handleSubmit}>
        <input name="email" placeholder="Email" onChange={handleChange} /><br /><br />
        <input name="password" type="password" placeholder="Password" onChange={handleChange} /><br /><br />
        <button type="submit">{mode === 'login' ? 'Login' : 'Register'}</button>
      </form>
      <p onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? "Don't have an account? Register" : 'Already have an account? Login'}
      </p>
    </div>
  );
}

export default App;