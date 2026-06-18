import { useState, useEffect, useCallback } from "react";
import {
  fetchTransactions,
  fetchCategories,
  fetchTransactionSummary,
  createTransaction,
  updateTransaction,
  deleteTransaction,
} from "../api/transactions";
import { EditIcon, DeleteIcon, CloseIcon } from "../components/Icons";
import { formatCurrency } from "../utils/format";
import type { Transaction, TransactionFormData, TransactionSummary, Category } from "../types/transaction";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const CURRENT_MONTH = new Date().getMonth() + 1;
const CURRENT_YEAR = new Date().getFullYear();

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterType, setFilterType] = useState<"" | "income" | "expense">("");
  const [filterMonth, setFilterMonth] = useState(CURRENT_MONTH);
  const [filterYear, setFilterYear] = useState(CURRENT_YEAR);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Transaction | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    Promise.all([
      fetchTransactions({ month: filterMonth, year: filterYear, type: filterType }),
      fetchTransactionSummary(filterMonth, filterYear),
      fetchCategories(),
    ])
      .then(([txns, sum, cats]) => {
        setTransactions(txns);
        setSummary(sum);
        setCategories(cats);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filterMonth, filterYear, filterType]);

  useEffect(() => { load(); }, [load]);

  function openCreate() {
    setEditing(null);
    setShowModal(true);
  }

  function openEdit(t: Transaction) {
    setEditing(t);
    setShowModal(true);
  }

  async function handleSave(data: TransactionFormData) {
    setSaving(true);
    try {
      if (editing) {
        await updateTransaction(editing.id, data);
      } else {
        await createTransaction(data);
      }
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
    if (!confirm("Delete this transaction?")) return;
    try {
      await deleteTransaction(id);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  const incomeCategories = categories.filter((c) => c.type === "income");
  const expenseCategories = categories.filter((c) => c.type === "expense");

  return (
    <div className="transactions-page">
      <div className="page-header">
        <h2>Transactions</h2>
        <button className="btn-primary" onClick={openCreate}>+ Add Transaction</button>
      </div>

      {error && <div className="form-error">{error}</div>}

      {summary && (
        <div className="summary-cards">
          <div className="summary-card" style={{ "--card-accent": "var(--green)" } as React.CSSProperties}>
            <div className="summary-card-title">Income</div>
            <div className="summary-card-value">{formatCurrency(summary.total_income)}</div>
          </div>
          <div className="summary-card" style={{ "--card-accent": "var(--red)" } as React.CSSProperties}>
            <div className="summary-card-title">Expenses</div>
            <div className="summary-card-value">{formatCurrency(summary.total_expense)}</div>
          </div>
          <div className="summary-card" style={{ "--card-accent": "var(--purple)" } as React.CSSProperties}>
            <div className="summary-card-title">Net</div>
            <div className="summary-card-value">{formatCurrency(summary.net)}</div>
          </div>
          <div className="summary-card" style={{ "--card-accent": "var(--blue)" } as React.CSSProperties}>
            <div className="summary-card-title">Savings Rate</div>
            <div className="summary-card-value">{summary.savings_rate_pct.toFixed(1)}%</div>
          </div>
        </div>
      )}

      <div className="filters-bar">
        <select value={filterType} onChange={(e) => setFilterType(e.target.value as typeof filterType)}>
          <option value="">All Types</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
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
        ) : transactions.length === 0 ? (
          <p className="empty-state">No transactions found</p>
        ) : (
          <div className="txn-table">
            <div className="txn-table-header">
              <span>Date</span>
              <span>Type</span>
              <span>Category</span>
              <span>Note</span>
              <span>Amount</span>
              <span>Actions</span>
            </div>
            {transactions.map((txn) => (
              <div key={txn.id} className="txn-row">
                <span className="txn-date">{txn.date}</span>
                <span className={`txn-type txn-type-${txn.type}`}>{txn.type}</span>
                <span className="txn-category">
                  <span className="category-dot" style={{ backgroundColor: txn.category_color }} />
                  {txn.category_name}
                </span>
                <span className="txn-note">{txn.note || "—"}</span>
                <span className={`txn-amount ${txn.type === "income" ? "amount-income" : "amount-expense"}`}>
                  {txn.type === "income" ? "+" : "-"}{formatCurrency(txn.amount)}
                </span>
                <span className="txn-actions">
                    <button className="btn-icon" onClick={() => openEdit(txn)} title="Edit">
                      <EditIcon />
                    </button>
                    <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(txn.id)} title="Delete">
                      <DeleteIcon />
                    </button>
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <TransactionModal
          editing={editing}
          incomeCategories={incomeCategories}
          expenseCategories={expenseCategories}
          saving={saving}
          onSave={handleSave}
          onClose={() => { setShowModal(false); setEditing(null); }}
        />
      )}
    </div>
  );
}

function TransactionModal({ editing, incomeCategories, expenseCategories, saving, onSave, onClose }: {
  editing: Transaction | null;
  incomeCategories: Category[];
  expenseCategories: Category[];
  saving: boolean;
  onSave: (data: TransactionFormData) => Promise<void>;
  onClose: () => void;
}) {
  const today = new Date().toISOString().split("T")[0];
  const [type, setType] = useState<"income" | "expense">(editing?.type || "expense");
  const [amount, setAmount] = useState(editing ? String(editing.amount) : "");
  const [category, setCategory] = useState(editing?.category ? String(editing.category) : "");
  const [date, setDate] = useState(editing?.date || today);
  const [note, setNote] = useState(editing?.note || "");
  const [mpesaRef, setMpesaRef] = useState(editing?.mpesa_ref || "");
  const [error, setError] = useState("");

  const cats = type === "income" ? incomeCategories : expenseCategories;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!amount || Number(amount) <= 0) {
      setError("Amount must be greater than zero");
      return;
    }
    try {
      await onSave({
        type,
        amount: Number(amount),
        currency_code: "KES",
        category: category ? Number(category) : null,
        date,
        note,
        mpesa_ref: mpesaRef,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{editing ? "Edit Transaction" : "Add Transaction"}</h3>
          <button className="btn-icon" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}
          <div className="form-row">
            <div className="form-group">
              <label>Type</label>
              <div className="type-toggle">
                <button type="button" className={`type-btn${type === "expense" ? " active expense" : ""}`} onClick={() => { setType("expense"); setCategory(""); }}>Expense</button>
                <button type="button" className={`type-btn${type === "income" ? " active income" : ""}`} onClick={() => { setType("income"); setCategory(""); }}>Income</button>
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="txn-amount">Amount</label>
              <input id="txn-amount" type="number" step="0.01" min="0" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="txn-category">Category</label>
              <select id="txn-category" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">{cats.length === 0 ? "No categories" : `Select ${type} category`}</option>
                {cats.map((c) => (
                  <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="txn-date">Date</label>
              <input id="txn-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="txn-note">Note</label>
            <input id="txn-note" type="text" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note" />
          </div>
          <div className="form-group">
            <label htmlFor="txn-mpesa">M-Pesa Ref</label>
            <input id="txn-mpesa" type="text" value={mpesaRef} onChange={(e) => setMpesaRef(e.target.value)} placeholder="Optional M-Pesa reference" />
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


