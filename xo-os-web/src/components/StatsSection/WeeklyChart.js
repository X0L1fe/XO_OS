import React, { useEffect, useMemo, useState } from "react";

export default function WeeklyChart({ refreshKey = 0 }) {
  const [weeks, setWeeks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadWeeklyStats = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/stats/weekly",
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setWeeks(
          Array.isArray(data)
            ? data.map((week) => ({
                ...week,
                hours: Number(week.hours) || 0,
              }))
            : []
        );
      } catch (err) {
        console.error(
          "Failed to fetch weekly stats:",
          err
        );

        setError(
          err.message ||
            "Не удалось загрузить статистику"
        );
      } finally {
        setLoading(false);
      }
    };

    loadWeeklyStats();
  }, [refreshKey]);

  const maxHours = useMemo(() => {
    return Math.max(
      ...weeks.map((week) => week.hours),
      1
    );
  }, [weeks]);

  const totalHours = useMemo(() => {
    return weeks.reduce(
      (sum, week) => sum + week.hours,
      0
    );
  }, [weeks]);

  if (loading) {
    return (
      <div className="flex h-[300px] items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <StatsMessage
        title="Не удалось загрузить динамику"
        description={error}
      />
    );
  }

  if (weeks.length === 0) {
    return (
      <StatsMessage
        title="Нет недель для отображения"
        description="После применения фильтров данные отсутствуют."
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-2 gap-3">
        <Metric
          label="Часов"
          value={`${formatNumber(totalHours)} ч`}
        />

        <Metric
          label="Недели"
          value={weeks.length}
        />
      </div>

      {/* Chart */}
      <div className="overflow-x-auto rounded-xl border border-border bg-background/40">
        <div
          className="min-w-[720px] p-4"
          style={{
            minHeight: 310,
          }}
        >
          <div className="relative h-[250px]">
            {/* Grid */}
            <div className="pointer-events-none absolute inset-0 flex flex-col justify-between">
              {[0, 1, 2, 3, 4].map((line) => (
                <div
                  key={line}
                  className="h-px w-full bg-border/40"
                />
              ))}
            </div>

            {/* Y axis max */}
            <div className="pointer-events-none absolute -left-1 top-0 -translate-x-full pr-2 text-[10px] font-mono text-text-muted">
              {formatNumber(maxHours)}ч
            </div>

            {/* Bars */}
            <div className="absolute inset-0 flex items-stretch gap-2">
              {weeks.map((week) => {
                const height =
                  week.hours > 0
                    ? Math.max(
                        (week.hours / maxHours) *
                          100,
                        5
                      )
                    : 2;

                const isFuture =
                  new Date(`${week.date_start.split(".").reverse().join("-")}T00:00:00`) >
                  new Date();

                const isCurrent =
                  week.current === true;

                return (
                  <div
                    key={week.week}
                    className="group relative flex flex-1 flex-col justify-end"
                    title={`Неделя ${week.week}: ${formatNumber(
                      week.hours
                    )} ч`}
                  >
                    {/* Value */}
                    {week.hours > 0 && (
                      <div className="mb-2 text-center font-mono text-[10px] text-text-secondary opacity-0 transition-opacity group-hover:opacity-100">
                        {formatNumber(week.hours)}
                      </div>
                    )}

                    {/* Bar */}
                    <div
                      className={`
                        mx-auto
                        w-full
                        max-w-[34px]
                        rounded-t-md
                        transition-all
                        duration-300
                        ${
                          isCurrent
                            ? "bg-accent-blue shadow-[0_0_18px_rgba(22,131,255,0.18)]"
                            : isFuture
                              ? "bg-accent-blue/10"
                              : "bg-accent-blue/40"
                        }
                        group-hover:bg-accent-blue
                      `}
                      style={{
                        height: `${height}%`,
                      }}
                    />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Labels */}
          <div className="mt-3 flex gap-2 border-t border-border/50 pt-3">
            {weeks.map((week) => {
              const showLabel =
                weeks.length <= 12 ||
                week.week % 2 === 1 ||
                week.current;

              return (
                <div
                  key={`label-${week.week}`}
                  className="flex-1 text-center"
                >
                  {showLabel && (
                    <>
                      <div
                        className={`font-mono text-[10px] ${
                          week.current
                            ? "font-semibold text-accent-blue"
                            : "text-text-muted"
                        }`}
                      >
                        {week.week}
                      </div>

                      <div className="mt-0.5 text-[9px] text-text-muted">
                        {week.date_start}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-text-muted">
        <Legend
          className="bg-accent-blue"
          label="Текущая неделя"
        />

        <Legend
          className="bg-accent-blue/40"
          label="Прошедшие недели"
        />

        <Legend
          className="bg-accent-blue/10"
          label="Предстоящие"
        />
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-border bg-background/50 px-4 py-3">
      <p className="text-[10px] uppercase tracking-wide text-text-muted">
        {label}
      </p>

      <p className="mt-1 font-mono text-lg font-semibold text-text-primary">
        {value}
      </p>
    </div>
  );
}

function Legend({ className, label }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`h-2 w-2 rounded-sm ${className}`}
      />

      <span>{label}</span>
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