/** Neumorphic countdown dial: raised outer disc, inset groove, progress arc. */
export default function Ring({ remaining, total, tone = "calm", label, sub }) {
  const r = 88;
  const c = 2 * Math.PI * r;
  const frac = total > 0 ? Math.max(0, Math.min(1, remaining / total)) : 0;
  return (
    <div className="ring" role="timer" aria-label={`${label} ${sub}`}>
      <svg viewBox="0 0 220 220" aria-hidden="true">
        <circle className="ring-track" cx="110" cy="110" r={r} />
        <circle
          className={`ring-bar ${tone}`}
          cx="110"
          cy="110"
          r={r}
          strokeDasharray={c}
          strokeDashoffset={c * (1 - frac)}
          transform="rotate(-90 110 110)"
        />
      </svg>
      <div className="ring-center">
        <strong>{label}</strong>
        <span>{sub}</span>
      </div>
    </div>
  );
}
