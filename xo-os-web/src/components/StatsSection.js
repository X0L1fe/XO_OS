import React from "react";

import DonutChart from "./StatsSection/DonutChart";
import WeeklyChart from "./StatsSection/WeeklyChart";
import PlanFact from "./StatsSection/PlanFact";
import TopSubjects from "./StatsSection/TopSubjects";

export default function StatsSection() {
  return (
    <section className="rounded-xl border border-border bg-panel p-5">
      {/* Header */}
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-accent-blue">
            Аналитика
          </p>

          <h2 className="mt-1 text-xl font-bold text-text-primary">
            Статистика
          </h2>
        </div>
      </div>

      <div className="space-y-4">
        {/* =====================================================
            SEMESTER LOAD
        ====================================================== */}
        <section className="rounded-lg border border-border bg-card p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-text-primary">
                Нагрузка семестра
              </h3>

              <p className="mt-1 text-xs text-text-muted">
                Распределение часов по типам занятий
              </p>
            </div>
          </div>

          <DonutChart />
        </section>

        {/* =====================================================
            WEEKLY + TOP SUBJECTS
        ====================================================== */}
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          {/* Weekly */}
          <section className="rounded-lg border border-border bg-card p-5">
            <div className="mb-5">
              <h3 className="text-base font-semibold text-text-primary">
                Динамика по неделям
              </h3>

              <p className="mt-1 text-xs text-text-muted">
                Нагрузка по неделям семестра
              </p>
            </div>

            <WeeklyChart />
          </section>

          {/* Top subjects */}
          <section className="rounded-lg border border-border bg-card p-5">
            <div className="mb-5">
              <h3 className="text-base font-semibold text-text-primary">
                Лучшие предметы
              </h3>

              <p className="mt-1 text-xs text-text-muted">
                Основные предметы по выбранному показателю
              </p>
            </div>

            <TopSubjects />
          </section>
        </div>

        {/* =====================================================
            PLAN VS FACT
        ====================================================== */}
        <section className="rounded-lg border border-border bg-card p-5">
          <div className="mb-5">
            <h3 className="text-base font-semibold text-text-primary">
              План vs Факт
            </h3>

            <p className="mt-1 text-xs text-text-muted">
              Сопоставление запланированной и фактической нагрузки
            </p>
          </div>

          <PlanFact />
        </section>
      </div>
    </section>
  );
}