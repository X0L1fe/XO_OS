import React, { useEffect, useState } from "react";

const COLORS = {
  lecture: "#1683FF",
  practice: "#FFC83D",
  lab: "#35D07F",
  other: "#6B7280",
  track: "#10243A",
};

export default function DonutChart({ refreshKey = 0 }) {
  const [data, setData] = useState({
    lecture: 0,
    practice: 0,
    lab: 0,
    other: 0,
    total: 0,
    lessonCount: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/stats/semester",
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();

        setData({
          lecture: Number(result.lecture) || 0,
          practice: Number(result.practice) || 0,
          lab: Number(result.lab) || 0,
          other: Number(result.other) || 0,
          total: Number(result.total) || 0,
          lessonCount:
            Number(result.lesson_count) || 0,
        });
      } catch (err) {
        console.error(
          "Failed to fetch semester stats:",
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

    loadStats();
  }, [refreshKey]);

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
        title="Не удалось загрузить статистику"
        description={error}
      />
    );
  }

  if (data.total <= 0) {
    return (
      <StatsMessage
        title="Нет данных за семестр"
        description="После применения фильтров занятий для расчёта не осталось."
      />
    );
  }

  const segments = [
    {
      key: "lecture",
      label: "Лекции",
      value: data.lecture,
      color: COLORS.lecture,
    },
    {
      key: "practice",
      label: "Практики",
      value: data.practice,
      color: COLORS.practice,
    },
    {
      key: "lab",
      label: "Лабораторные",
      value: data.lab,
      color: COLORS.lab,
    },
    ...(data.other > 0
      ? [
          {
            key: "other",
            label: "Другие",
            value: data.other,
            color: COLORS.other,
          },
        ]
      : []),
  ];

  let offset = 0;

  return (
    <div className="grid items-center gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
      {/* DONUT */}
      <div className="flex justify-center">
        <div className="relative h-[220px] w-[220px]">
          <svg
            className="h-full w-full"
            viewBox="0 0 36 36"
            role="img"
            aria-label={`Нагрузка семестра: ${data.total} часов`}
          >
            <circle
              cx="18"
              cy="18"
              r="15.5"
              fill="none"
              stroke={COLORS.track}
              strokeWidth="4.5"
              pathLength="100"
            />

            {segments.map((segment) => {
              const percentage =
                data.total > 0
                  ? (segment.value / data.total) * 100
                  : 0;

              const currentOffset = offset;
              offset += percentage;

              return (
                <circle
                  key={segment.key}
                  cx="18"
                  cy="18"
                  r="15.5"
                  fill="none"
                  stroke={segment.color}
                  strokeWidth="4.5"
                  strokeDasharray={`${percentage} ${
                    100 - percentage
                  }`}
                  strokeDashoffset={-currentOffset}
                  strokeLinecap="butt"
                  pathLength="100"
                  transform="rotate(-90 18 18)"
                />
              );
            })}
          </svg>

          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="font-mono text-3xl font-bold tracking-tight text-text-primary">
              {formatNumber(data.total)}
            </span>

            <span className="mt-1 text-[11px] uppercase tracking-[0.18em] text-text-secondary">
              часов
            </span>

            <span className="mt-2 text-[10px] text-text-muted">
              {data.lessonCount} занятий
            </span>
          </div>
        </div>
      </div>

      {/* BREAKDOWN */}
      <div className="grid min-w-0 gap-3 sm:grid-cols-2">
        {segments.map((segment) => {
          const percentage =
            data.total > 0
              ? (segment.value / data.total) * 100
              : 0;

          return (
            <div
              key={segment.key}
              className="
                min-w-0
                overflow-hidden
                rounded-xl
                border
                border-border
                bg-background/50
                p-4
                transition-colors
                hover:bg-background
              "
            >
              <div className="flex min-w-0 items-start justify-between gap-2">
                <div className="flex min-w-0 items-center gap-2">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{
                      backgroundColor: segment.color,
                    }}
                  />

                  <span className="truncate text-xs font-semibold text-text-secondary">
                    {segment.label}
                  </span>
                </div>

                <span
                  className="shrink-0 whitespace-nowrap font-mono text-[11px] text-text-muted"
                  title={`${percentage.toFixed(1)}%`}
                >
                  {percentage.toFixed(0)}%
                </span>
              </div>

              <div className="mt-3 flex min-w-0 items-baseline gap-1">
                <span className="min-w-0 truncate font-mono text-xl font-semibold text-text-primary">
                  {formatNumber(segment.value)}
                </span>

                <span className="shrink-0 text-[11px] text-text-muted">
                  ч
                </span>
              </div>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-card">
                <div
                  className="h-full max-w-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(
                      percentage,
                      100
                    )}%`,
                    backgroundColor: segment.color,
                  }}
                />
              </div>
            </div>
          );
        })}

        {/* TOTAL */}
        <div className="min-w-0 overflow-hidden rounded-xl border border-border bg-background/50 p-4 sm:col-span-2">
          <div className="flex min-w-0 items-center justify-between gap-4">
            <span className="truncate text-xs text-text-muted">
              Общая нагрузка
            </span>

            <span className="shrink-0 whitespace-nowrap font-mono text-sm font-semibold text-text-primary">
              {formatNumber(data.total)} ч
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatsMessage({ title, description }) {
  return (
    <div className="flex min-h-[240px] items-center justify-center">
      <div className="max-w-md text-center">
        <p className="text-sm font-medium text-text-primary">
          {title}
        </p>

        <p className="mt-2 text-xs leading-5 text-text-muted">
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