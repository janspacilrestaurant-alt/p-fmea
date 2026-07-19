import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, type Project } from "../lib/api";

export default function Projects() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const { data, isLoading, error } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: api.listProjects,
  });
  const create = useMutation({
    mutationFn: () => api.createProject({ name }),
    onSuccess: () => {
      setName("");
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  if (isLoading) return <p>Načítám…</p>;
  if (error) return <p style={{ color: "crimson" }}>Chyba načtení projektů.</p>;

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", gap: 8 }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Název projektu" />
        <button disabled={!name || create.isPending} onClick={() => create.mutate()}>
          Nový projekt
        </button>
      </div>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={th}>Název</th>
            <th style={th}>Zákazník</th>
            <th style={th}>FMEA č.</th>
            <th style={th}>Revize</th>
          </tr>
        </thead>
        <tbody>
          {data?.map((p) => (
            <tr key={p.id}>
              <td style={td}>{p.name}</td>
              <td style={td}>{p.customer || "—"}</td>
              <td style={td}>{p.fmea_number || "—"}</td>
              <td style={td}>{p.revision}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

const th: React.CSSProperties = { textAlign: "left", borderBottom: "2px solid #ddd", padding: 8 };
const td: React.CSSProperties = { borderBottom: "1px solid #eee", padding: 8 };
