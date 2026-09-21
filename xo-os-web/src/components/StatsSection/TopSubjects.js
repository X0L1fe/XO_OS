import React, { useEffect, useState } from "react";

export default function TopSubjects() {
  const [subjects, setSubjects] = useState([]);
  const [mode, setMode] = useState("hours");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadSubjects = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/stats/topsubjects", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setSubjects(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch top subjects:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadSubjects();
  }, []);

  const getValue = (subject) => {
    const hours = Number(subject.hours) || 0;

    switch (mode) {
      case "lessons":
        return Math.round(hours / 1.5);

      case "xp":
        return Math.round(hours * 10);

      case "tasks":
        return Math.round(hours / 2);

      default:
        return hours;
    }
  };

  if (loading) {
    return (
      <div className="flex h-full min-h-[220px] items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[220px] flex-col items-center justify-center text-center">
        <p className="text-sm text-text-secondary">
          Ошибка загрузки данных
        </p>

        <p className="mt-1 text-xs text-text-muted">
          {error}
        </p>
      </div>
    );
  }

  if (subjects.length === 0) {
    return (
      <div className="flex min-h-[220px] items-center justify-center">
        <p className="text-sm text-text-secondary">
          Нет данных по предметам
        </p>
      </div>
    );
  }

  const values = subjects.map(getValue);
  const maxValue = Math.max(...values, 1);

  const modes = [
    { id: "hours", label: "Часы" },
    { id: "lessons", label: "Занятия" },
    { id: "xp", label: "XP" },
    { id: "tasks", label: "Задачи" },
  ];

  return (
    <div className="space-y-5">
      {/* Segmented control */}
      <div className="inline-flex rounded-lg border border-border bg-background p-1">
        {modes.map((item) => {
          const active = mode === item.id;

          return (
            <button
              key={item.id}
              type="button"
              onClick={() => setMode(item.id)}
              className={`
                rounded-md px-3 py-1.5 text-xs font-medium
                transition-all duration-180
                ${
                  active
                    ? "bg-accent-blue text-white shadow-[0_0_14px_rgba(22,131,255,0.16)]"
                    : "text-text-secondary hover:bg-card hover:text-text-primary"
                }
              `}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      {/* Subjects */}
      <div className="space-y-3">
        {subjects.map((subject, index) => {
          const value = getValue(subject);
          const percentage =
            maxValue > 0 ? (value / maxValue) * 100 : 0;

          return (
            <div
              key={subject.name || index}
              className="group rounded-lg border border-border/60 bg-card/60 px-3 py-3 transition-colors duration-180 hover:border-border hover:bg-card"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[11px] text-text-muted">
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    <span className="truncate text-sm font-medium text-text-primary">
                      {subject.name}
                    </span>
                  </div>
                </div>

                <span className="shrink-0 font-mono text-sm text-text-secondary">
                  {value}
                  {mode === "hours" ? " ч" : ""}
                </span>
              </div>

              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-background">
                <div
                  className="h-full rounded-full bg-accent-blue transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}