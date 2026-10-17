import React, { useEffect, useMemo, useState } from "react";
import { useFiltersRefreshKey } from "../../hooks/useFiltersRefreshKey";

const COLORS = {
  lecture: "#1683FF",
  practice: "#FFC83D",
  lab: "#35D07F",
  other: "#6B7280",
  track: "#10243A",
};

export default function DonutChart({ refreshKey = 0, mode = "compact" }) {
  const filtersKey = useFiltersRefreshKey();
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
        const response = await fetch("/api/stats/semester", {
          credentials: "include",
        });

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
          lessonCount: Number(result.lesson_count) || 0,
        });
      } catch (err) {
        console.error("Failed to fetch semester stats:", err);
        setError(err.message || "Не удалось загрузить статистику");
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, [refreshKey, filtersKey]);

  // ------------------------------------------------------------
  // Сегменты + предрасчёт дуг (не зависит от mode)
  // ------------------------------------------------------------
  const arcs = useMemo(() => {
    const base = [
      { key: "lecture", label: "Лекции", value: data.lecture, color: COLORS.lecture },
      { key: "practice", label: "Практики", value: data.practice, color: COLORS.practice },
      { key: "lab", label: "Лабораторные", value: data.lab, color: COLORS.lab },
    ];

    if (data.other > 0) {
      base.push({ key: "other", label: "Другие", value: data.other, color: COLORS.other });
    }

    let cumulative = 0;

    return base.map((segment) => {
      const percentage =
        data.total > 0 ? (segment.value / data.total) * 100 : 0;

      const offset = cumulative;
      cumulative += percentage;

      return { ...segment, percentage, offset };
    });
  }, [data]);

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

  return mode === "full" ? (
    <FullView data={data} arcs={arcs} />
  ) : (
    <CompactView data={data} arcs={arcs} />
  );
}

/* ================================================================
 * COMPACT (для дашборда)
 * ================================================================ */
function CompactView({ data, arcs }) {
  return (
    <div className="space-y-4">
      {/* ROW 1: 3 карточки во всю ширину */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {arcs.map((segment) => (
          <div
            key={segment.key}
            className="
              min-w-0 overflow-hidden rounded-xl border border-border
              bg-background/50 p-4 transition-colors hover:bg-background
            "
          >
            <div className="flex min-w-0 items-center gap-2">
              <span
                className="h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ backgroundColor: segment.color }}
              />

              <span className="min-w-0 text-xs font-semibold text-text-secondary">
                {segment.label}
              </span>
            </div>

            <div className="mt-3 flex items-baseline justify-between gap-3">
              <div className="flex items-baseline gap-1">
                <span className="font-mono text-xl font-semibold text-text-primary">
                  {formatNumber(segment.value)}
                </span>
                <span className="text-[11px] text-text-muted">ч</span>
              </div>

              <span
                className="shrink-0 font-mono text-[11px] tabular-nums text-text-muted"
                title={`${segment.percentage.toFixed(1)}%`}
              >
                {segment.percentage.toFixed(0)}%
              </span>
            </div>

            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-card">
              <div
                className="h-full max-w-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(segment.percentage, 100)}%`,
                  backgroundColor: segment.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* ROW 2: донат + общая нагрузка */}
      <div className="grid items-center gap-6 lg:grid-cols-[240px_minmax(0,1fr)]">
        <div className="flex justify-center">
          <Donut data={data} arcs={arcs} size={220} />
        </div>

        <div className="min-w-0 overflow-hidden rounded-xl border border-border bg-background/50 p-4">
          <div className="flex min-w-0 items-center justify-between gap-4">
            <span className="text-xs text-text-muted">Общая нагрузка</span>

            <span className="shrink-0 whitespace-nowrap font-mono text-sm font-semibold text-text-primary">
              {formatNumber(data.total)} ч
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
 * FULL (для страницы «Статистика»)
 * ================================================================ */
function FullView({ data, arcs }) {
  return (
    <div className="space-y-6">
      <div className="grid items-center gap-8 lg:grid-cols-[minmax(0,300px)_minmax(0,1fr)]">
        {/* Крупный донат */}
        <div className="flex justify-center">
          <Donut data={data} arcs={arcs} size={280} />
        </div>

        {/* Легенда-список */}
        <div className="space-y-5">
          {arcs.map((segment) => (
            <div key={segment.key}>
              <div className="flex items-baseline justify-between gap-4">
                <div className="flex min-w-0 items-center gap-2.5">
                  <span
                    className="h-3 w-3 shrink-0 rounded-full"
                    style={{ backgroundColor: segment.color }}
                  />

                  <span className="min-w-0 truncate text-sm font-medium text-text-primary">
                    {segment.label}
                  </span>
                </div>

                <div className="flex shrink-0 items-baseline gap-3">
                  <span className="font-mono text-lg font-semibold text-text-primary">
                    {formatNumber(segment.value)}
                  </span>

                  <span className="text-xs text-text-muted">ч</span>

                  <span
                    className="min-w-[40px] text-right font-mono text-xs tabular-nums text-text-muted"
                    title={`${segment.percentage.toFixed(1)}%`}
                  >
                    {segment.percentage.toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-card">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(segment.percentage, 100)}%`,
                    backgroundColor: segment.color,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Нижний блок: нагрузка + всего занятий */}
      <div className="grid gap-4 rounded-xl border border-border bg-background/50 p-5 sm:grid-cols-2">
        <div className="flex items-center justify-between gap-4">
          <span className="text-sm text-text-muted">Общая нагрузка</span>

          <span className="font-mono text-lg font-semibold text-text-primary">
            {formatNumber(data.total)} ч
          </span>
        </div>

        <div className="flex items-center justify-between gap-4 sm:border-l sm:border-border/60 sm:pl-5">
          <span className="text-sm text-text-muted">Всего занятий</span>

          <span className="font-mono text-lg font-semibold text-text-primary">
            {data.lessonCount}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
 * Общий донат
 * ================================================================ */
function Donut({ data, arcs, size }) {
  const strokeWidth = size >= 260 ? 4 : 4.5;

  return (
    <div
      className="relative"
      style={{ width: size, height: size }}
    >
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
          strokeWidth={strokeWidth}
          pathLength="100"
        />

        {arcs.map((segment) => (
          <circle
            key={segment.key}
            cx="18"
            cy="18"
            r="15.5"
            fill="none"
            stroke={segment.color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${segment.percentage} ${100 - segment.percentage}`}
            strokeDashoffset={-segment.offset}
            strokeLinecap="butt"
            pathLength="100"
            transform="rotate(-90 18 18)"
          />
        ))}
      </svg>

      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
        <span
          className={`font-mono font-bold tracking-tight text-text-primary ${size >= 260 ? "text-4xl" : "text-3xl"
            }`}
        >
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
  );
}

function StatsMessage({ title, description }) {
  return (
    <div className="flex min-h-[240px] items-center justify-center">
      <div className="max-w-md text-center">
        <p className="text-sm font-medium text-text-primary">{title}</p>
        <p className="mt-2 text-xs leading-5 text-text-muted">{description}</p>
      </div>
    </div>
  );
}

function formatNumber(value) {
  return Number(value).toLocaleString("ru-RU", {
    maximumFractionDigits: 1,
  });
}