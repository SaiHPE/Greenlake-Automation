import React from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, Database, PlayCircle, ShieldCheck } from 'lucide-react';
import './styles.css';

function App() {
  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <h1>Alletra Onboard</h1>
          <p>Jump-box automation console for GreenLake and DSCC onboarding.</p>
        </div>
        <button><PlayCircle size={18} /> New run</button>
      </section>
      <section className="grid">
        <Panel icon={<ShieldCheck />} title="Preflight" value="Ready" />
        <Panel icon={<Activity />} title="Active runs" value="0" />
        <Panel icon={<Database />} title="State store" value="SQLite WAL" />
      </section>
      <section className="run-panel">
        <h2>Run timeline</h2>
        <div className="empty">Import arrays or create a run from the CLI to start.</div>
      </section>
    </main>
  );
}

function Panel({ icon, title, value }: { icon: React.ReactNode; title: string; value: string }) {
  return <article className="panel"><div className="icon">{icon}</div><span>{title}</span><strong>{value}</strong></article>;
}

createRoot(document.getElementById('root')!).render(<App />);
