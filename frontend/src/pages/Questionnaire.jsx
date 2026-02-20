import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AddQuestionModal from "../components/AddQuestionModal";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

function getToken() {
  return localStorage.getItem("access_token") || localStorage.getItem("token") || "";
}

export default function Questionnaire() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openAdd, setOpenAdd] = useState(false);

  const [error, setError] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);

  const loadQuestions = async () => {
    setError("");
    setLoading(true);

    try {
      const url = `${API_BASE}/questions?active_only=${activeOnly ? "true" : "false"}`;

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });

      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Failed to load questions (${res.status})`);
      }

      const data = await res.json();
      setItems(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e?.message || "Failed to load questions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuestions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeOnly]);

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      {/* Header Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex items-start justify-between gap-4">
        <div className="space-y-2">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-3 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-sm"
          >
            ← Back to Home
          </Link>

          <div>
            <h1 className="text-2xl font-semibold">Question Bank</h1>
            <p className="text-slate-600">Editable questions that drive self-assessments.</p>
          </div>

          <label className="inline-flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(e) => setActiveOnly(e.target.checked)}
            />
            Show active only
          </label>
        </div>

        <button
          className="px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800"
          onClick={() => setOpenAdd(true)}
        >
          + Add Question
        </button>
      </div>

      {/* Errors */}
      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700">
          {error}
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="text-slate-600">Loading questions...</div>
      ) : items.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 text-slate-600">
          No questions found.
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((q) => (
            <div
              key={q.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-sm transition"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="text-sm text-slate-500">
                  <span className="capitalize">{q.domain}</span> ·{" "}
                  <span className="capitalize">{q.category}</span>
                </div>

                {q.is_active === false && (
                  <span className="text-xs px-2 py-1 rounded-full bg-slate-100 border border-slate-200">
                    inactive
                  </span>
                )}
              </div>

              <div className="mt-2 text-base font-semibold text-slate-900">{q.text}</div>

              <div className="mt-3 text-sm text-slate-700 flex flex-wrap gap-2">
                {(q.options || []).map((op) => (
                  <span
                    key={op.id}
                    className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200"
                  >
                    {String(op.label).toUpperCase()} : {op.score}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <AddQuestionModal
        open={openAdd}
        onClose={() => setOpenAdd(false)}
        onCreated={loadQuestions}
      />
    </div>
  );
}
