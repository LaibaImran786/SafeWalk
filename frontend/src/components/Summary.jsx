import AlertList from "./AlertList.jsx";
import { when } from "./format.js";

export default function Summary({ journey, alerts, onNew }) {
  return (
    <div className="grid">
      <section className="panel center">
        <h2>Journey ended</h2>
        <dl className="facts">
          <div><dt>Traveler</dt><dd>{journey.traveler_name}</dd></div>
          <div><dt>Destination</dt><dd>{journey.destination}</dd></div>
          <div><dt>Started</dt><dd>{when(journey.created_at)}</dd></div>
          <div><dt>Ended</dt><dd>{when(journey.ended_at)}</dd></div>
          <div><dt>Alerts</dt><dd>{alerts.length}</dd></div>
        </dl>
        <p className="hint">The safety workflow has stopped. No further alerts can be raised for this journey.</p>
        <button className="btn primary wide" onClick={onNew}>Start a new journey</button>
      </section>
      <AlertList alerts={alerts} />
    </div>
  );
}
