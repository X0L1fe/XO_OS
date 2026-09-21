import React, { useEffect, useState } from "react";

export default function WeeklyChart() {
  const [weeks, setWeeks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadWeeklyStats = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/stats/weekly", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setWeeks(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch weekly stats:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadWeeklyStats();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[220px] items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[220px] flex-col items-center justify-center text-center">
        <p className="text-sm text-text-secondary">
          Ошибка загрузки данных
        </p>

        <p className="mt-1 text-xs text-text-muted">
          {error}
        </p>
      </div>
    );
  }

  if (weeks.length === 0) {
    return (
      <div className="flex h-[220px] items-center justify-center">
        <p className="text-sm text-text-secondary">
          Нет данных за недели
        </p>
      </div>
    );
  }

  const normalizedWeeks = weeks.map((week, index) => ({
    ...week,
    hours: Number(week.hours) || 0,
    label: week.label ?? `${index + 1}`,
  }));

  const maxHours = Math.max(
    ...normalizedWeeks.map((week) => week.hours),
    1
  );

  return (
    <div className="space-y-3">
      {/* Chart */}
      <div className="relative h-[220px] rounded-lg border border-border bg-card px-4 pt-4">
        {/* Grid */}
        <div className="pointer-events-none absolute inset-4 flex flex-col justify-between">
          <GridLine />
          <GridLine />
          <GridLine />
          <GridLine />
          <GridLine />
        </div>

        {/* Bars */}
        <div className="absolute inset-x-4 bottom-4 top-4 flex items-end gap-2">
          {normalizedWeeks.map((week, index) => {
            const height =
              week.hours === 0
                ? 4
                : Math.max((week.hours / maxHours) * 100, 8);

            const isCurrent =
              week.current === true ||
              (week.current === undefined &&
                index === normalizedWeeks.length - 1);

            return (
              <div
                key={`${week.label}-${index}`}
                className="group flex h-full flex-1 items-end"
                title={`${week.label}: ${week.hours} ч`}
              >
                <div className="flex h-full w-full items-end justify-center">
                  <div
                    className={`
                      w-full max-w-[34px] rounded-t-md
                      transition-all duration-200
                      ${
                        isCurrent
                          ? "bg-accent-blue"
                          : "bg-accent-blue/40"
                      }
                      group-hover:bg-accent-blue
                    `}
                    style={{ height: `${height}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Axis labels */}
      <div className="flex gap-2 px-4">
        {normalizedWeeks.map((week, index) => (
          <div
            key={`${week.label}-label-${index}`}
            className="flex-1 text-center"
          >
            <div className="text-[11px] text-text-muted">
              {week.label}
            </div>

            <div className="mt-1 font-mono text-[11px] text-text-secondary">
              {week.hours}
            </div>
          </div>
        ))}
      </div>

      <div className="text-right text-[11px] uppercase tracking-wider text-text-muted">
        часы
      </div>
    </div>
  );
}

function GridLine() {
  return (
    <div className="h-px w-full bg-border/40" />
  );
}