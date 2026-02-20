import { useEffect, useMemo, useState } from "react";

type Domain = "soft" | "digital";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

function getToken() {
  return localStorage.getItem("access_token") || localStorage.getItem("token") || "";
}

type OptionRow = {
  label: string;
  text: string;
  score: number;
};

export default function AddQuestionModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => Promise<void> | void;
}) {
  const defaultOptions: OptionRow[] = useMemo(
    () => [
      { label: "A", text: "Strongly Agree", score: 5 },
      { label: "B", text: "Agree", score: 4 },
      { label: "C", text: "Neutral", score: 3 },
      { label: "D", text: "Disagree", score: 2 },
      { label: "E", text: "Strongly Disagree", score: 1 },
    ],
    []
  );

  const [domain, setDomain] = useState<Domain>("soft");
  const [category, setCategory] = useState("");
  const [text, setText] = useState("");
  const [displayOrder, setDisplayOrder] = useState<number>(0);
  const [isActive, setIsActive] = useState(true);
  const [options, setOptions] = useState<OptionRow[]>(defaultOptions);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // Reset form each time it opens
  useEffect(() => {
    if (!open) return;
    setError("");
    setDomain("soft");
    setCategory("");
    setText("");
    setDisplayOrder(0);
    setIsActive(true);
    setOptions(defaultOptions);
  }, [open, defaultOptions]);

  // Close on ESC
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const updateOption = (idx: number, patch: Partial<OptionRow>) => {
    setOptions((prev) => prev.map((o, i) => (i === idx ? { ...o, ...patch } : o)));
  };

  const addOption = () => {
    setOptions((prev) => [...prev, { label: "", text: "", score: 3 }]);
  };

  const removeOption = (idx: number) => {
    setOptions((prev) => prev.filter((_, i) => i !== idx));
  };

  const validate = () => {
    if (!text.trim()) return "Question text is required.";
    if (!category.trim()) return "Category is required.";
    if (options.length < 2) return "At least two options are required.";

    const labels = options.map((o) => (o.label || "").trim().toUpperCase()).filter(Boolean);
    const uniqueLabels = new Set(labels);
    if (labels.length !== options.length) return "Each option must have a label (e.g. A, B, C).";
    if (uniqueLabels.size !== labels.length) return "Option labels must be unique.";

    for (const o of options) {
      if (!o.text.trim()) return "Each option must have text (e.g. Agree).";
      if (o.score < 1 || o.score > 5) return "Scores must be between 1 and 5.";
    }
    return "";
  };

  const submit = async () => {
    setError("");
    const v = validate();
    if (v) {
      setError(v);
      return;
    }

    setSaving(true);
    try {
      const payload = {
        text: text.trim(),
        domain,
        category: category.trim(),
        display_order: Number.isFinite(displayOrder) ? displayOrder : 0,
        is_active: isActive,
        options: options.map((o) => ({
          label: o.label.trim().toUpperCase(),
          text: o.text.trim(),
          score: o.score,
        })),
      };

      const res = await fetch(`${API_BASE}/questions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Failed to create question (${res.status})`);
      }

      await onCreated?.();
      onClose();
    } catch (e: any) {
      setError(e?.message || "Failed to create question.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      aria-modal="true"
      role="dialog"
    >
      {/* overlay */}
      <div
        className="absolute inset-0 bg-slate-900/50"
        onClick={onClose}
      />

      {/* modal */}
      <div className="relative w-[95%] max-w-2xl bg-white rounded-2xl shadow-xl border border-slate-200">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Add Question</h2>
            <p className="text-sm text-slate-600">Create a new item in the question bank.</p>
          </div>

          <button
            onClick={onClose}
            className="px-3 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-sm"
          >
            Close
          </button>
        </div>

        <div className="p-5 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-slate-700">Domain</label>
              <select
                className="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 bg-white"
                value={domain}
                onChange={(e) => setDomain(e.target.value as Domain)}
              >
                <option value="soft">soft</option>
                <option value="digital">digital</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-slate-700">Category</label>
              <input
                className="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200"
                placeholder="e.g. communication"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="text-sm text-slate-700">Question text</label>
            <textarea
              className="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 min-h-[90px]"
              placeholder="Type the question..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-slate-700">Display order</label>
              <input
                type="number"
                className="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200"
                value={displayOrder}
                onChange={(e) => setDisplayOrder(parseInt(e.target.value || "0", 10))}
              />
            </div>

            <div className="flex items-end">
              <label className="inline-flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                />
                Active
              </label>
            </div>
          </div>

          <div className="pt-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Options</h3>
              <button
                onClick={addOption}
                className="px-3 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-sm"
                type="button"
              >
                + Add option
              </button>
            </div>

            <div className="mt-3 space-y-2">
              {options.map((op, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-12 gap-2 items-center bg-slate-50 border border-slate-200 rounded-2xl p-3"
                >
                  <div className="col-span-2">
                    <label className="text-xs text-slate-600">Label</label>
                    <input
                      className="mt-1 w-full px-2 py-2 rounded-xl border border-slate-200 bg-white"
                      value={op.label}
                      onChange={(e) => updateOption(idx, { label: e.target.value })}
                      placeholder="A"
                    />
                  </div>

                  <div className="col-span-7">
                    <label className="text-xs text-slate-600">Text</label>
                    <input
                      className="mt-1 w-full px-2 py-2 rounded-xl border border-slate-200 bg-white"
                      value={op.text}
                      onChange={(e) => updateOption(idx, { text: e.target.value })}
                      placeholder="Agree"
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="text-xs text-slate-600">Score</label>
                    <input
                      type="number"
                      min={1}
                      max={5}
                      className="mt-1 w-full px-2 py-2 rounded-xl border border-slate-200 bg-white"
                      value={op.score}
                      onChange={(e) => updateOption(idx, { score: parseInt(e.target.value || "1", 10) })}
                    />
                  </div>

                  <div className="col-span-1 flex justify-end">
                    <button
                      type="button"
                      disabled={options.length <= 2}
                      onClick={() => removeOption(idx)}
                      className="px-2 py-2 rounded-xl border border-slate-200 hover:bg-white text-xs disabled:opacity-40"
                      title={options.length <= 2 ? "Need at least 2 options" : "Remove"}
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="p-5 border-t border-slate-200 flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50"
            disabled={saving}
          >
            Cancel
          </button>

          <button
            onClick={submit}
            className="px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Question"}
          </button>
        </div>
      </div>
    </div>
  );
}
