import { useState, useEffect, useCallback } from "react";
import { fetchDashboard } from "../api/dashboard";
import { formatCurrency } from "../utils/format";
import type { DashboardData } from "../types/dashboard";

const CURRENT_MONTH = new Date().getMonth() + 1;
const CURRENT_YEAR = new Date().getFullYear();
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterMonth, setFilterMonth] = useState(CURRENT_MONTH);
  const [filterYear, setFilterYear] = useState(CURRENT_YEAR);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    fetchDashboard(filterMonth, filterYear)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filterMonth, filterYear]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="page-loader">Loading dashboard...</div>;
  if (error) return <div className="page-error">{error}</div>;
  if (!data) return null;

  const { summary, spending_by_category, budget_vs_actual, global_limit, upcoming_bills, goals, mom_change, currency } = data;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <div className="dashboard-filters">
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
      </div>

      <div className="summary-cards">
        <SummaryCard
          title="Income"
          value={summary.total_income}
          currency={currency}
          change={mom_change.income_change_pct}
          color="var(--green)"
        />
        <SummaryCard
          title="Expenses"
          value={summary.total_expense}
          currency={currency}
          change={mom_change.expense_change_pct}
          color="var(--red)"
          inverse
        />
        <SummaryCard
          title="Net Savings"
          value={summary.net}
          currency={currency}
          color="var(--purple)"
        />
        <SummaryCard
          title="Savings Rate"
          value={summary.savings_rate_pct}
          suffix="%"
          color="var(--blue)"
        />
      </div>

      <div className="dashboard-grid">
        <div className="card card-full">
          <div className="card-header">
            <h3>Spending by Category</h3>
          </div>
          <div className="category-list">
            {spending_by_category.length === 0 ? (
              <p className="empty-state">No expenses this month</p>
            ) : (
              spending_by_category.map((cat) => (
                <div key={cat.category} className="category-row">
                  <div className="category-info">
                    <span className="category-icon">{cat.icon || "●"}</span>
                    <span className="category-name">{cat.category}</span>
                  </div>
                  <div className="category-bar-wrap">
                    <div className="category-bar">
                      <div
                        className="category-bar-fill"
                        style={{ width: `${cat.pct}%`, backgroundColor: cat.color }}
                      />
                    </div>
                  </div>
                  <div className="category-amount">
                    <span className="amount">{formatCurrency(cat.amount, currency)}</span>
                    <span className="pct">{cat.pct.toFixed(1)}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Budget vs Actual</h3>
          </div>
          <div className="budget-list">
            {budget_vs_actual.length === 0 ? (
              <p className="empty-state">No budgets set</p>
            ) : (
              budget_vs_actual.map((b) => (
                <div key={b.category_id} className="budget-row">
                  <div className="budget-info">
                    <span className="category-icon">{b.category_icon || "●"}</span>
                    <span className="category-name">{b.category_name}</span>
                    <span className={`status-badge status-${b.status}`}>{b.status}</span>
                  </div>
                  <div className="budget-bar-wrap">
                    <div className="budget-bar">
                      <div
                        className="budget-bar-fill"
                        style={{ width: `${Math.min(b.pct_used, 100)}%` }}
                      />
                    </div>
                    <div className="budget-labels">
                      <span>{formatCurrency(b.actual, currency)}</span>
                      <span>{formatCurrency(b.limit, currency)}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          {global_limit.monthly_limit > 0 && (
            <div className="global-limit">
              <div className="global-limit-header">
                <span>Global Spending Limit</span>
                <span className={`status-badge status-${global_limit.status}`}>{global_limit.status}</span>
              </div>
              <div className="budget-bar">
                <div className="budget-bar-fill" style={{ width: `${Math.min(global_limit.pct_used, 100)}%` }} />
              </div>
              <div className="budget-labels">
                <span>{formatCurrency(global_limit.total_spent, currency)}</span>
                <span>{formatCurrency(global_limit.monthly_limit, currency)}</span>
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Upcoming Bills</h3>
          </div>
          <div className="bills-list">
            {upcoming_bills.length === 0 ? (
              <p className="empty-state">No upcoming bills</p>
            ) : (
              upcoming_bills.map((bill) => (
                <div key={bill.id} className="bill-row">
                  <div className="bill-info">
                    <span className="bill-name">{bill.name}</span>
                    <span className="bill-due">Due {bill.next_due_date}</span>
                  </div>
                  <div className="bill-amount">{formatCurrency(bill.amount, bill.currency_code)}</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Savings Goals</h3>
          </div>
          <div className="goals-list">
            {goals.length === 0 ? (
              <p className="empty-state">No goals set</p>
            ) : (
              goals.map((g) => (
                <div key={g.id} className="goal-row">
                  <div className="goal-info">
                    <span className="goal-name">{g.name}</span>
                    <span className={`goal-status ${g.is_on_track ? "on-track" : "off-track"}`}>
                      {g.is_on_track ? "On track" : "Behind"}
                    </span>
                  </div>
                  <div className="goal-bar-wrap">
                    <div className="goal-bar">
                      <div className="goal-bar-fill" style={{ width: `${g.progress_pct}%` }} />
                    </div>
                    <div className="goal-labels">
                      <span>{formatCurrency(g.total_saved, g.currency_code)}</span>
                      <span>{formatCurrency(g.target_amount, g.currency_code)}</span>
                    </div>
                  </div>
                  <span className="goal-pct">{g.progress_pct.toFixed(0)}%</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}



function SummaryCard({ title, value, currency, change, suffix, color, inverse }: {
  title: string;
  value: number;
  currency?: string;
  change?: number;
  suffix?: string;
  color: string;
  inverse?: boolean;
}) {
  const display = suffix
    ? `${value.toFixed(1)}${suffix}`
    : formatCurrency(value, currency || "KES");

  return (
    <div className="summary-card" style={{ "--card-accent": color } as React.CSSProperties}>
      <div className="summary-card-title">{title}</div>
      <div className="summary-card-value">{display}</div>
      {change !== undefined && (
        <div className={`summary-card-change ${change >= 0 ? "up" : "down"} ${inverse ? "inverse" : ""}`}>
          {change >= 0 ? "↑" : "↓"} {Math.abs(change).toFixed(1)}% vs last month
        </div>
      )}
    </div>
  );
}
