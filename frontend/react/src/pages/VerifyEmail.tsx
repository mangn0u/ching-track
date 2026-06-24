import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { verifyEmail } from "../api/auth";

type Status = "loading" | "success" | "error";

export default function VerifyEmail() {
  const { token } = useParams<{ token: string }>();
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token found in the link.");
      return;
    }

    verifyEmail(token)
      .then((res) => {
        setMessage(res.message);
        setStatus("success");
      })
      .catch((err: Error) => {
        setMessage(err.message || "Verification failed. The link may have expired.");
        setStatus("error");
      });
  }, [token]);

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1>ChingTrack</h1>
          <p>Email Verification</p>
        </div>

        <div className="verify-email-body">
          {status === "loading" && (
            <div className="verify-email-state">
              <div className="verify-email-icon verify-email-icon--loading" aria-hidden="true">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
              </div>
              <p className="verify-email-message">Verifying your email address…</p>
            </div>
          )}

          {status === "success" && (
            <div className="verify-email-state">
              <div className="verify-email-icon verify-email-icon--success" aria-hidden="true">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </div>
              <p className="verify-email-message verify-email-message--success">{message}</p>
            </div>
          )}

          {status === "error" && (
            <div className="verify-email-state">
              <div className="verify-email-icon verify-email-icon--error" aria-hidden="true">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
              </div>
              <p className="verify-email-message verify-email-message--error">{message}</p>
            </div>
          )}
        </div>

        <p className="login-footer">
          {status === "success" ? (
            <Link to="/login">Proceed to Sign In →</Link>
          ) : status === "error" ? (
            <>
              Need to register again? <Link to="/register">Create account</Link>
            </>
          ) : null}
        </p>
      </div>
    </div>
  );
}
