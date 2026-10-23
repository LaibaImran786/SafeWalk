import Ring from "./Ring.jsx";
import { clock } from "./format.js";

export default function WarningPanel({ journey, now, busy, onCheckin, onCancel, onSos }) {
  const remaining = (Date.parse(journey.warning_deadline) - now) / 1000;
  return (
    <section className="panel center warn-panel" role="alert">
      <h2>You missed a check-in</h2>
      <p className="hint">Confirm you’re safe before the countdown ends, or an alert will be recorded for {journey.trusted_contact}.</p>
      <Ring remaining={remaining} total={journey.warning_seconds} tone="warn" label={clock(remaining)} sub="until alert" />
      <button className="btn primary wide" onClick={onCheckin} disabled={busy}>I’m safe</button>
      <button className="btn wide" onClick={onCancel} disabled={busy}>Cancel warning</button>
      <button className="btn danger wide" onClick={onSos} disabled={busy}>Send SOS now</button>
    </section>
  );
}
