import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import EditorPage from './pages/EditorPage';
import CaptionsPage from './pages/CaptionsPage';
import ExportPage from './pages/ExportPage';
import JobsPage from './pages/JobsPage';

const styles = `
  :root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-card: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --success: #22c55e;
    --error: #ef4444;
    --warning: #f59e0b;
    --border: #475569;
  }

  body {
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
  }

  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.2s;
  }

  .btn-primary { background: var(--accent); color: white; }
  .btn-primary:hover { background: var(--accent-hover); }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-danger { background: var(--error); color: white; }
  .btn-success { background: var(--success); color: white; }
  .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text-primary); }

  .card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
  }

  .input {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    color: var(--text-primary);
    font-size: 14px;
    width: 100%;
  }

  .input:focus { outline: none; border-color: var(--accent); }

  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .badge-pending { background: var(--warning); color: #000; }
  .badge-running { background: var(--accent); color: white; }
  .badge-completed { background: var(--success); color: white; }
  .badge-failed { background: var(--error); color: white; }
  .badge-ready { background: var(--success); color: white; }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: var(--bg-card);
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    background: var(--accent);
    transition: width 0.3s;
    border-radius: 4px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }

  th { color: var(--text-secondary); font-size: 13px; font-weight: 600; text-transform: uppercase; }
`;

export default function App() {
  return (
    <>
      <style>{styles}</style>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/editor/:videoId" element={<EditorPage />} />
          <Route path="/captions/:videoId" element={<CaptionsPage />} />
          <Route path="/export/:clipId" element={<ExportPage />} />
          <Route path="/jobs" element={<JobsPage />} />
        </Routes>
      </Layout>
    </>
  );
}
