import React, { useEffect, useState } from "react";

import DonutChart from "./StatsSection/DonutChart";
import WeeklyChart from "./StatsSection/WeeklyChart";
import PlanFact from "./StatsSection/PlanFact";
import TopSubjects from "./StatsSection/TopSubjects";

const FILTER_EVENT_NAME =
  "xo-os:schedule-filters-changed";

export default function StatsSection() {
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const handleFiltersChanged = () => {
      /*
       * ScheduleList уже сохранил фильтр на backend.
       * Просто увеличиваем refreshKey — все статистические
       * компоненты повторно запросят свои endpoints.
       */
      setRefreshKey((value) => value + 1);
    };

    window.addEventListener(
      FILTER_EVENT_NAME,
      handleFiltersChanged
    );

    return () => {
      window.removeEventListener(
        FILTER_EVENT_NAME,
        handleFiltersChanged
      );
    };
  }, []);

  return (
    <section className="rounded-2xl border border-border bg-panel p-5 shadow-xl shadow-black/10 sm:p-6">
      {/* Header */}
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-accent-blue">
            Аналитика
          </p>

          <h2 className="mt-1 text-xl font-bold tracking-tight text-text-primary">
            Статистика
          </h2>

          <p className="mt-1 text-xs text-text-muted">
            Нагрузка текущего семестра с учётом фильтров расписания
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Semester */}
        <section className="rounded-xl border border-border bg-card p-5 sm:p-6">
          <div className="mb-6">
            <h3 className="text-base font-semibold text-text-primary">
              Нагрузка семестра
            </h3>

            <p className="mt-1 text-xs text-text-muted">
              Фактическое распределение часов по типам занятий
            </p>
          </div>

          <DonutChart refreshKey={refreshKey} mode="full" size={280}/>
        </section>

        {/* Weekly + subjects */}
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <section className="rounded-xl border border-border bg-card p-5 sm:p-6">
            <div className="mb-6">
              <h3 className="text-base font-semibold text-text-primary">
                Динамика по неделям
              </h3>

              <p className="mt-1 text-xs text-text-muted">
                Нагрузка по неделям текущего семестра
              </p>
            </div>

            <WeeklyChart refreshKey={refreshKey} />
          </section>

          <section className="rounded-xl border border-border bg-card p-5 sm:p-6">
            <div className="mb-6">
              <h3 className="text-base font-semibold text-text-primary">
                Предметы
              </h3>

              <p className="mt-1 text-xs text-text-muted">
                Пять предметов с наибольшей нагрузкой
              </p>
            </div>

            <TopSubjects refreshKey={refreshKey} />
          </section>
        </div>

        {/* Progress */}
        <section className="rounded-xl border border-border bg-card p-5 sm:p-6">
          <div className="mb-6">
            <h3 className="text-base font-semibold text-text-primary">
              Прогресс семестра
            </h3>

            <p className="mt-1 text-xs text-text-muted">
              Сколько запланированной нагрузки уже прошло
            </p>
          </div>

          <PlanFact refreshKey={refreshKey} />
        </section>
      </div>
    </section>
  );
}