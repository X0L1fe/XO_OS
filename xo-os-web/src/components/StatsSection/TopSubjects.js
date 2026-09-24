import React, { useEffect, useMemo, useState } from "react";

export default function TopSubjects({ refreshKey = 0 }) {
  const [subjects, setSubjects] = useState([]);
  const [mode, setMode] = useState("hours");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadSubjects = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/stats/topsubjects",
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setSubjects(
          Array.isArray(data)
            ? data.map((subject) => ({
                ...subject,
                hours:
                  Number(subject.hours) || 0,
                lessons:
                  Number(subject.lessons) || 0,
              }))
            : []
        );
      } catch (err) {
        console.error(
          "Failed to fetch top subjects:",
          err
        );

        setError(
          err.message ||
            "Не удалось загрузить предметы"
        );
      } finally {
        setLoading(false);
      }
    };

    loadSubjects();
  }, [refreshKey]);

  const values = useMemo(() => {
    return subjects.map((subject) =>
      mode === "lessons"
        ? subject.lessons
        : subject.hours
    );
  }, [subjects, mode]);

  const maxValue = Math.max(...values, 1);

  if (loading) {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <StatsMessage
        title="Не удалось загрузить предметы"
        description={error}
      />
    );
  }

  if (subjects.length === 0) {
    return (
      <StatsMessage
        title="Нет данных по предметам"
        description="После применения фильтров предметов для анализа не осталось."
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between gap-3">
        <div className="text-[11px] text-text-muted">
          Топ-5 по нагрузке
        </div>

        <div className="inline-flex rounded-lg border border-border bg-background p-1">
          <button
            type="button"
            onClick={() => setMode("hours")}
            className={`
              rounded-md
              px-3
              py-1.5
              text-[11px]
              font-medium
              transition-all
              duration-180
              ${
                mode === "hours"
                  ? "bg-accent-blue text-white"
                  : "text-text-secondary hover:bg-card hover:text-text-primary"
              }
            `}
          >
            Часы
          </button>

          <button
            type="button"
            onClick={() => setMode("lessons")}
            className={`
              rounded-md
              px-3
              py-1.5
              text-[11px]
              font-medium
              transition-all
              duration-180
              ${
                mode === "lessons"
                  ? "bg-accent-blue text-white"
                  : "text-text-secondary hover:bg-card hover:text-text-primary"
              }
            `}
          >
            Занятия
          </button>
        </div>
      </div>

      {/* Subjects */}
      <div className="space-y-2.5">
        {subjects.map((subject, index) => {
          const value =
            mode === "lessons"
              ? subject.lessons
              : subject.hours;

          const percentage =
            maxValue > 0
              ? (value / maxValue) * 100
              : 0;

          return (
            <div
              key={subject.name || index}
              className="rounded-xl border border-border/70 bg-background/40 px-3.5 py-3 transition-colors hover:border-border hover:bg-background/70"
            >
              <div className="flex items-center gap-3">
                <span className="w-5 shrink-0 text-center font-mono text-[10px] text-text-muted">
                  {String(index + 1).padStart(
                    2,
                    "0"
                  )}
                </span>

                <div className="min-w-0 flex-1">
                  <p
                    className="truncate text-xs font-medium text-text-primary"
                    title={subject.name}
                  >
                    {subject.name}
                  </p>

                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-card">
                    <div
                      className="h-full rounded-full bg-accent-blue transition-all duration-500"
                      style={{
                        width: `${percentage}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="w-16 shrink-0 text-right">
                  <p className="font-mono text-xs font-semibold text-text-primary">
                    {formatNumber(value)}
                    {mode === "hours" ? " ч" : ""}
                  </p>

                  <p className="mt-0.5 text-[9px] text-text-muted">
                    {mode === "hours"
                      ? `${subject.lessons} занятий`
                      : `${formatNumber(
                          subject.hours
                        )} ч`}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatsMessage({ title, description }) {
  return (
    <div className="flex min-h-[240px] items-center justify-center text-center">
      <div>
        <p className="text-sm font-medium text-text-primary">
          {title}
        </p>

        <p className="mt-2 max-w-sm text-xs leading-5 text-text-muted">
          {description}
        </p>
      </div>
    </div>
  );
}

function formatNumber(value) {
  return Number(value).toLocaleString("ru-RU", {
    maximumFractionDigits: 1,
  });
}