import Ring from "./Ring.jsx";
import { clock } from "./format.js";

export default function ActivePanel({ journey, now, busy, onCheckin, onSos, onEnd }) {
  const total = journey.checkin_interval_seconds;
  const remaining = (Date.parse(journey.checkin_deadline) - now) / 1000;
  return (
    <section className="panel center">
      <h2>On your way to {journey.destination}</h2>
      <Ring remaining={remaining} total={total} tone="calm" label={clock(remaining)} sub="until next check-in" />
      <button className="btn primary wide" onClick={onCheckin} disabled={busy}>I’m safe — check in</button>
      <button className="sos" onClick={onSos} disabled={busy} aria-label="Send SOS now">
        <span>SOS</span>
      </button>
      <p className="hint">Press SOS to raise an alert immediately, without a countdown.</p>
      <button className="btn quiet" onClick={onEnd} disabled={busy}>End journey</button>
    </section>
  );
}
