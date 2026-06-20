import { useState, type FormEvent } from "react";
import { changePassword } from "../api/auth";

export default function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (newPassword !== newPasswordConfirm) {
      setError("New passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      const res = await changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      });
      setSuccess(res.message);
      setOldPassword("");
      setNewPassword("");
      setNewPasswordConfirm("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to change password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <h2>Change Password</h2>
      </div>

      <div className="card" style={{ maxWidth: 480 }}>
        <form onSubmit={handleSubmit} className="modal-form" style={{ padding: 0, marginTop: 0 }}>
          {error && <div className="form-error">{error}</div>}
          {success && <div className="form-success">{success}</div>}

          <div className="form-group">
            <label htmlFor="old_password">Current Password</label>
            <input
              id="old_password"
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="Enter your current password"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="new_password">New Password</label>
            <input
              id="new_password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Min 8 characters"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="new_password_confirm">Confirm New Password</label>
            <input
              id="new_password_confirm"
              type="password"
              value={newPasswordConfirm}
              onChange={(e) => setNewPasswordConfirm(e.target.value)}
              placeholder="Re-enter new password"
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Updating..." : "Update password"}
          </button>
        </form>
      </div>
    </div>
  );
}
