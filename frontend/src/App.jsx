import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "./services/api.js";
import { useServerNow } from "./hooks/useServerNow.js";
import { useLocationReporting } from "./hooks/useLocation.js";
import Header from "./components/Header.jsx";
import JourneySetup from "./components/JourneySetup.jsx";
import ActivePanel from "./components/ActivePanel.jsx";
import WarningPanel from "./components/WarningPanel.jsx";
import AlertPanel from "./components/AlertPanel.jsx";
import Summary from "./components/Summary.jsx";
import Details from "./components/Details.jsx";
import AlertList from "./components/AlertList.jsx";

export default function App() {
  const [journey, setJourney] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [offset, setOffset] = useState(0); // server clock minus browser clock
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const now = useServerNow(offset);
  const auto = useRef({ running: false, failedAt: 0 });

  const applyJourney = useCallback((j) => {
    setJourney(j);
    setOffset(Date.parse(j.server_time) - Date.now());
  }, []);

  const refreshAlerts = useCallback(async (id) => {
    try {
      setAlerts((await api.getAlerts(id)).alerts);
    } catch {
      /* alert history is secondary; ignore transient failures */
    }
  }, []);

  // Restore an in-progress journey after a page refresh. State lives in the database.
  useEffect(() => {
    (async () => {
      try {
        const { journey: j } = await api.getActive();
        if (j) {
          applyJourney(j);
          refreshAlerts(j.id);
        }
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [applyJourney, refreshAlerts]);

  const geo = useLocationReporting(journey?.id, journey && journey.status !== "ENDED", applyJourney);

  // Run a backend action, then adopt the server's version of the journey.
  const act = useCallback(
    async (fn, { silent = false } = {}) => {
      if (!silent) setBusy(true);
      setError("");
      try {
        const res = await fn();
        applyJourney(res.journey);
        await refreshAlerts(res.journey.id);
        return true;
      } catch (e) {
        setError(e.message);
        try {
          const { journey: j } = await api.getActive(); // resync after a rejected (e.g. stale) action
          if (j) applyJourney(j);
        } catch {
          /* offline */
        }
        return false;
      } finally {
        if (!silent) setBusy(false);
      }
    },
    [applyJourney, refreshAlerts]
  );

  // The browser only *requests* transitions at the deadlines; the backend validates every one.
  useEffect(() => {
    if (!journey || auto.current.running || Date.now() - auto.current.failedAt < 3000) return;
    let fn = null;
    if (journey.status === "ACTIVE" && now >= Date.parse(journey.checkin_deadline)) {
      fn = () => api.missedCheckin(journey.id);
    } else if (journey.status === "ALERT_PENDING" && now >= Date.parse(journey.warning_deadline)) {
      fn = () => api.escalate(journey.id);
    }
    if (!fn) return;
    auto.current.running = true;
    act(fn, { silent: true }).then((ok) => {
      if (!ok) auto.current.failedAt = Date.now();
      auto.current.running = false;
    });
  }, [now, journey, act]);

  const start = async (data) => {
    setBusy(true);
    setError("");
    try {
      const res = await api.createJourney(data);
      setAlerts([]);
      applyJourney(res.journey);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setJourney(null);
    setAlerts([]);
    setError("");
  };

  const id = journey?.id;
  const triggered = [...alerts].reverse().find((a) => a.status === "simulated");

  let main;
  if (loading) {
    main = <p className="hint center-text">Loading…</p>;
  } else if (!journey) {
    main = <JourneySetup onStart={start} busy={busy} error={error} />;
  } else if (journey.status === "ENDED") {
    main = <Summary journey={journey} alerts={alerts} onNew={reset} />;
  } else {
    const left =
      journey.status === "ACTIVE" ? (
        <ActivePanel
          journey={journey}
          now={now}
          busy={busy}
          onCheckin={() => act(() => api.checkin(id))}
          onSos={() => act(() => api.sos(id))}
          onEnd={() => act(() => api.end(id))}
        />
      ) : journey.status === "ALERT_PENDING" ? (
        <WarningPanel
          journey={journey}
          now={now}
          busy={busy}
          onCheckin={() => act(() => api.checkin(id))}
          onCancel={() => act(() => api.cancelAlert(id))}
          onSos={() => act(() => api.sos(id))}
        />
      ) : (
        <AlertPanel journey={journey} alert={triggered} busy={busy} onEnd={() => act(() => api.end(id))} />
      );
    main = (
      <div className="grid">
        {left}
        <div className="stack">
          <Details journey={journey} geo={geo} />
          <AlertList alerts={alerts} />
        </div>
      </div>
    );
  }

  return (
    <div className="shell">
      <Header status={journey?.status} />
      {journey && error && (
        <p className="error banner" role="alert">{error}</p>
      )}
      <main>{main}</main>
      <footer className="footer">
        SafeWalk is a prototype. Alerts are recorded and simulated; they are not delivered to real contacts or emergency services.
      </footer>
    </div>
  );
}
