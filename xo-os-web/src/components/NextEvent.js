import React, { useEffect, useState } from "react";
import {
  FiCalendar,
  FiMapPin,
  FiUser,
  FiArrowRight,
} from "react-icons/fi";

export default function NextEvent() {
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadNextEvent = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/schedule", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const schedule = await response.json();

        if (Array.isArray(schedule) && schedule.length > 0) {
          setEvent(schedule[0]);
        } else {
          setEvent(null);
        }
      } catch (err) {
        console.error("Failed to fetch next event:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadNextEvent();
  }, []);

  if (loading) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <div className="flex min-h-[120px] items-center justify-center">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <div className="flex min-h-[120px] flex-col items-center justify-center text-center">
          <p className="text-sm text-text-secondary">
            Не удалось загрузить следующее событие
          </p>

          <p className="mt-1 text-xs text-text-muted">
            {error}
          </p>
        </div>
      </section>
    );
  }

  if (!event) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <div className="flex min-h-[120px] flex-col items-center justify-center text-center">
          <FiCalendar className="h-6 w-6 text-text-muted" />

          <p className="mt-3 text-sm font-medium text-text-primary">
            Больше событий нет
          </p>

          <p className="mt-1 text-xs text-text-muted">
            На ближайшее время ничего не запланировано
          </p>
        </div>
      </section>
    );
  }

  const getTypeColor = (type) => {
    switch (type) {
      case "LECTURE":
        return "bg-accent-blue";

      case "PRACTICE":
        return "bg-accent-purple";

      case "LAB":
        return "bg-accent-yellow";

      case "EXAM":
        return "bg-accent-red";

      default:
        return "bg-text-secondary";
    }
  };

  return (
    <section className="rounded-xl border border-border bg-panel p-5 transition-colors duration-180 hover:border-border/80 hover:bg-card">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${getTypeColor(
              event.type
            )}`}
          />

          <h2 className="text-sm font-semibold uppercase tracking-[0.08em] text-text-secondary">
            Следующее событие
          </h2>
        </div>

        <span className="font-mono text-xs text-text-muted">
          {event.time || "--:--"}
        </span>
      </div>

      {/* Subject */}
      <div className="mt-4">
        <h3 className="text-lg font-bold text-text-primary">
          {event.subject || "Без названия"}
        </h3>
      </div>

      {/* Meta */}
      <div className="mt-4 space-y-2">
        {event.room && (
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <FiMapPin className="h-4 w-4 text-text-muted" />

            <span>{event.room}</span>
          </div>
        )}

        {event.teacher && (
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <FiUser className="h-4 w-4 text-text-muted" />

            <span className="truncate">
              {event.teacher}
            </span>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-5 flex items-center justify-between border-t border-border/60 pt-4">
        <div className="flex items-center gap-2">
          <FiCalendar className="h-4 w-4 text-text-muted" />

          <span className="text-xs text-text-secondary">
            {event.type === "LECTURE"
              ? "Лекция"
              : event.type === "PRACTICE"
              ? "Практика"
              : event.type === "LAB"
              ? "Лабораторная"
              : event.type === "EXAM"
              ? "Экзамен"
              : "Занятие"}
          </span>
        </div>

        <FiArrowRight className="h-4 w-4 text-accent-blue" />
      </div>
    </section>
  );
}