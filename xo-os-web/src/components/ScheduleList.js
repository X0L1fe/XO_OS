import React, { useEffect, useState } from "react";
import {
  FiCalendar,
  FiMapPin,
  FiUser,
  FiCheckCircle,
} from "react-icons/fi";

export default function ScheduleList() {
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadSchedule = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/schedule", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setSchedule(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch schedule:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadSchedule();
  }, []);

  const getTypeDetails = (type) => {
    switch (type) {
      case "LECTURE":
        return {
          label: "Лекция",
          badge:
            "border-accent-blue/30 bg-accent-blue/10 text-accent-blue",
          dot: "bg-accent-blue",
        };

      case "PRACTICE":
        return {
          label: "Практика",
          badge:
            "border-accent-purple/30 bg-accent-purple/10 text-accent-purple",
          dot: "bg-accent-purple",
        };

      case "LAB":
        return {
          label: "Лабораторная",
          badge:
            "border-accent-yellow/30 bg-accent-yellow/10 text-accent-yellow",
          dot: "bg-accent-yellow",
        };

      case "EXAM":
        return {
          label: "Экзамен",
          badge:
            "border-accent-red/30 bg-accent-red/10 text-accent-red",
          dot: "bg-accent-red",
        };

      default:
        return {
          label: "Занятие",
          badge:
            "border-border bg-background text-text-secondary",
          dot: "bg-text-secondary",
        };
    }
  };

  if (loading) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <ScheduleHeader />

        <div className="flex min-h-[180px] items-center justify-center">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <ScheduleHeader />

        <div className="flex min-h-[180px] flex-col items-center justify-center text-center">
          <p className="text-sm text-text-secondary">
            Не удалось загрузить расписание
          </p>

          <p className="mt-1 text-xs text-text-muted">
            {error}
          </p>
        </div>
      </section>
    );
  }

  if (schedule.length === 0) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <ScheduleHeader />

        <div className="flex min-h-[180px] items-center justify-center">
          <p className="text-sm text-text-secondary">
            Запланированных занятий нет
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-border bg-panel p-5">
      <ScheduleHeader />

      <div className="divide-y divide-border/60">
        {schedule.map((item, index) => {
          const type = getTypeDetails(item.type);
          const isSync = item.status === "sync";

          return (
            <div
              key={item.id || `${item.time}-${item.subject}-${index}`}
              className={`
                group
                grid
                grid-cols-[90px_minmax(90px,120px)_minmax(0,1fr)_140px_180px_110px]
                items-center
                gap-4
                py-4
                transition-colors
                duration-180
                hover:bg-card/50
              `}
            >
              {/* Time */}
              <div className="flex items-center gap-2">
                <FiCalendar className="h-4 w-4 shrink-0 text-text-muted" />

                <span className="font-mono text-sm font-semibold text-text-primary">
                  {item.time || "--:--"}
                </span>
              </div>

              {/* Type */}
              <div>
                <span
                  className={`
                    inline-flex
                    items-center
                    gap-2
                    rounded-full
                    border
                    px-3
                    py-1.5
                    text-[11px]
                    font-semibold
                    uppercase
                    tracking-wide
                    ${type.badge}
                  `}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${type.dot}`}
                  />

                  {type.label}
                </span>
              </div>

              {/* Subject */}
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-text-primary">
                  {item.subject || "Без названия"}
                </p>
              </div>

              {/* Room */}
              <div className="flex min-w-0 items-center gap-2 text-sm text-text-secondary">
                <FiMapPin className="h-4 w-4 shrink-0 text-text-muted" />

                <span className="truncate">
                  {item.room || "—"}
                </span>
              </div>

              {/* Teacher */}
              <div className="flex min-w-0 items-center gap-2 text-sm text-text-secondary">
                <FiUser className="h-4 w-4 shrink-0 text-text-muted" />

                <span className="truncate">
                  {item.teacher || "—"}
                </span>
              </div>

              {/* Sync status */}
              <div className="flex items-center justify-start gap-2">
                {isSync ? (
                  <>
                    <FiCheckCircle className="h-4 w-4 text-accent-green" />

                    <span className="text-xs font-medium text-accent-green">
                      В календаре
                    </span>
                  </>
                ) : (
                  <>
                    <span className="h-2 w-2 rounded-full bg-accent-red" />

                    <span className="text-xs font-medium text-accent-red">
                      Не синхр.
                    </span>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function ScheduleHeader() {
  return (
    <div className="mb-2 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-blue/10 text-accent-blue">
          <FiCalendar className="h-4 w-4" />
        </div>

        <div>
          <h2 className="text-lg font-bold text-text-primary">
            Ближайшие занятия
          </h2>

          <p className="mt-0.5 text-xs text-text-muted">
            Предстоящие события из расписания
          </p>
        </div>
      </div>

      <span className="hidden text-xs text-text-muted lg:block">
        Расписание
      </span>
    </div>
  );
}