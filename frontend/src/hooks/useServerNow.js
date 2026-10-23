import { useEffect, useState } from "react";

/** Current time in ms, corrected by the offset between server and browser clocks. */
export function useServerNow(offsetMs) {
  const [now, setNow] = useState(() => Date.now() + offsetMs);
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now() + offsetMs), 250);
    return () => clearInterval(id);
  }, [offsetMs]);
  return now;
}
