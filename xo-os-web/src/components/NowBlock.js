import React, { useCallback, useEffect, useState } from "react";
import {
  FiBookOpen,
  FiClock,
  FiFlag,
  FiPlay,
  FiRefreshCw,
  FiZap,
} from "react-icons/fi";

const FILTER_EVENT_NAME =
  "xo-os:schedule-filters-changed";

const EMPTY_NOW = {
  taskTitle: "",
  taskDesc: "",
  timeEstimate: "",
  priority: "",
  xpReward: 0,
  time: "--:--",
  category: "",
};

export default function NowBlock() {
  const [now, setNow] = useState(EMPTY_NOW);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [currentTime, setCurrentTime] = useState(
    formatCurrentTime()
  );

  const loadNow = useCallback(
    async (showRefreshing = false) => {
      if (showRefreshing) {
        setRefreshing(true);
      }

      try {
        const response = await fetch("/api/now", {
          credentials: "include",
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setNow({
          ...EMPTY_NOW,
          ...data,
        });
      } catch (error) {
        console.error(
          "Failed to fetch current lesson:",
          error
        );

        setNow(EMPTY_NOW);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    []
  );

  /*
   * Initial load + automatic refresh.
   */
  useEffect(() => {
    loadNow();

    const interval = window.setInterval(() => {
      loadNow(true);
    }, 15000);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadNow]);

  /*
   * Live clock.
   */
  useEffect(() => {
    const updateClock = () => {
      setCurrentTime(formatCurrentTime());
    };

    updateClock();

    const interval = window.setInterval(
      updateClock,
      1000
    );

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  /*
   * When schedule filters change, immediately
   * re-check current event.
   */
  useEffect(() => {
    const handleFiltersChanged = () => {
      loadNow(true);
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
  }, [loadNow]);

  const hasTask = Boolean(now.taskTitle);

  return (
    <section
      className="
        group
        relative
        overflow-hidden
        rounded-2xl
        border
        border-border
        bg-panel
        p-6
        transition-all
        duration-300
        ease-out
        hover:border-accentBlue/30
        hover:shadow-[0_12px_40px_rgba(0,0,0,0.22)]
      "
    >
      {/* Glow */}
      <div
        className="
          pointer-events-none
          absolute
          -right-16
          -top-16
          h-32
          w-32
          rounded-full
          bg-accentBlue/10
          blur-3xl
          opacity-50
          transition-opacity
          duration-300
          group-hover:opacity-80
        "
      />

      {/* Header */}
      <div
        className="
          relative
          flex
          items-center
          justify-between
          border-b
          border-border
          pb-4
        "
      >
        <div className="flex items-center gap-3">
          <div
            className="
              flex
              h-9
              w-9
              items-center
              justify-center
              rounded-xl
              border
              border-accentBlue/20
              bg-accentBlue/10
              text-accentBlue
              transition-all
              duration-300
              group-hover:border-accentBlue/30
              group-hover:bg-accentBlue/15
            "
          >
            <FiClock size={16} />
          </div>

          <div>
            <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-secondary">
              Текущий фокус
            </p>

            <h2 className="mt-0.5 text-lg font-semibold tracking-tight text-primary">
              СЕЙЧАС
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {refreshing && (
            <FiRefreshCw
              size={13}
              className="animate-spin text-secondary"
            />
          )}

          <span
            className="
              rounded-lg
              border
              border-border
              bg-background/60
              px-3
              py-1.5
              font-mono
              text-xs
              font-medium
              text-secondary
            "
          >
            {currentTime}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="relative mt-5">
        {loading ? (
          <div className="space-y-4 animate-pulse">
            <div className="h-8 w-2/3 rounded-lg bg-background" />
            <div className="h-4 w-24 rounded bg-background" />
            <div className="h-4 w-4/5 rounded bg-background" />

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="h-12 rounded-xl bg-background" />
              <div className="h-12 rounded-xl bg-background" />
            </div>

            <div className="h-12 rounded-xl bg-background" />
          </div>
        ) : !hasTask ? (
          <div
            className="
              flex
              min-h-[190px]
              flex-col
              items-center
              justify-center
              rounded-xl
              border
              border-dashed
              border-border
              bg-background/40
              px-6
              text-center
            "
          >
            <div
              className="
                mb-3
                flex
                h-11
                w-11
                items-center
                justify-center
                rounded-xl
                border
                border-border
                bg-background
                text-secondary
              "
            >
              <FiBookOpen size={18} />
            </div>

            <p className="text-sm font-medium text-primary">
              Сейчас нет активного занятия
            </p>

            <p className="mt-1 text-xs leading-5 text-secondary">
              Здесь появится текущее событие расписания.
            </p>
          </div>
        ) : (
          <>
            {/* Main */}
            <div>
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p
                    className="
                      text-2xl
                      font-semibold
                      leading-tight
                      tracking-tight
                      text-primary
                    "
                  >
                    {now.taskTitle}
                  </p>

                  {now.category && (
                    <div className="mt-3 inline-flex items-center gap-2 rounded-lg border border-accentBlue/15 bg-accentBlue/10 px-2.5 py-1.5">
                      <FiBookOpen
                        size={12}
                        className="text-accentBlue"
                      />

                      <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-accentBlue">
                        {now.category}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {now.taskDesc && (
                <p
                  className="
                    mt-4
                    max-w-3xl
                    text-sm
                    leading-6
                    text-secondary
                  "
                >
                  {now.taskDesc}
                </p>
              )}
            </div>

            {/* Meta */}
            <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div
                className="
                  rounded-xl
                  border
                  border-border
                  bg-background/50
                  px-4
                  py-3
                  transition-all
                  duration-200
                  hover:border-accentBlue/20
                  hover:bg-background/70
                "
              >
                <div className="flex items-center gap-2 text-secondary">
                  <FiClock size={14} />

                  <span className="text-[10px] font-medium uppercase tracking-[0.14em]">
                    Время занятия
                  </span>
                </div>

                <p className="mt-2 font-mono text-sm font-medium text-primary">
                  {now.timeEstimate || "Не указано"}
                </p>
              </div>

              <div
                className="
                  rounded-xl
                  border
                  border-border
                  bg-background/50
                  px-4
                  py-3
                  transition-all
                  duration-200
                  hover:border-accentYellow/20
                  hover:bg-background/70
                "
              >
                <div className="flex items-center gap-2 text-secondary">
                  <FiFlag size={14} />

                  <span className="text-[10px] font-medium uppercase tracking-[0.14em]">
                    Тип
                  </span>
                </div>

                <p className="mt-2 text-sm font-medium text-primary">
                  {formatLessonType(now.priority)}
                </p>
              </div>
            </div>

            {/* XP */}
            <div
              className="
                mt-4
                flex
                items-center
                justify-between
                rounded-xl
                border
                border-accentYellow/15
                bg-accentYellow/5
                px-4
                py-3
              "
            >
              <div className="flex items-center gap-2.5">
                <div
                  className="
                    flex
                    h-8
                    w-8
                    items-center
                    justify-center
                    rounded-lg
                    bg-accentYellow/10
                    text-accentYellow
                  "
                >
                  <FiZap size={15} />
                </div>

                <span className="text-xs font-medium uppercase tracking-[0.14em] text-secondary">
                  Награда
                </span>
              </div>

              <span className="font-mono text-sm font-semibold text-accentYellow">
                +{Number(now.xpReward) || 0} XP
              </span>
            </div>

            {/* Action */}
            <button
              type="button"
              className="
                mt-5
                flex
                w-full
                items-center
                justify-center
                gap-2.5
                rounded-xl
                border
                border-accentBlue/20
                bg-accentBlue
                px-4
                py-3
                text-sm
                font-semibold
                text-white
                shadow-[0_8px_24px_rgba(30,130,255,0.14)]
                transition-all
                duration-200
                ease-out
                hover:-translate-y-0.5
                hover:bg-accentBlue/90
                hover:shadow-[0_12px_30px_rgba(30,130,255,0.2)]
                active:translate-y-0
                active:scale-[0.99]
              "
            >
              <FiPlay size={15} />
              НАЧАТЬ
            </button>
          </>
        )}
      </div>
    </section>
  );
}

function formatCurrentTime() {
  return new Intl.DateTimeFormat("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
}

function formatLessonType(type) {
  const normalized = String(type || "")
    .trim()
    .toUpperCase();

  switch (normalized) {
    case "LECTURE":
      return "Лекция";

    case "PRACTICE":
      return "Практика";

    case "LAB":
      return "Лабораторная";

    case "EXAM":
      return "Экзамен";

    default:
      return type || "Занятие";
  }
}