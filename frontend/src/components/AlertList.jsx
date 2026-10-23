import { ALERT_STATUS, REASONS, when } from "./format.js";

export default function AlertList({ alerts }) {
  return (
    <section className="panel">
      <h2>Alert history</h2>
      {alerts.length === 0 ? (
        <p className="hint">No alerts on this journey.</p>
      ) : (
        <ul className="list">
          {alerts.map((a) => (
            <li key={a.id} className="inset-item">
              <div className="item-top">
                <strong>{REASONS[a.reason] || a.reason}</strong>
                <span className={`tag ${a.status}`}>{ALERT_STATUS[a.status] || a.status}</span>
              </div>
              <p>{a.message}</p>
              <small>{when(a.created_at)}</small>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
