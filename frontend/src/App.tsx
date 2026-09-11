import { useCallback, useEffect, useState } from "react";

type Category =
  | "visitor"
  | "package_delivery"
  | "loitering"
  | "fall_suspected"
  | "ambient_noise"
  | "unknown";

type AlertLevel = "critical" | "high" | "none";

interface Analysis {
  category: Category;
  confidence: number;
  summary: string;
  offline: boolean;
}

interface DoorstepEvent {
  event_id: string;
  occurred_at: string;
  analysis: Analysis;
  snapshot_ref: string | null;
  alert_level: AlertLevel;
  alert_reason: string;
  acknowledged: boolean;
}

interface CareDigest {
  date: string;
  text: string;
  anomaly: string | null;
  offline: boolean;
}

const CATEGORY_META: Record<Category, { icon: string; label: string }> = {
  visitor: { icon: "👋", label: "Visitor" },
  package_delivery: { icon: "📦", label: "Package" },
  loitering: { icon: "👀", label: "Loitering" },
  fall_suspected: { icon: "🚨", label: "Fall suspected" },
  ambient_noise: { icon: "🌿", label: "Ambient" },
  unknown: { icon: "❔", label: "Unclassified" },
};

const DEMO_SCENARIOS: { scenario: Category | string; label: string }[] = [
  { scenario: "visitor", label: "👋 Visitor" },
  { scenario: "package_delivery", label: "📦 Package" },
  { scenario: "loitering", label: "👀 Loitering" },
  { scenario: "fall_suspected", label: "🚨 Fall" },
  { scenario: "ambient_noise", label: "🌿 Noise" },
];

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, init);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

export default function App() {
  const [events, setEvents] = useState<DoorstepEvent[]>([]);
  const [digest, setDigest] = useState<CareDigest | null>(null);
  const [backendUp, setBackendUp] = useState(false);
  const [triggering, setTriggering] = useState<string | null>(null);
  const [showDemo, setShowDemo] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [events, digest] = await Promise.all([
        api<DoorstepEvent[]>("/events"),
        api<CareDigest>("/digest/today"),
      ]);
      setEvents(events);
      setDigest(digest);
      setBackendUp(true);
    } catch {
      setBackendUp(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 10_000);
    return () => clearInterval(timer);
  }, [refresh]);

  const openAlert = events.find(
    (e) => e.alert_level !== "none" && !e.acknowledged,
  );

  const trigger = async (scenario: string) => {
    setTriggering(scenario);
    try {
      await api(`/dev/simulate?scenario=${scenario}`, { method: "POST" });
      await refresh();
    } catch {
      /* banner shows backend state */
    } finally {
      setTriggering(null);
    }
  };

  const ack = async (eventId: string) => {
    try {
      await api(`/alerts/${eventId}/ack`, { method: "POST" });
      await refresh();
    } catch {
      /* ignore */
    }
  };

  return (
    <main className="shell">
      {openAlert && (
        <div className={`banner ${openAlert.alert_level}`} role="alert">
          <div className="banner-title">
            {openAlert.alert_level === "critical" ? "🚨 Act now" : "⚠️ Needs attention"}
            <span className="banner-when">
              {new Date(openAlert.occurred_at).toLocaleTimeString()}
            </span>
          </div>
          <p>{openAlert.alert_reason}</p>
          <button className="btn primary" onClick={() => ack(openAlert.event_id)}>
            I've checked — calm down
          </button>
        </div>
      )}

      <header>
        <h1>
          <span aria-hidden>🏮</span> PorchLight
        </h1>
        <p className="tagline">The porch light stays on — for Mom and Dad.</p>
        <p className={`backend ${backendUp ? "ok" : "down"}`}>
          {backendUp ? "● connected to home" : "○ backend not reachable (start backend on :8000)"}
        </p>
      </header>

      <section className="digest">
        <h2>Today at the door</h2>
        {digest ? (
          <>
            <p className="digest-text">{digest.text}</p>
            {digest.anomaly && <p className="anomaly">⚠ {digest.anomaly}</p>}
          </>
        ) : (
          <p className="muted">Loading…</p>
        )}
      </section>

      <section className="events">
        <h2>Recent doorstep activity</h2>
        {events.length === 0 ? (
          <p className="muted">
            No events yet — trigger one below, or push from the Ring sandbox.
          </p>
        ) : (
          <ul>
            {events.map((event) => {
              const meta = CATEGORY_META[event.analysis.category] ?? CATEGORY_META.unknown;
              return (
                <li
                  key={event.event_id}
                  className={`event ${event.alert_level !== "none" ? "alerted" : ""}`}
                >
                  {event.snapshot_ref ? (
                    <img
                      className="thumb"
                      src={`/api/snapshots/${event.event_id}`}
                      alt={`${meta.label} at the doorstep`}
                    />
                  ) : (
                    <span className="icon" aria-hidden>
                      {meta.icon}
                    </span>
                  )}
                  <span className="body">
                    <strong>{meta.label}</strong>
                    <span className="summary">{event.analysis.summary}</span>
                    {event.alert_level !== "none" && !event.acknowledged && (
                      <button className="btn small" onClick={() => ack(event.event_id)}>
                        Acknowledge {event.alert_level === "critical" ? "🚨" : "⚠️"}
                      </button>
                    )}
                  </span>
                  <time>{new Date(event.occurred_at).toLocaleTimeString()}</time>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section className="demo">
        <button className="linklike" onClick={() => setShowDemo(!showDemo)}>
          {showDemo ? "▾" : "▸"} Try a test event <span className="muted">(dev)</span>
        </button>
        {showDemo && (
          <div className="demo-strip">
            {DEMO_SCENARIOS.map(({ scenario, label }) => (
              <button
                key={scenario}
                className="btn"
                disabled={!backendUp || triggering !== null}
                onClick={() => trigger(scenario)}
              >
                {triggering === scenario ? "…" : label}
              </button>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
