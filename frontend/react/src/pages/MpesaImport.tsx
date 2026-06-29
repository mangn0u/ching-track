import { useState, useEffect } from "react";
import { parseSms, confirmImport } from "../api/mpesa";
import { fetchCategories } from "../api/transactions";
import { formatCurrency } from "../utils/format";
import type { ParsedTransaction } from "../types/mpesa";
import type { Category } from "../types/transaction";

export default function MpesaImport() {
  const [rawSms, setRawSms] = useState("");
  const [parsed, setParsed] = useState<ParsedTransaction | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [parsing, setParsing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [importedId, setImportedId] = useState<number | null>(null);
  const [history, setHistory] = useState<ParsedTransaction[]>([]);

  useEffect(() => {
    fetchCategories().then((cats) => {
      setCategories(cats);
      if (cats.length > 0) setSelectedCategory(String(cats[0].id));
    }).catch(() => {});
  }, []);

  async function handleParse() {
    setError("");
    setSuccess(false);
    setImportedId(null);

    const trimmed = rawSms.trim();
    if (!trimmed) {
      setError("Please paste an M-Pesa SMS message.");
      return;
    }
    if (trimmed.length < 20) {
      setError("SMS text is too short to be a valid M-Pesa message.");
      return;
    }
    if (trimmed.length > 1000) {
      setError("SMS text is too long (max 1000 characters).");
      return;
    }

    setParsing(true);
    try {
      const res = await parseSms(trimmed);
      if (res.parsed) {
        setParsed(res.transaction);
        if (res.transaction.type === "expense") {
          const expenseCats = categories.filter((c) => c.type === "expense");
          if (expenseCats.length > 0) setSelectedCategory(String(expenseCats[0].id));
        } else {
          const incomeCats = categories.filter((c) => c.type === "income");
          if (incomeCats.length > 0) setSelectedCategory(String(incomeCats[0].id));
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to parse SMS");
    } finally {
      setParsing(false);
    }
  }

  async function handleConfirm() {
    if (!parsed) return;
    setError("");
    setSaving(true);
    try {
      const res = await confirmImport({
        type: parsed.type,
        amount: parsed.amount,
        currency_code: parsed.currency_code,
        date: parsed.date,
        note: parsed.note,
        mpesa_ref: parsed.mpesa_ref,
        raw_sms: parsed.raw_sms,
        category_id: selectedCategory ? Number(selectedCategory) : null,
      });
      setImportedId(res.id);
      setSuccess(true);
      setHistory((prev) => [parsed, ...prev]);
      setParsed(null);
      setRawSms("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save transaction");
    } finally {
      setSaving(false);
    }
  }

  function handleNew() {
    setParsed(null);
    setSuccess(false);
    setImportedId(null);
    setError("");
    setRawSms("");
  }

  const filteredCategories = categories.filter(
    (c) => c.type === (parsed?.type || "expense"),
  );

  return (
    <div className="mpesa-page">
      <div className="page-header">
        <h2>M-Pesa Import</h2>
      </div>

      <div className="mpesa-layout">
        <div className="card mpesa-input-section">
          <h3 className="card-title">Paste M-Pesa SMS</h3>
          <p className="settings-description">
            Copy an M-Pesa message from your SMS app and paste it below. The system will automatically extract the amount, type, date, and reference.
          </p>
          <textarea
            className="mpesa-textarea"
            rows={4}
            value={rawSms}
            onChange={(e) => setRawSms(e.target.value)}
            placeholder={`Paste M-Pesa SMS here...\n\nExample:\nKSh 1,500.00 sent to John Doe 0722123456 on 29/6/26 at 10:30 AM. New M-PESA balance is KSh 5,000.00. Transaction code, RKX123456Z.`}
            disabled={!!parsed}
          />
          {error && <div className="form-error">{error}</div>}
          {success && importedId && (
            <div className="form-success">
              Transaction imported successfully (#{importedId}).
            </div>
          )}

          <div className="mpesa-actions">
            {!parsed ? (
              <button className="btn-primary" onClick={handleParse} disabled={parsing || !rawSms.trim()}>
                {parsing ? "Parsing..." : "Parse SMS"}
              </button>
            ) : (
              <>
                <button className="btn-secondary" onClick={handleNew}>
                  Start Over
                </button>
                <button className="btn-primary" onClick={handleConfirm} disabled={saving}>
                  {saving ? "Importing..." : "Confirm & Import"}
                </button>
              </>
            )}
          </div>
        </div>

        {parsed && (
          <div className="card mpesa-preview-section">
            <h3 className="card-title">Parsed Transaction</h3>

            <div className="mpesa-preview-grid">
              <div className="mpesa-preview-item">
                <span className="mpesa-preview-label">Type</span>
                <span className={`txn-type txn-type-${parsed.type}`}>{parsed.type}</span>
              </div>

              <div className="mpesa-preview-item">
                <span className="mpesa-preview-label">Amount</span>
                <span className={`mpesa-preview-value ${parsed.type === "income" ? "amount-income" : "amount-expense"}`}>
                  {parsed.type === "income" ? "+" : "-"}{formatCurrency(Number(parsed.amount))}
                </span>
              </div>

              <div className="mpesa-preview-item">
                <span className="mpesa-preview-label">Date</span>
                <span className="mpesa-preview-value">{parsed.date}</span>
              </div>

              <div className="mpesa-preview-item">
                <span className="mpesa-preview-label">M-Pesa Ref</span>
                <span className="mpesa-preview-value mpesa-ref">{parsed.mpesa_ref || "—"}</span>
              </div>

              <div className="mpesa-preview-item mpesa-preview-full">
                <span className="mpesa-preview-label">Counterparty</span>
                <span className="mpesa-preview-value">{parsed.note || "—"}</span>
              </div>

              <div className="mpesa-preview-item mpesa-preview-full">
                <span className="mpesa-preview-label">Category</span>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="mpesa-category-select"
                >
                  <option value="">No category</option>
                  {filteredCategories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.icon} {c.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="card">
            <h3 className="card-title">Import History</h3>
            <div className="mpesa-history-list">
              {history.map((h, i) => (
                <div key={i} className="mpesa-history-row">
                  <span className={`txn-type txn-type-${h.type}`}>{h.type}</span>
                  <span className={`txn-amount ${h.type === "income" ? "amount-income" : "amount-expense"}`}>
                    {formatCurrency(Number(h.amount))}
                  </span>
                  <span className="mpesa-history-meta">{h.note || h.mpesa_ref}</span>
                  <span className="mpesa-history-date">{h.date}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
