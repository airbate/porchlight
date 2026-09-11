import { useCallback, useEffect, useState } from "react";

type Category =
  | "visitor"
  | "package_delivery"
  | "loitering"
  | "fall_suspected"
  | "ambient_noise"
  | "unknown";

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
  alerted: boolean;
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

async function api<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

export default function App() {
  const [events, setEvents] = useState<DoorstepEvent[]>([]);
  const [digest, setDigest] = useState<CareDigest | null>(null);
  const [backendUp, setBackendUp] = useState(false);

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

  return (
    <main className="shell">
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
            No events yet — try <code>POST /dev/simulate?scenario=visitor</code> on the backend.
          </p>
        ) : (
          <ul>
            {events.map((event) => {
              const meta = CATEGORY_META[event.analysis.category] ?? CATEGORY_META.unknown;
              return (
                <li key={event.event_id} className={`event ${event.alerted ? "alerted" : ""}`}>
                  <span className="icon" aria-hidden>
                    {meta.icon}
                  </span>
                  <span className="body">
                    <strong>{meta.label}</strong>
                    <span className="summary">{event.analysis.summary}</span>
                  </span>
                  <time>{new Date(event.occurred_at).toLocaleTimeString()}</time>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </main>
  );
}
