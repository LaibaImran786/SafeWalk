const BASE = import.meta.env.VITE_API_URL || "";

function describe(detail) {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`).join("; ");
  }
  return null;
}

async function request(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch(`${BASE}/api${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    const err = new Error("Cannot reach the SafeWalk server. Check that the backend is running.");
    err.status = 0;
    throw err;
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* empty body */
  }
  if (!res.ok) {
    const err = new Error(describe(data?.detail) || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}

const post = (path, body) => request(path, { method: "POST", body });

export const api = {
  createJourney: (data) => post("/journeys", data),
  getActive: () => request("/journeys/active"),
  saveLocation: (id, latitude, longitude) => post(`/journeys/${id}/location`, { latitude, longitude }),
  checkin: (id) => post(`/journeys/${id}/checkin`),
  missedCheckin: (id) => post(`/journeys/${id}/missed-checkin`),
  cancelAlert: (id) => post(`/journeys/${id}/cancel-alert`),
  sos: (id) => post(`/journeys/${id}/sos`),
  escalate: (id) => post(`/journeys/${id}/escalate`),
  end: (id) => post(`/journeys/${id}/end`),
  getAlerts: (id) => request(`/journeys/${id}/alerts`),
  briefing: (data) => post("/ai/briefing", data),
};
