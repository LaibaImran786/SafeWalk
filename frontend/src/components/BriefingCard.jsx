import { useState } from "react";
import { api } from "../services/api.js";

export default function BriefingCard({ kind = "briefing", name, destination, interval, reason, title, cta }) {
  const [state, setState] = useState({ loading: false, data: null, error: "" });
  const ready = name?.trim() && destination?.trim();

  async function load() {
    setState({ loading: true, data: null, error: "" });
    try {
      const data = await api.briefing({
        kind,
        traveler_name: name.trim(),
        destination: destination.trim(),
        checkin_interval_seconds: interval || null,
        reason: reason || null,
      });
      setState({ loading: false, data, error: "" });
    } catch (e) {
      setState({ loading: false, data: null, error: e.message });
    }
  }

  return (
    <section className="panel" aria-live="polite">
      <h2>{title}</h2>
      {state.data && (
        <>
          
<p className="ai-text">{state.data.text}</p>

<p className="hint">
  {state.data.ai_available
    ? "Personalized safety guidance · Powered by Gemma 4"
    : "General safety guidance · Personalized AI briefing temporarily unavailable"}
</p>

        </>
      )}
      {state.error && <p className="error">{state.error}</p>}
      {!state.data && !state.error && <p className="hint">Optional. SafeWalk works the same without it.</p>}
      <button type="button" className="btn" onClick={load} disabled={!ready || state.loading}>
        {state.loading ? "Writing…" : cta}
      </button>
    </section>
  );
}
