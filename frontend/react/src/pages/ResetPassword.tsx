import { useState, type FormEvent } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { resetPassword } from "../api/auth";

export default function ResetPassword() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    if (password !== passwordConfirm) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (!token) {
      setError("Invalid reset link.");
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, password);
      navigate("/login", {
        state: { message: "Password reset successfully! You can now sign in." },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1>ChingTrack</h1>
          <p>Enter your new password</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="form-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min 8 characters"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password_confirm">Confirm New Password</label>
            <input
              id="password_confirm"
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="Re-enter your new password"
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Resetting..." : "Reset password"}
          </button>
        </form>
        <p className="login-footer">
          <Link to="/login">Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}
