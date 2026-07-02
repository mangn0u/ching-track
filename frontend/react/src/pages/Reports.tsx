import { useState, useEffect, useCallback } from "react";
import { fetchTrends } from "../api/reports";
import { formatCurrency } from "../utils/format";
import type { TrendsData } from "../types/reports";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const RANGE_OPTIONS = [
  { label: "3 months", value: 3 },
  { label: "6 months", value: 6 },
  { label: "12 months", value: 12 },
];

export default function Reports() {
  const [data, setData] = useState<TrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [range, setRange] = useState(6);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    fetchTrends(range)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [range]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="page-loader">Loading reports...</div>;
  if (error) return <div className="page-error">{error}</div>;
  if (!data) return null;

  const { monthly, total_income, total_expense, net, currency, top_categories } = data;
  const maxAmount = Math.max(...monthly.map((m) => Math.max(m.income, m.expense)), 1);

  return (
    <div className="reports-page">
      <div className="page-header">
        <h2>Reports</h2>
        <div className="filters-bar">
          {RANGE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`category-tab ${range === opt.value ? "active" : ""}`}
              onClick={() => setRange(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="summary-cards">
        <div className="summary-card" style={{ "--card-accent": "var(--green)" } as React.CSSProperties}>
          <div className="summary-card-title">Total Income</div>
          <div className="summary-card-value">{formatCurrency(total_income, currency)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--red)" } as React.CSSProperties}>
          <div className="summary-card-title">Total Expenses</div>
          <div className="summary-card-value">{formatCurrency(total_expense, currency)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--purple)" } as React.CSSProperties}>
          <div className="summary-card-title">Net</div>
          <div className="summary-card-value">{formatCurrency(net, currency)}</div>
        </div>
        <div className="summary-card" style={{ "--card-accent": "var(--blue)" } as React.CSSProperties}>
          <div className="summary-card-title">Savings Rate</div>
          <div className="summary-card-value">
            {total_income > 0 ? `${((net / total_income) * 100).toFixed(1)}%` : "—"}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Income vs Expenses</h3>
        </div>
        <div className="chart-container">
          <div className="chart-bars">
            {monthly.map((m) => (
              <div key={`${m.year}-${m.month}`} className="chart-column">
                <div className="chart-bars-group">
                  <div className="chart-bar-wrap">
                    <div
                      className="chart-bar chart-bar-income"
                      style={{ height: `${(m.income / maxAmount) * 100}%` }}
                      title={`Income: ${formatCurrency(m.income, currency)}`}
                    />
                  </div>
                  <div className="chart-bar-wrap">
                    <div
                      className="chart-bar chart-bar-expense"
                      style={{ height: `${(m.expense / maxAmount) * 100}%` }}
                      title={`Expenses: ${formatCurrency(m.expense, currency)}`}
                    />
                  </div>
                </div>
                <div className="chart-label">{MONTHS[m.month - 1]} {String(m.year).slice(2)}</div>
              </div>
            ))}
          </div>
          <div className="chart-legend">
            <span className="chart-legend-item">
              <span className="chart-legend-dot income" /> Income
            </span>
            <span className="chart-legend-item">
              <span className="chart-legend-dot expense" /> Expenses
            </span>
          </div>
        </div>
      </div>

      <div className="reports-grid">
        <div className="card">
          <div className="card-header">
            <h3>Monthly Breakdown</h3>
          </div>
          <div className="monthly-table">
            <div className="monthly-table-header">
              <span>Month</span>
              <span>Income</span>
              <span>Expenses</span>
              <span>Net</span>
            </div>
            {monthly.map((m) => (
              <div key={`${m.year}-${m.month}`} className="monthly-table-row">
                <span className="monthly-table-month">{MONTHS[m.month - 1]} {m.year}</span>
                <span className="monthly-table-income">{formatCurrency(m.income, currency)}</span>
                <span className="monthly-table-expense">{formatCurrency(m.expense, currency)}</span>
                <span className={`monthly-table-net ${m.net >= 0 ? "positive" : "negative"}`}>
                  {formatCurrency(m.net, currency)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Top Spending Categories</h3>
          </div>
          {top_categories.length === 0 ? (
            <p className="empty-state">No expenses in this period</p>
          ) : (
            <div className="category-list">
              {top_categories.map((cat) => {
                const pct = total_expense > 0 ? (cat.total / total_expense) * 100 : 0;
                return (
                  <div key={cat.category} className="category-row">
                    <div className="category-info">
                      <span className="category-icon">{cat.icon || "●"}</span>
                      <span className="category-name">{cat.category}</span>
                    </div>
                    <div className="category-bar-wrap">
                      <div className="category-bar">
                        <div className="category-bar-fill" style={{ width: `${pct}%`, backgroundColor: cat.color }} />
                      </div>
                    </div>
                    <div className="category-amount">
                      <span className="amount">{formatCurrency(cat.total, currency)}</span>
                      <span className="pct">{pct.toFixed(1)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
