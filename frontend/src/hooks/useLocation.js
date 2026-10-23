import { useEffect, useRef, useState } from "react";
import { api } from "../services/api.js";

/**
 * Watches the browser position while a journey is open and posts it to the backend.
 * geo: "requesting" | "granted" | "denied" | "unavailable"
 * Coordinates are never invented: without permission nothing is sent.
 */
export function useLocationReporting(journeyId, enabled, onSaved) {
  const [geo, setGeo] = useState("requesting");
  const last = useRef(0);
  const saved = useRef(onSaved);
  saved.current = onSaved;

  useEffect(() => {
    if (!journeyId || !enabled) return undefined;
    if (!("geolocation" in navigator)) {
      setGeo("unavailable");
      return undefined;
    }
    setGeo("requesting");
    const watchId = navigator.geolocation.watchPosition(
      async (pos) => {
        setGeo("granted");
        if (Date.now() - last.current < 10000) return;
        last.current = Date.now();
        try {
          const res = await api.saveLocation(journeyId, pos.coords.latitude, pos.coords.longitude);
          saved.current(res.journey);
        } catch {
          /* a failed location upload must never interrupt the safety flow */
        }
      },
      (err) => setGeo(err.code === 1 ? "denied" : "unavailable"),
      { enableHighAccuracy: true, maximumAge: 10000, timeout: 20000 }
    );
    return () => navigator.geolocation.clearWatch(watchId);
  }, [journeyId, enabled]);

  return geo;
}
