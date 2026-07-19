import { Navigate, Route, Routes } from "react-router-dom";
import { auth } from "./lib/api";
import Login from "./pages/Login";
import Projects from "./pages/Projects";

function Protected({ children }: { children: React.ReactNode }) {
  return auth.token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24, maxWidth: 960, margin: "0 auto" }}>
      <h1 style={{ fontSize: 20, marginBottom: 24 }}>P-FMEA · Dr.Indus</h1>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/projects" element={<Protected><Projects /></Protected>} />
        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
    </div>
  );
}
