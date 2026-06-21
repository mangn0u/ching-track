import { useState, useEffect, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { updateProfile, exportData, deleteAccount } from "../api/auth";
import { fetchPreferences, updatePreferences } from "../api/preferences";

export default function Settings() {
  const { user } = useAuth();

  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [phone, setPhone] = useState(user?.phone_number || "");
  const [mpesaPhone, setMpesaPhone] = useState(user?.mpesa_phone || "");
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState("");

  const [currency, setCurrency] = useState("KES");
  const [spendingLimit, setSpendingLimit] = useState("");
  const [prefsSaving, setPrefsSaving] = useState(false);
  const [prefsError, setPrefsError] = useState("");
  const [prefsSuccess, setPrefsSuccess] = useState("");

  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  useEffect(() => {
    fetchPreferences()
      .then((p) => {
        setCurrency(p.currency);
        setSpendingLimit(p.monthly_spending_limit ? String(p.monthly_spending_limit) : "");
      })
      .catch(() => {});
  }, []);

  async function handleProfileSubmit(e: FormEvent) {
    e.preventDefault();
    setProfileError("");
    setProfileSuccess("");
    setProfileSaving(true);
    try {
      await updateProfile({
        first_name: firstName,
        last_name: lastName,
        phone_number: phone,
        mpesa_phone: mpesaPhone || null,
      });
      setProfileSuccess("Profile updated");
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setProfileSaving(false);
    }
  }

  async function handlePrefsSubmit(e: FormEvent) {
    e.preventDefault();
    setPrefsError("");
    setPrefsSuccess("");
    setPrefsSaving(true);
    try {
      await updatePreferences({
        currency,
        monthly_spending_limit: spendingLimit ? Number(spendingLimit) : null,
      });
      setPrefsSuccess("Preferences saved");
    } catch (err) {
      setPrefsError(err instanceof Error ? err.message : "Failed to save preferences");
    } finally {
      setPrefsSaving(false);
    }
  }

  async function handleExport() {
    setExportError("");
    setExporting(true);
    try {
      const data = await exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chingtrack-export-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  }

  async function handleDeleteAccount() {
    setDeleteError("");
    setDeleting(true);
    try {
      await deleteAccount();
      window.location.href = "/login";
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Account deletion failed");
      setDeleting(false);
    }
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <h2>Settings</h2>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Profile</h3>
        </div>
        <form onSubmit={handleProfileSubmit} className="settings-form">
          {profileError && <div className="form-error">{profileError}</div>}
          {profileSuccess && <div className="form-success">{profileSuccess}</div>}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first-name">First Name</label>
              <input id="first-name" type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="First name" />
            </div>
            <div className="form-group">
              <label htmlFor="last-name">Last Name</label>
              <input id="last-name" type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="Last name" />
            </div>
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={user?.email || ""} disabled />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input id="phone" type="text" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+254..." />
            </div>
            <div className="form-group">
              <label htmlFor="mpesa-phone">M-Pesa Phone</label>
              <input id="mpesa-phone" type="text" value={mpesaPhone} onChange={(e) => setMpesaPhone(e.target.value)} placeholder="e.g. 254712345678" />
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={profileSaving} style={{ alignSelf: "flex-start" }}>
            {profileSaving ? "Saving..." : "Save Profile"}
          </button>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Preferences</h3>
        </div>
        <form onSubmit={handlePrefsSubmit} className="settings-form">
          {prefsError && <div className="form-error">{prefsError}</div>}
          {prefsSuccess && <div className="form-success">{prefsSuccess}</div>}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="currency">Preferred Currency</label>
              <select id="currency" value={currency} onChange={(e) => setCurrency(e.target.value)}>
                <option value="KES">KES - Kenyan Shilling</option>
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
                <option value="UGX">UGX - Ugandan Shilling</option>
                <option value="TZS">TZS - Tanzanian Shilling</option>
                <option value="NGN">NGN - Nigerian Naira</option>
                <option value="ZAR">ZAR - South African Rand</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="spending-limit">Monthly Spending Limit</label>
              <input id="spending-limit" type="number" step="0.01" min="0" value={spendingLimit} onChange={(e) => setSpendingLimit(e.target.value)} placeholder="0 = no limit" />
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={prefsSaving} style={{ alignSelf: "flex-start" }}>
            {prefsSaving ? "Saving..." : "Save Preferences"}
          </button>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Data</h3>
        </div>
        <div className="settings-form">
          {exportError && <div className="form-error">{exportError}</div>}
          <p className="settings-description">Download all your data as a JSON file (GDPR compliant).</p>
          <button className="btn-primary" onClick={handleExport} disabled={exporting} style={{ alignSelf: "flex-start" }}>
            {exporting ? "Exporting..." : "Export My Data"}
          </button>
        </div>
      </div>

      <div className="card card-danger">
        <div className="card-header">
          <h3>Danger Zone</h3>
        </div>
        <div className="settings-form">
          {deleteError && <div className="form-error">{deleteError}</div>}
          <p className="settings-description">
            Permanently delete your account and all associated data. This action cannot be undone.
          </p>
          <button className="btn-danger" onClick={() => setShowDeleteConfirm(true)} style={{ alignSelf: "flex-start" }}>
            Delete My Account
          </button>
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => !deleting && setShowDeleteConfirm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Delete Account?</h3>
            </div>
            <div className="modal-form">
              <p className="settings-description">
                This will permanently delete your account, transactions, budgets, bills, goals, and all associated data.
                This cannot be undone.
              </p>
              <div className="modal-actions">
                <button className="btn-secondary" onClick={() => setShowDeleteConfirm(false)} disabled={deleting}>Cancel</button>
                <button className="btn-danger" onClick={handleDeleteAccount} disabled={deleting}>
                  {deleting ? "Deleting..." : "Yes, Delete Everything"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
