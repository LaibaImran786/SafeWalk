const LABELS = {
  ACTIVE: ["Journey active", "ok"],
  ALERT_PENDING: ["Check-in missed", "warn"],
  ALERT_TRIGGERED: ["Alert recorded", "danger"],
  ENDED: ["Journey ended", "calm"],
};

export default function Header({ status }) {
  const [label, tone] = LABELS[status] || ["No journey", "calm"];
  return (
    <header className="header">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" />
            <path d="M9 12l2 2 4-4" />
          </svg>
        </span>
        <div>
          <h1>SafeWalk</h1>
          <p>Journey check-ins with a safety net</p>
        </div>
      </div>
      <span className={`pill ${tone}`}>
        <i aria-hidden="true" /> {label}
      </span>
    </header>
  );
}
