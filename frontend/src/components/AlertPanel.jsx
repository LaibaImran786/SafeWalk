import BriefingCard from "./BriefingCard.jsx";
import { REASONS, coords, when } from "./format.js";

export default function AlertPanel({ journey, alert, busy, onEnd }) {
  const pos = alert ? coords(alert) : null;
  return (
    <div className="stack">
      <section className="panel center alert-panel" role="alert">
        <div className="alert-badge" aria-hidden="true">!</div>
        <h2>Emergency alert recorded</h2>
        <dl className="facts">
          <div><dt>Reason</dt><dd>{alert ? REASONS[alert.reason] : "—"}</dd></div>
          <div><dt>Journey</dt><dd>{journey.traveler_name} to {journey.destination}</dd></div>
          <div>
            <dt>Last known location</dt>
            <dd>{pos ? <>{pos} <small>at {when(alert.location_updated_at)}</small></> : "Location unavailable"}</dd>
          </div>
          <div>
            <dt>Contact</dt>
            <dd>{journey.trusted_contact}{journey.trusted_contact_phone ? ` · ${journey.trusted_contact_phone}` : ""}</dd>
          </div>
          <div>
            <dt>Notification</dt>
            <dd><span className="tag simulated">Simulated</span> No real message was delivered.</dd>
          </div>
          <div><dt>Recorded</dt><dd>{alert ? when(alert.created_at) : "—"}</dd></div>
        </dl>
        <button className="btn wide" onClick={onEnd} disabled={busy}>End journey</button>
      </section>
      {alert && (
        <BriefingCard
          kind="alert_explanation"
          title="What happened"
          cta="Explain this alert"
          name={journey.traveler_name}
          destination={journey.destination}
          reason={alert.reason}
        />
      )}
    </div>
  );
}
