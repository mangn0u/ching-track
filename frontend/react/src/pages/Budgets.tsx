import { useState, useEffect, useCallback } from "react";
import { fetchBudgets, upsertBudget, deleteBudget, fetchBudgetVsActual } from "../api/budgets";
import { fetchCategories } from "../api/transactions";
import type { Budget, BudgetFormData, BudgetVsActual } from "../types/budget";
import type { Category } from "../types/transaction";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const CURRENT_MONTH = new Date().getMonth() + 1;
const CURRENT_YEAR = new Date().getFullYear();

export default function Budgets() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [vsActual, setVsActual] = useState<BudgetVsActual[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterMonth, setFilterMonth] = useState(CURRENT_MONTH);
  const [filterYear, setFilterYear] = useState(CURRENT_YEAR);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Budget | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    Promise.all([
      fetchBudgets(filterMonth, filterYear),
      fetchBudgetVsActual(filterMonth, filterYear),
      fetchCategories("expense"),
    ])
      .then(([budgetList, vs, cats]) => {
        setBudgets(budgetList);
        setVsActual(vs);
        setCategories(cats);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filterMonth, filterYear]);

  useEffect(() => { load(); }, [load]);

  const totalBudget = budgets.reduce((sum, b) => sum + b.limit_amount, 0);
  const totalSpent = vsActual.reduce((sum, b) => sum + b.actual, 0);
  const totalRemaining = Math.max(0, totalBudget - totalSpent);

  function openCreate() {
    setEditing(null);
    setShowModal(true);
  }

  function openEdit(b: Budget) {
    setEditing(b);
    setShowModal(true);
  }

  async function handleSave(data: BudgetFormData) {
    setSaving(true);
    try {
      await upsertBudget(data);
      setShowModal(false);
      setEditing(null);
      load();
    } catch (e) {
      throw e;
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this budget?")) return;
    try {
      await deleteBudget(id);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  return (
    <div className="budgets-page">
      <div className="page-header">
        <h2>Budgets</h2>
        <button className="btn-primary" onClick={openCreate}>+ Add Budget</button>
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="summary-cards">
        <div className="summary-card" style={{ "--card-accent": "var(--blue)" } as React.CSSProperties}>
          <div className="summary-card-title">Total Budget</div>
          <div className="summary-card-value">{formatCurrency(totalBudget)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--red)" } as React.CSSProperties}>
          <div className="summary-card-title">Total Spent</div>
          <div className="summary-card-value">{formatCurrency(totalSpent)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--green)" } as React.CSSProperties}>
          <div className="summary-card-title">Remaining</div>
          <div className="summary-card-value">{formatCurrency(totalRemaining)}</div>
        </div>
      </div>

      <div className="filters-bar">
        <select value={filterMonth} onChange={(e) => setFilterMonth(Number(e.target.value))}>
          {MONTHS.map((m, i) => (
            <option key={i + 1} value={i + 1}>{m}</option>
          ))}
        </select>
        <select value={filterYear} onChange={(e) => setFilterYear(Number(e.target.value))}>
          {Array.from({ length: 5 }, (_, i) => CURRENT_YEAR - i).map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      <div className="card">
        {loading ? (
          <div className="page-loader">Loading...</div>
        ) : budgets.length === 0 ? (
          <p className="empty-state">No budgets set for this period</p>
        ) : (
          <div className="budget-grid">
            {budgets.map((budget) => {
              const vs = vsActual.find((v) => v.category_id === budget.category);
              const pct = vs ? vs.pct_used : 0;
              const spent = vs ? vs.actual : 0;
              const status = vs ? vs.status : "safe";
              return (
                <div key={budget.id} className="budget-card">
                  <div className="budget-card-header">
                    <div className="budget-card-info">
                      <span className="category-dot" style={{ backgroundColor: budget.category_color }} />
                      <span className="budget-card-category">{budget.category_name}</span>
                    </div>
                    <span className={`status-badge status-${status}`}>{status}</span>
                  </div>
                  <div className="budget-bar">
                    <div
                      className="budget-bar-fill"
                      style={{ width: `${Math.min(pct, 100)}%`, background: status === "over" ? "var(--red)" : status === "warning" ? "var(--orange)" : "var(--green)" }}
                    />
                  </div>
                  <div className="budget-card-details">
                    <div className="budget-detail-item">
                      <span className="budget-detail-label">Spent</span>
                      <span className="budget-detail-value">{formatCurrency(spent)}</span>
                    </div>
                    <div className="budget-detail-item">
                      <span className="budget-detail-label">Budget</span>
                      <span className="budget-detail-value">{formatCurrency(budget.limit_amount)}</span>
                    </div>
                  </div>
                  <div className="budget-card-actions">
                    <button className="btn-icon" onClick={() => openEdit(budget)} title="Edit">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(budget.id)} title="Delete">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {showModal && (
        <BudgetModal
          editing={editing}
          categories={categories}
          month={filterMonth}
          year={filterYear}
          saving={saving}
          onSave={handleSave}
          onClose={() => { setShowModal(false); setEditing(null); }}
        />
      )}
    </div>
  );
}

function BudgetModal({ editing, categories, month, year, saving, onSave, onClose }: {
  editing: Budget | null;
  categories: Category[];
  month: number;
  year: number;
  saving: boolean;
  onSave: (data: BudgetFormData) => Promise<void>;
  onClose: () => void;
}) {
  const [category, setCategory] = useState(editing ? String(editing.category) : "");
  const [limitAmount, setLimitAmount] = useState(editing ? String(editing.limit_amount) : "");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!category) {
      setError("Please select a category");
      return;
    }
    if (!limitAmount || Number(limitAmount) <= 0) {
      setError("Limit must be greater than zero");
      return;
    }
    try {
      await onSave({
        category: Number(category),
        month: editing ? editing.month : month,
        year: editing ? editing.year : year,
        limit_amount: Number(limitAmount),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{editing ? "Edit Budget" : "Add Budget"}</h3>
          <button className="btn-icon" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}
          <div className="form-group">
            <label htmlFor="budget-category">Category</label>
            <select id="budget-category" value={category} onChange={(e) => setCategory(e.target.value)} required>
              <option value="">Select category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
              ))}
            </select>
          </div>
          {!editing && (
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="budget-month">Month</label>
                <select id="budget-month" value={month} disabled>
                  {MONTHS.map((m, i) => (
                    <option key={i + 1} value={i + 1}>{m}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="budget-year">Year</label>
                <input id="budget-year" type="number" value={year} disabled />
              </div>
            </div>
          )}
          <div className="form-group">
            <label htmlFor="budget-limit">Limit Amount</label>
            <input id="budget-limit" type="number" step="0.01" min="0" value={limitAmount} onChange={(e) => setLimitAmount(e.target.value)} placeholder="0.00" required />
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

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-KE", { style: "currency", currency: "KES", minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(amount);
}
