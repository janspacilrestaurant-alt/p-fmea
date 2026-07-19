import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export default function Login() {
  const [email, setEmail] = useState("admin@drindus.local");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.login(email, password);
      navigate("/projects");
    } catch {
      setError("Přihlášení se nezdařilo.");
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ display: "grid", gap: 12, maxWidth: 320 }}>
      <h2 style={{ fontSize: 16 }}>Přihlášení</h2>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="E-mail" />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Heslo"
      />
      {error && <span style={{ color: "crimson" }}>{error}</span>}
      <button type="submit">Přihlásit</button>
    </form>
  );
}
