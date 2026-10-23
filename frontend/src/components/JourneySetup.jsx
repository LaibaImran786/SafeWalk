import { useState } from "react";
import BriefingCard from "./BriefingCard.jsx";

const INTERVALS = [
  [10, "Every 10 seconds (demo)"],
  [60, "Every minute"],
  [300, "Every 5 minutes"],
  [900, "Every 15 minutes"],
  [1800, "Every 30 minutes"],
];
const WARNINGS = [
  [10, "10 seconds (demo)"],
  [30, "30 seconds"],
  [60, "1 minute"],
  [120, "2 minutes"],
];

export default function JourneySetup({ onStart, busy, error }) {
  const [f, setF] = useState({
    traveler_name: "",
    destination: "",
    trusted_contact: "",
    trusted_contact_phone: "",
    checkin_interval_seconds: 60,
    warning_seconds: 30,
  });
  const [touched, setTouched] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const missing = ["traveler_name", "destination", "trusted_contact"].filter((k) => !f[k].trim());

  function submit(e) {
    e.preventDefault();
    setTouched(true);
    if (missing.length) return;
    onStart({
      ...f,
      trusted_contact_phone: f.trusted_contact_phone.trim() || null,
      checkin_interval_seconds: Number(f.checkin_interval_seconds),
      warning_seconds: Number(f.warning_seconds),
    });
  }

  const bad = (k) => touched && !f[k].trim();

  return (
    <div className="grid">
      <form className="panel" onSubmit={submit} noValidate>
        <h2>Start a journey</h2>
        <p className="hint">Tell SafeWalk where you’re going and who to alert if you stop responding.</p>

        <label className="field">
          <span>Your name</span>
          <input value={f.traveler_name} onChange={set("traveler_name")} aria-invalid={bad("traveler_name")} autoComplete="name" />
          {bad("traveler_name") && <em>Enter your name.</em>}
        </label>
        <label className="field">
          <span>Destination</span>
          <input value={f.destination} onChange={set("destination")} aria-invalid={bad("destination")} placeholder="Where are you heading?" />
          {bad("destination") && <em>Enter a destination.</em>}
        </label>
        <div className="row">
          <label className="field">
            <span>Trusted contact</span>
            <input value={f.trusted_contact} onChange={set("trusted_contact")} aria-invalid={bad("trusted_contact")} />
            {bad("trusted_contact") && <em>Enter a contact name.</em>}
          </label>
          <label className="field">
            <span>Contact phone (optional)</span>
            <input value={f.trusted_contact_phone} onChange={set("trusted_contact_phone")} inputMode="tel" />
          </label>
        </div>
        <div className="row">
          <label className="field">
            <span>Check in</span>
            <select value={f.checkin_interval_seconds} onChange={set("checkin_interval_seconds")}>
              {INTERVALS.map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Warning countdown</span>
            <select value={f.warning_seconds} onChange={set("warning_seconds")}>
              {WARNINGS.map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </label>
        </div>

        {error && <p className="error" role="alert">{error}</p>}
        <button type="submit" className="btn primary wide" disabled={busy}>
          {busy ? "Starting…" : "Start journey"}
        </button>
      </form>

      <div className="stack">
        <BriefingCard
          title="Safety briefing"
          cta="Get safety briefing"
          name={f.traveler_name}
          destination={f.destination}
          interval={Number(f.checkin_interval_seconds)}
        />
        <section className="panel inset-panel">
          <h2>How it works</h2>
          <p className="hint">
            SafeWalk asks you to check in on a schedule. If you miss one, you get a warning countdown. If it runs out,
            an alert is recorded. Notifications are simulated in this prototype and are not sent to your contact.
          </p>
        </section>
      </div>
    </div>
  );
}
