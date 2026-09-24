import React, { useEffect, useMemo, useState } from "react";
import {
  FiArrowDown,
  FiArrowUp,
  FiClock,
} from "react-icons/fi";

export default function PlanFact({ refreshKey = 0 }) {
  const [data, setData] = useState({
    total: 0,
    completed: 0,
    remaining: 0,
    progress_percent: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadProgress = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/stats/planfact",
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();

        setData({
          total: Number(result.total) || 0,
          completed:
            Number(result.completed) || 0,
          remaining:
            Number(result.remaining) || 0,
          progress_percent:
            Number(result.progress_percent) || 0,
        });
      } catch (err) {
        console.error(
          "Failed to fetch semester progress:",
          err
        );

        setError(
          err.message ||
            "Не удалось загрузить прогресс"
        );
      } finally {
        setLoading(false);
      }
    };

    loadProgress();
  }, [refreshKey]);

  const progress = useMemo(() => {
    return Math.min(
      Math.max(data.progress_percent, 0),
      100
    );
  }, [data.progress_percent]);

  if (loading) {
    return (
      <div className="flex min-h-[240px] items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[240px] items-center justify-center text-center">
        <div>
          <p className="text-sm text-text-primary">
            Не удалось загрузить прогресс
          </p>

          <p className="mt-2 text-xs text-text-muted">
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (data.total <= 0) {
    return (
      <div className="flex min-h-[240px] items-center justify-center text-center">
        <div>
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-background text-text-muted">
            <FiClock className="h-4 w-4" />
          </div>

          <p className="mt-3 text-sm font-medium text-text-primary">
            Нет данных о нагрузке
          </p>

          <p className="mx-auto mt-2 max-w-sm text-xs leading-5 text-text-muted">
            После применения фильтров в текущем семестре
            нет занятий.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Progress header */}
      <div className="rounded-xl border border-border bg-background/40 p-5">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-[10px] uppercase tracking-[0.16em] text-text-muted">
              Прогресс
            </p>

            <p className="mt-1 font-mono text-3xl font-bold text-text-primary">
              {progress.toFixed(0)}%
            </p>
          </div>

          <p className="font-mono text-xs text-text-muted">
            {formatNumber(data.total)} ч всего
          </p>
        </div>

        <div className="mt-5 h-3 overflow-hidden rounded-full bg-card">
          <div
            className="h-full rounded-full bg-accent-blue shadow-[0_0_18px_rgba(22,131,255,0.18)] transition-all duration-700"
            style={{
              width: `${progress}%`,
            }}
          />
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <ProgressCard
          icon={<FiCheck className="h-4 w-4" />}
          label="Прошло"
          value={`${formatNumber(
            data.completed
          )} ч`}
          tone="blue"
        />

        <ProgressCard
          icon={<FiArrowUp className="h-4 w-4" />}
          label="Впереди"
          value={`${formatNumber(
            data.remaining
          )} ч`}
          tone="yellow"
        />

        <ProgressCard
          icon={<FiClock className="h-4 w-4" />}
          label="Всего"
          value={`${formatNumber(
            data.total
          )} ч`}
          tone="green"
        />
      </div>
    </div>
  );
}

function ProgressCard({
  icon,
  label,
  value,
  tone,
}) {
  const toneClasses = {
    blue: {
      icon: "border-accent-blue/20 bg-accent-blue/10 text-accent-blue",
    },
    yellow: {
      icon: "border-accent-yellow/20 bg-accent-yellow/10 text-accent-yellow",
    },
    green: {
      icon: "border-accent-green/20 bg-accent-green/10 text-accent-green",
    },
  };

  const palette =
    toneClasses[tone] || toneClasses.blue;

  return (
    <div className="rounded-xl border border-border bg-background/40 p-4">
      <div
        className={`flex h-8 w-8 items-center justify-center rounded-lg border ${palette.icon}`}
      >
        {icon}
      </div>

      <p className="mt-4 text-[10px] uppercase tracking-[0.14em] text-text-muted">
        {label}
      </p>

      <p className="mt-1 font-mono text-lg font-semibold text-text-primary">
        {value}
      </p>
    </div>
  );
}

function formatNumber(value) {
  return Number(value).toLocaleString("ru-RU", {
    maximumFractionDigits: 1,
  });
}

function FiCheck({ className }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className={className}
    >
      <path d="m5 12 4 4L19 6" />
    </svg>
  );
}