export function clock(seconds) {
  const s = Math.max(0, Math.ceil(seconds));
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, "0")}`;
}

export function when(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "medium" });
}

export function coords(j) {
  if (j.latitude == null || j.longitude == null) return null;
  return `${j.latitude.toFixed(5)}, ${j.longitude.toFixed(5)}`;
}

export const REASONS = { manual_sos: "Manual SOS", missed_checkin: "Missed check-in" };
export const ALERT_STATUS = {
  pending: "Pending",
  simulated: "Simulated",
  cancelled: "Cancelled",
  failed: "Failed",
};
