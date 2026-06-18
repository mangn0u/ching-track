import { useState, useEffect, useCallback } from "react";
import { fetchGoals, createGoal, updateGoal, deleteGoal, contributeToGoal, fetchContributions } from "../api/goals";
import { EditIcon, DeleteIcon, CloseIcon, HistoryIcon } from "../components/Icons";
import { formatCurrency } from "../utils/format";
import type { Goal, GoalFormData, GoalContribution, ContributionFormData } from "../types/goal";

export default function Goals() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Goal | null>(null);
  const [saving, setSaving] = useState(false);
  const [contributingSaving, setContributingSaving] = useState(false);
  const [contributingId, setContributingId] = useState<number | null>(null);
  const [viewingContributions, setViewingContributions] = useState<Goal | null>(null);
  const [contributions, setContributions] = useState<GoalContribution[]>([]);
  const [loadingContributions, setLoadingContributions] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    fetchGoals()
      .then(setGoals)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalTarget = goals.reduce((s, g) => s + g.target_amount, 0);
  const totalSaved = goals.reduce((s, g) => s + g.total_saved, 0);
  const onTrackCount = goals.filter((g) => g.is_on_track).length;

  function openCreate() {
    setEditing(null);
    setShowModal(true);
  }

  function openEdit(g: Goal) {
    setEditing(g);
    setShowModal(true);
  }

  async function handleSave(data: GoalFormData) {
    setSaving(true);
    try {
      if (editing) {
        await updateGoal(editing.id, data);
      } else {
        await createGoal(data);
      }
      setShowModal(false);
      setEditing(null);
      load();
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this savings goal?")) return;
    try {
      await deleteGoal(id);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  async function handleContribute(goalId: number, data: ContributionFormData) {
    setContributingSaving(true);
    try {
      await contributeToGoal(goalId, data);
      setContributingId(null);
      load();
    } finally {
      setContributingSaving(false);
    }
  }

  async function openContributions(g: Goal) {
    setViewingContributions(g);
    setLoadingContributions(true);
    try {
      const data = await fetchContributions(g.id);
      setContributions(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load contributions");
    } finally {
      setLoadingContributions(false);
    }
  }

  return (
    <div className="goals-page">
      <div className="page-header">
        <h2>Savings Goals</h2>
        <button className="btn-primary" onClick={openCreate}>+ Add Goal</button>
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="summary-cards">
        <div className="summary-card" style={{ "--card-accent": "var(--purple)" } as React.CSSProperties}>
          <div className="summary-card-title">Total Target</div>
          <div className="summary-card-value">{formatCurrency(totalTarget)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--green)" } as React.CSSProperties}>
          <div className="summary-card-title">Total Saved</div>
          <div className="summary-card-value">{formatCurrency(totalSaved)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--blue)" } as React.CSSProperties}>
          <div className="summary-card-title">On Track</div>
          <div className="summary-card-value">{onTrackCount}/{goals.length}</div>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div className="page-loader">Loading...</div>
        ) : goals.length === 0 ? (
          <p className="empty-state">No savings goals yet</p>
        ) : (
          <div className="goal-grid">
            {goals.map((goal) => (
              <div key={goal.id} className="goal-card">
                <div className="goal-card-header">
                  <span className="goal-card-name">{goal.name}</span>
                  <span className={`status-badge ${goal.is_on_track ? "status-safe" : "status-over"}`}>
                    {goal.is_on_track ? "On Track" : "Behind"}
                  </span>
                </div>
                {goal.description && <p className="goal-card-desc">{goal.description}</p>}
                <div className="goal-card-progress">
                  <div className="goal-bar">
                    <div className="goal-bar-fill" style={{ width: `${Math.min(goal.progress_pct, 100)}%` }} />
                  </div>
                  <div className="goal-labels">
                    <span>{formatCurrency(goal.total_saved)}</span>
                    <span>{formatCurrency(goal.target_amount)}</span>
                  </div>
                </div>
                <div className="goal-card-stats">
                  <div className="goal-stat">
                    <span className="goal-stat-value">{goal.progress_pct.toFixed(0)}%</span>
                    <span className="goal-stat-label">Complete</span>
                  </div>
                  <div className="goal-stat">
                    <span className="goal-stat-value">{goal.days_remaining !== null ? `${goal.days_remaining}d` : "—"}</span>
                    <span className="goal-stat-label">Left</span>
                  </div>
                  <div className="goal-stat">
                    <span className="goal-stat-value">{goal.monthly_required !== null ? formatCurrency(goal.monthly_required) : "—"}</span>
                    <span className="goal-stat-label">/mo needed</span>
                  </div>
                </div>
                <div className="goal-card-actions">
                  <button className="btn-primary btn-sm" onClick={() => setContributingId(goal.id)}>+ Contribute</button>
                  <div className="goal-card-icon-actions">
                    <button className="btn-icon" onClick={() => openContributions(goal)} title="View History">
                      <HistoryIcon />
                    </button>
                    <button className="btn-icon" onClick={() => openEdit(goal)} title="Edit">
                      <EditIcon />
                    </button>
                    <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(goal.id)} title="Delete">
                      <DeleteIcon />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <GoalModal
          editing={editing}
          saving={saving}
          onSave={handleSave}
          onClose={() => { setShowModal(false); setEditing(null); }}
        />
      )}

      {contributingId !== null && (() => {
        const goal = goals.find((g) => g.id === contributingId);
        if (!goal) return null;
        return (
          <ContributeModal
            goal={goal}
            saving={contributingSaving}
            onSave={(data) => handleContribute(contributingId, data)}
            onClose={() => setContributingId(null)}
          />
        );
      })()}

      {viewingContributions && (
        <ContributionsModal
          goal={viewingContributions}
          contributions={contributions}
          loading={loadingContributions}
          onClose={() => { setViewingContributions(null); setContributions([]); }}
        />
      )}
    </div>
  );
}

function GoalModal({ editing, saving, onSave, onClose }: {
  editing: Goal | null;
  saving: boolean;
  onSave: (data: GoalFormData) => Promise<void>;
  onClose: () => void;
}) {
  const [name, setName] = useState(editing?.name || "");
  const [description, setDescription] = useState(editing?.description || "");
  const [targetAmount, setTargetAmount] = useState(editing ? String(editing.target_amount) : "");
  const [deadline, setDeadline] = useState(editing?.deadline || "");
  const [currencyCode, setCurrencyCode] = useState(editing?.currency_code || "KES");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!name.trim()) {
      setError("Goal name is required");
      return;
    }
    if (!targetAmount || Number(targetAmount) <= 0) {
      setError("Target amount must be greater than zero");
      return;
    }
    try {
      await onSave({
        name: name.trim(),
        description: description.trim(),
        target_amount: Number(targetAmount),
        currency_code: currencyCode,
        deadline: deadline || null,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{editing ? "Edit Goal" : "Add Savings Goal"}</h3>
          <button className="btn-icon" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}
          <div className="form-group">
            <label htmlFor="goal-name">Goal Name</label>
            <input id="goal-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Emergency Fund" required />
          </div>
          <div className="form-group">
            <label htmlFor="goal-desc">Description</label>
            <input id="goal-desc" type="text" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional description" />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="goal-target">Target Amount</label>
              <input id="goal-target" type="number" step="0.01" min="0" value={targetAmount} onChange={(e) => setTargetAmount(e.target.value)} placeholder="0.00" required />
            </div>
            <div className="form-group">
              <label htmlFor="goal-currency">Currency</label>
              <input id="goal-currency" type="text" maxLength={3} value={currencyCode} onChange={(e) => setCurrencyCode(e.target.value.toUpperCase())} placeholder="KES" />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="goal-deadline">Deadline (optional)</label>
            <input id="goal-deadline" type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : editing ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ContributeModal({ goal, saving, onSave, onClose }: {
  goal: Goal;
  saving: boolean;
  onSave: (data: ContributionFormData) => Promise<void>;
  onClose: () => void;
}) {
  const today = new Date().toISOString().split("T")[0];
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState(today);
  const [note, setNote] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!amount || Number(amount) <= 0) {
      setError("Amount must be greater than zero");
      return;
    }
    try {
      await onSave({
        amount: Number(amount),
        date,
        note: note.trim(),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Contribute to "{goal.name}"</h3>
          <button className="btn-icon" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cont-amount">Amount</label>
              <input id="cont-amount" type="number" step="0.01" min="0" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" required />
            </div>
            <div className="form-group">
              <label htmlFor="cont-date">Date</label>
              <input id="cont-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="cont-note">Note</label>
            <input id="cont-note" type="text" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note" />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : "Contribute"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ContributionsModal({ goal, contributions, loading, onClose }: {
  goal: Goal;
  contributions: GoalContribution[];
  loading: boolean;
  onClose: () => void;
}) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Contributions — {goal.name}</h3>
          <button className="btn-icon" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <div className="modal-form">
          {loading ? (
            <p className="empty-state">Loading contributions...</p>
          ) : contributions.length === 0 ? (
            <p className="empty-state">No contributions yet</p>
          ) : (
            <div className="contribution-list">
              <div className="contribution-header">
                <span>Date</span>
                <span>Amount</span>
                <span>Note</span>
              </div>
              {contributions.map((c) => (
                <div key={c.id} className="contribution-row">
                  <span className="contribution-date">{c.date}</span>
                  <span className="contribution-amount">{formatCurrency(c.amount)}</span>
                  <span className="contribution-note">{c.note || "—"}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


