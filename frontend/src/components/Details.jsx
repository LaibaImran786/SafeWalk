import { coords, when } from "./format.js";

const GEO_TEXT = {
  requesting: "Waiting for location permission…",
  granted: "Location sharing is on.",
  denied: "Location permission was denied. Your journey continues without a location.",
  unavailable: "Location is unavailable on this device. Your journey continues without it.",
};

export default function Details({ journey, geo }) {
  const pos = coords(journey);
  return (
    <section className="panel">
      <h2>Journey details</h2>
      <dl className="facts">
        <div><dt>Traveler</dt><dd>{journey.traveler_name}</dd></div>
        <div><dt>Destination</dt><dd>{journey.destination}</dd></div>
        <div>
          <dt>Trusted contact</dt>
          <dd>{journey.trusted_contact}{journey.trusted_contact_phone ? ` · ${journey.trusted_contact_phone}` : ""}</dd>
        </div>
        <div><dt>Started</dt><dd>{when(journey.created_at)}</dd></div>
        <div>
          <dt>Latest location</dt>
          <dd>
            {pos ? (
              <>
                {pos} <small>updated {when(journey.location_updated_at)}</small>
              </>
            ) : (
              "Location unavailable"
            )}
          </dd>
        </div>
      </dl>
      {journey.status !== "ENDED" && <p className={`hint geo ${geo}`}>{GEO_TEXT[geo]}</p>}
    </section>
  );
}
