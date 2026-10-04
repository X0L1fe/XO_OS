import React, { useEffect, useState } from "react";
import {
  FiZap,
  FiBattery,
  FiTarget,
  FiTrendingUp,
} from "react-icons/fi";

const PlayerCard = ({ user }) => {
  const [stats, setStats] = useState({
    level: 1,
    total_xp: 0,
    focus: 0,
    energy: 0,
    discipline: 0,
    productivity: 0,
    name: "",
    role: "Студент-исследователь",
  });

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await fetch("/api/gamification/", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setStats((prev) => ({
          ...prev,
          level: Number.isFinite(data.level) ? data.level : prev.level,
          total_xp: Number.isFinite(data.total_xp)
            ? data.total_xp
            : prev.total_xp,
          // name/role в gamification нет — оставляем как было,
          // они подтянутся из пропа user во втором useEffect.
        }));
      } catch (error) {
        console.warn("Failed to fetch player stats:", error);
      }
    };

    loadStats();

    const onGamificationUpdated = () => loadStats();
    window.addEventListener(
      "xo-os:gamification-updated",
      onGamificationUpdated
    );

    return () => {
      window.removeEventListener(
        "xo-os:gamification-updated",
        onGamificationUpdated
      );
    };
  }, []);

  /*
   * Данные пользователя используются как начальное состояние,
   * если backend stats ещё не успел загрузиться.
   */
  useEffect(() => {
    if (!user) {
      return;
    }

    setStats((prev) => ({
      ...prev,
      name: user.name || prev.name,
      role: user.role || prev.role,
      level: user.level ?? prev.level,
      total_xp: user.total_xp ?? prev.total_xp,
    }));
  }, [user]);

  const level = Number(stats.level) || 1;
  const totalXP = Number(stats.total_xp) || 0;

  /*
   * Текущая модель уровней проекта:
   * уровень N -> следующий уровень начинается после N * 1000 XP.
   */
  const currentLevelStart = (level - 1) * 1000;
  const nextLevelXP = level * 1000;

  const levelProgressXP = Math.max(
    0,
    totalXP - currentLevelStart
  );

  const levelRange = Math.max(
    1,
    nextLevelXP - currentLevelStart
  );

  const xpProgress = Math.min(
    100,
    (levelProgressXP / levelRange) * 100
  );

  const name =
    stats.name ||
    user?.name ||
    "Пользователь";

  const role =
    stats.role ||
    user?.role ||
    "Студент-исследователь";

  const initials = name
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2) || "XO";

  const playerStats = [
    {
      label: "Focus",
      value: Number(stats.focus) || 0,
      icon: FiTarget,
      accent: "blue",
    },
    {
      label: "Energy",
      value: Number(stats.energy) || 0,
      icon: FiZap,
      accent: "yellow",
    },
    {
      label: "Discipline",
      value: Number(stats.discipline) || 0,
      icon: FiBattery,
      accent: "green",
    },
    {
      label: "Productivity",
      value: Number(stats.productivity) || 0,
      icon: FiTrendingUp,
      accent: "purple",
    },
  ];

  const accentClasses = {
    blue: {
      iconBg: "bg-accent-blue/10",
      icon: "text-accent-blue",
      border: "border-accent-blue/20",
    },
    yellow: {
      iconBg: "bg-accent-yellow/10",
      icon: "text-accent-yellow",
      border: "border-accent-yellow/20",
    },
    green: {
      iconBg: "bg-accent-green/10",
      icon: "text-accent-green",
      border: "border-accent-green/20",
    },
    purple: {
      iconBg: "bg-accent-purple/10",
      icon: "text-accent-purple",
      border: "border-accent-purple/20",
    },
  };

  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(300px,1.05fr)_minmax(520px,1.95fr)] xl:items-center">

        {/* =====================================================
            PLAYER IDENTITY
        ====================================================== */}
        <div className="min-w-0">
          <div className="flex items-center gap-4">
            {/* Avatar */}
            <div className="relative flex h-[76px] w-[76px] shrink-0 items-center justify-center rounded-full border-2 border-accent-blue bg-background shadow-[0_0_20px_rgba(22,131,255,0.14)]">
              <span className="font-mono text-2xl font-bold text-text-primary">
                {initials}
              </span>

              <span className="absolute inset-[-5px] rounded-full border border-accent-blue/30" />
            </div>

            {/* Identity */}
            <div className="min-w-0">
              <h2 className="truncate text-2xl font-bold tracking-tight text-text-primary">
                {name}
              </h2>

              <p className="mt-1 text-sm text-text-secondary">
                {role}
              </p>

              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
                <span className="text-sm font-semibold text-text-primary">
                  Уровень {level}
                </span>

                <span className="font-mono text-sm text-accent-blue">
                  XP {levelProgressXP} / {levelRange}
                </span>
              </div>
            </div>
          </div>

          {/* XP Bar */}
          <div className="mt-5">
            <div className="h-2 overflow-hidden rounded-full bg-background">
              <div
                className="h-full rounded-full bg-accent-blue transition-all duration-500"
                style={{ width: `${xpProgress}%` }}
              />
            </div>

            <div className="mt-2 flex items-center justify-between text-[11px] text-text-muted">
              <span>
                {totalXP} XP всего
              </span>

              <span>
                {Math.max(0, nextLevelXP - totalXP)} XP до уровня {level + 1}
              </span>
            </div>
          </div>
        </div>

        {/* =====================================================
            PLAYER ATTRIBUTES
        ====================================================== */}
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {playerStats.map((stat) => {
            const Icon = stat.icon;
            const colors = accentClasses[stat.accent];

            return (
              <div
                key={stat.label}
                className={`
                  min-w-0 rounded-lg
                  border
                  ${colors.border}
                  bg-background/70
                  px-3
                  py-3.5
                  transition-all
                  duration-180
                  hover:-translate-y-0.5
                  hover:bg-card
                `}
              >
                {/* Icon */}
                <div
                  className={`
                    flex
                    h-8
                    w-8
                    items-center
                    justify-center
                    rounded-md
                    ${colors.iconBg}
                    ${colors.icon}
                  `}
                >
                  <Icon className="h-4 w-4" />
                </div>

                {/* Label */}
                <div className="mt-3 truncate text-[11px] font-medium uppercase tracking-[0.08em] text-text-secondary">
                  {stat.label}
                </div>

                {/* Value */}
                <div className="mt-1 flex items-baseline gap-1">
                  <span className="font-mono text-xl font-bold text-text-primary">
                    {Math.max(0, Math.min(100, stat.value))}
                  </span>

                  <span className="font-mono text-[11px] text-text-muted">
                    /100
                  </span>
                </div>

                {/* Small progress */}
                <div className="mt-3 h-1 overflow-hidden rounded-full bg-background">
                  <div
                    className={`
                      h-full rounded-full
                      ${stat.accent === "blue"
                        ? "bg-accent-blue"
                        : stat.accent === "yellow"
                          ? "bg-accent-yellow"
                          : stat.accent === "green"
                            ? "bg-accent-green"
                            : "bg-accent-purple"
                      }
                    `}
                    style={{
                      width: `${Math.max(
                        0,
                        Math.min(100, stat.value)
                      )}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default PlayerCard;