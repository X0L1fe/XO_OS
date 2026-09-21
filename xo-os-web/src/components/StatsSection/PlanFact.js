import React, { useEffect, useState } from "react";

export default function PlanFact() {
  const [planFact, setPlanFact] = useState({
    study: { plan: 0, fact: 0 },
    projects: { plan: 0, fact: 0 },
    self: { plan: 0, fact: 0 },
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadPlanFact = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/stats/planfact", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setPlanFact({
          study: {
            plan: Number(data?.study?.plan) || 0,
            fact: Number(data?.study?.fact) || 0,
          },
          projects: {
            plan: Number(data?.projects?.plan) || 0,
            fact: Number(data?.projects?.fact) || 0,
          },
          self: {
            plan: Number(data?.self?.plan) || 0,
            fact: Number(data?.self?.fact) || 0,
          },
        });
      } catch (err) {
        console.error("Failed to fetch plan/fact stats:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPlanFact();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[180px] items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[180px] flex-col items-center justify-center text-center">
        <p className="text-sm text-text-secondary">
          Ошибка загрузки данных
        </p>

        <p className="mt-1 text-xs text-text-muted">
          {error}
        </p>
      </div>
    );
  }

  const rows = [
    {
      key: "study",
      label: "УЧЕБА",
      color: "blue",
      data: planFact.study,
    },
    {
      key: "projects",
      label: "ПРОЕКТЫ",
      color: "purple",
      data: planFact.projects,
    },
    {
      key: "self",
      label: "САМОРАЗВИТИЕ",
      color: "green",
      data: planFact.self,
    },
  ];

  const hasData = rows.some(
    (row) => row.data.plan > 0 || row.data.fact > 0
  );

  if (!hasData) {
    return (
      <div className="flex min-h-[180px] items-center justify-center">
        <p className="text-sm text-text-secondary">
          Данные не загружены
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Column labels */}
      <div className="grid grid-cols-[120px_1fr_1fr] gap-4">
        <div />

        <div className="text-xs uppercase tracking-wider text-text-muted">
          План
        </div>

        <div className="text-xs uppercase tracking-wider text-text-muted">
          Факт
        </div>
      </div>

      {rows.map((row) => {
        const plan = row.data.plan;
        const fact = row.data.fact;
        const maxValue = Math.max(plan, fact, 1);

        const planPercent = (plan / maxValue) * 100;
        const factPercent = (fact / maxValue) * 100;

        const colors = {
          blue: {
            plan: "bg-accent-blue/25",
            fact: "bg-accent-blue",
            value: "text-accent-blue",
          },
          purple: {
            plan: "bg-accent-purple/25",
            fact: "bg-accent-purple",
            value: "text-accent-purple",
          },
          green: {
            plan: "bg-accent-green/25",
            fact: "bg-accent-green",
            value: "text-accent-green",
          },
        };

        const palette = colors[row.color];

        return (
          <div
            key={row.key}
            className="grid grid-cols-[120px_1fr_1fr] items-center gap-4"
          >
            {/* Label */}
            <div className="text-xs font-semibold tracking-wider text-text-secondary">
              {row.label}
            </div>

            {/* Plan */}
            <ProgressColumn
              value={plan}
              percentage={planPercent}
              barClass={palette.plan}
              valueClass={palette.value}
            />

            {/* Fact */}
            <ProgressColumn
              value={fact}
              percentage={factPercent}
              barClass={palette.fact}
              valueClass={palette.value}
            />
          </div>
        );
      })}
    </div>
  );
}

function ProgressColumn({
  value,
  percentage,
  barClass,
  valueClass,
}) {
  return (
    <div>
      <div className="h-2.5 overflow-hidden rounded-full bg-background">
        <div
          className={`h-full rounded-full transition-all duration-300 ${barClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div
        className={`mt-1.5 font-mono text-xs font-medium ${valueClass}`}
      >
        {value} ч
      </div>
    </div>
  );
}