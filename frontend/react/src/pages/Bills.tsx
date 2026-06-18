import { useState, useEffect, useCallback } from "react";
import { fetchBills, createBill, updateBill, deleteBill, payBill } from "../api/bills";
import { EditIcon, DeleteIcon, CloseIcon } from "../components/Icons";
import { formatCurrency } from "../utils/format";
import type { Bill, BillFormData } from "../types/bill";

export default function Bills() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"active" | "inactive">("active");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Bill | null>(null);
  const [saving, setSaving] = useState(false);
  const [payingId, setPayingId] = useState<number | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    fetchBills(filter === "active")
      .then(setBills)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const totalMonthly = bills
    .filter((b) => b.frequency === "monthly")
    .reduce((s, b) => s + b.amount, 0);
  const paidCount = bills.filter((b) => b.is_paid_this_period).length;
  const upcomingCount = bills.filter((b) => !b.is_paid_this_period).length;

  function openCreate() {
    setEditing(null);
    setShowModal(true);
  }

  function openEdit(b: Bill) {
    setEditing(b);
    setShowModal(true);
  }

  async function handleSave(data: BillFormData) {
    setSaving(true);
    try {
      if (editing) {
        await updateBill(editing.id, data);
      } else {
        await createBill(data);
      }
      setShowModal(false);
      setEditing(null);
      load();
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Deactivate this bill?")) return;
    try {
      await deleteBill(id);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  async function handlePay(id: number) {
    setPayingId(id);
    try {
      await payBill(id, {});
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Payment failed");
    } finally {
      setPayingId(null);
    }
  }

  return (
    <div className="bills-page">
      <div className="page-header">
        <h2>Bills</h2>
        <button className="btn-primary" onClick={openCreate}>+ Add Bill</button>
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="summary-cards">
        <div className="summary-card" style={{ "--card-accent": "var(--blue)" } as React.CSSProperties}>
          <div className="summary-card-title">Monthly Bills</div>
          <div className="summary-card-value">{formatCurrency(totalMonthly)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--green)" } as React.CSSProperties}>
          <div className="summary-card-title">Paid This Month</div>
          <div className="summary-card-value">{paidCount}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--orange)" } as React.CSSProperties}>
          <div className="summary-card-title">Upcoming</div>
          <div className="summary-card-value">{upcomingCount}</div>
        </div>
      </div>

      <div className="filters-bar">
        <select value={filter} onChange={(e) => setFilter(e.target.value as typeof filter)}>
          <option value="active">Active Bills</option>
          <option value="inactive">Inactive Bills</option>
        </select>
      </div>

      <div className="card">
        {loading ? (
          <div className="page-loader">Loading...</div>
        ) : bills.length === 0 ? (
          <p className="empty-state">No {filter} bills found</p>
        ) : (
          <div className="bill-grid">
            {bills.map((bill) => (
              <div key={bill.id} className="bill-card">
                <div className="bill-card-header">
                  <div className="bill-card-info">
                    <span className="bill-card-name">{bill.name}</span>
                    <span className={`bill-frequency frequency-${bill.frequency}`}>{bill.frequency}</span>
                  </div>
                  <span className={`status-badge ${bill.is_paid_this_period ? "status-safe" : "status-warning"}`}>
                    {bill.is_paid_this_period ? "Paid" : "Due"}
                  </span>
                </div>
                <div className="bill-card-amount">{formatCurrency(bill.amount)}</div>
                <div className="bill-card-details">
                  <div className="bill-detail-item">
                    <span className="bill-detail-label">Due Day</span>
                    <span className="bill-detail-value">{ordinal(bill.due_day)}</span>
                  </div>
                  <div className="bill-detail-item">
                    <span className="bill-detail-label">Next Due</span>
                    <span className="bill-detail-value">{bill.next_due_date}</span>
                  </div>
                </div>
                <div className="bill-card-actions">
                  <button className="btn-primary btn-sm" onClick={() => handlePay(bill.id)} disabled={payingId === bill.id || bill.is_paid_this_period}>
                    {payingId === bill.id ? "Paying..." : bill.is_paid_this_period ? "Paid ✓" : "Pay Now"}
                  </button>
                  <div className="bill-card-icon-actions">
                    <button className="btn-icon" onClick={() => openEdit(bill)} title="Edit">
                      <EditIcon />
                    </button>
                    <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(bill.id)} title="Deactivate">
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
        <BillModal
          editing={editing}
          saving={saving}
          onSave={handleSave}
          onClose={() => { setShowModal(false); setEditing(null); }}
        />
      )}
    </div>
  );
}

function BillModal({ editing, saving, onSave, onClose }: {
  editing: Bill | null;
  saving: boolean;
  onSave: (data: BillFormData) => Promise<void>;
  onClose: () => void;
}) {
  const [name, setName] = useState(editing?.name || "");
  const [amount, setAmount] = useState(editing ? String(editing.amount) : "");
  const [dueDay, setDueDay] = useState(editing ? String(editing.due_day) : "1");
  const [frequency, setFrequency] = useState<"monthly" | "weekly" | "once">(editing?.frequency || "monthly");
  const [currencyCode, setCurrencyCode] = useState(editing?.currency_code || "KES");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!name.trim()) {
      setError("Bill name is required");
      return;
    }
    if (!amount || Number(amount) <= 0) {
      setError("Amount must be greater than zero");
      return;
    }
    const day = Number(dueDay);
    if (day < 1 || day > 31) {
      setError("Due day must be between 1 and 31");
      return;
    }
    try {
      await onSave({
        name: name.trim(),
        amount: Number(amount),
        currency_code: currencyCode,
        due_day: day,
        frequency,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{editing ? "Edit Bill" : "Add Bill"}</h3>
          <button className="btn-icon" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}
          <div className="form-group">
            <label htmlFor="bill-name">Bill Name</label>
            <input id="bill-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Netflix" required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="bill-amount">Amount</label>
              <input id="bill-amount" type="number" step="0.01" min="0" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" required />
            </div>
            <div className="form-group">
              <label htmlFor="bill-currency">Currency</label>
              <input id="bill-currency" type="text" maxLength={3} value={currencyCode} onChange={(e) => setCurrencyCode(e.target.value.toUpperCase())} placeholder="KES" required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="bill-due-day">Due Day</label>
              <input id="bill-due-day" type="number" min="1" max="31" value={dueDay} onChange={(e) => setDueDay(e.target.value)} required />
            </div>
            <div className="form-group">
              <label htmlFor="bill-frequency">Frequency</label>
              <select id="bill-frequency" value={frequency} onChange={(e) => setFrequency(e.target.value as typeof frequency)}>
                <option value="monthly">Monthly</option>
                <option value="weekly">Weekly</option>
                <option value="once">One-time</option>
              </select>
            </div>
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

function ordinal(n: number) {
  if (n > 3 && n < 21) return `${n}th`;
  switch (n % 10) {
    case 1: return `${n}st`;
    case 2: return `${n}nd`;
    case 3: return `${n}rd`;
    default: return `${n}th`;
  }
}


