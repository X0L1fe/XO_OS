import React, { useEffect, useState } from "react";

const COLORS = {
  lecture: "#1683FF",
  practice: "#8F5BFF",
  lab: "#FFC83D",
  track: "#12304A",
};

export default function DonutChart() {
  const [data, setData] = useState({
    lecture: 0,
    practice: 0,
    lab: 0,
    total: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadSemesterStats = async () => {
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
          total: Number(result.total) || 0,
        });
      } catch (err) {
        console.error("Failed to fetch semester stats:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadSemesterStats();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[220px] items-center justify-center">
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

  const total = data.total;
  const lecture = data.lecture;
  const practice = data.practice;
  const lab = data.lab;

  if (total === 0) {
    return (
      <div className="flex min-h-[220px] items-center justify-center">
        <p className="text-sm text-text-secondary">
          Нет данных за семестр
        </p>
      </div>
    );
  }

  const lecturePct = (lecture / total) * 100;
  const practicePct = (practice / total) * 100;
  const labPct = (lab / total) * 100;

  const segments = [
    {
      value: lecturePct,
      color: COLORS.lecture,
    },
    {
      value: practicePct,
      color: COLORS.practice,
    },
    {
      value: labPct,
      color: COLORS.lab,
    },
  ];

  let offset = 0;

  return (
    <div className="flex flex-col items-center">
      <div className="relative h-[190px] w-[190px]">
        <svg
          className="h-full w-full"
          viewBox="0 0 36 36"
          role="img"
          aria-label={`Нагрузка семестра: ${total} часов`}
        >
          {/* Track */}
          <circle
            cx="18"
            cy="18"
            r="15.5"
            fill="none"
            stroke={COLORS.track}
            strokeWidth="4.5"
            pathLength="100"
          />

          {/* Segments */}
          {segments.map((segment, index) => {
            const currentOffset = offset;
            offset += segment.value;

            return (
              <circle
                key={index}
                cx="18"
                cy="18"
                r="15.5"
                fill="none"
                stroke={segment.color}
                strokeWidth="4.5"
                strokeDasharray={`${segment.value} ${100 - segment.value}`}
                strokeDashoffset={-currentOffset}
                strokeLinecap="butt"
                pathLength="100"
                transform="rotate(-90 18 18)"
              />
            );
          })}
        </svg>

        {/* Center */}
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-mono text-3xl font-bold text-text-primary">
            {total}
          </span>

          <span className="mt-1 text-xs uppercase tracking-[0.16em] text-text-secondary">
            часов
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-5 grid w-full max-w-md grid-cols-3 gap-3">
        <LegendItem
          color={COLORS.lecture}
          label="ЛК"
          value={lecture}
          percent={lecturePct}
        />

        <LegendItem
          color={COLORS.practice}
          label="ПЗ"
          value={practice}
          percent={practicePct}
        />

        <LegendItem
          color={COLORS.lab}
          label="ЛР"
          value={lab}
          percent={labPct}
        />
      </div>
    </div>
  );
}

function LegendItem({ color, label, value, percent }) {
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-3">
      <div className="flex items-center gap-2">
        <span
          className="h-2.5 w-2.5 shrink-0 rounded-full"
          style={{ backgroundColor: color }}
        />

        <span className="text-xs font-semibold text-text-secondary">
          {label}
        </span>
      </div>

      <div className="mt-2 font-mono text-base font-semibold text-text-primary">
        {value} ч
      </div>

      <div className="mt-0.5 text-[11px] text-text-muted">
        {percent.toFixed(0)}%
      </div>
    </div>
  );
}