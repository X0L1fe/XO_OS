/* src/components/Sidebar.js */
import React, { useEffect, useState } from "react";

import Logo from "../assets/logo.svg";

import {
  FiHome,
  FiCalendar,
  FiCheck,
  FiFolder,
  FiBarChart2,
  FiAward,
  FiSettings,
  FiChevronLeft,
  FiChevronRight,
} from "react-icons/fi";

const Sidebar = ({ onSelect, activeSection, user }) => {
  const [collapsed, setCollapsed] = useState(() => {
    try {
      const item = localStorage.getItem("sidebarCollapsed");
      return item !== null ? JSON.parse(item) : false;
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(
        "sidebarCollapsed",
        JSON.stringify(collapsed)
      );
    } catch (error) {
      console.warn(
        "Не удалось сохранить состояние сайдбара",
        error
      );
    }
  }, [collapsed]);

  const [syncStatus, setSyncStatus] = useState("Синхронизировано");
  const [lastSync, setLastSync] = useState("Сегодня, 14:32");
  const [online, setOnline] = useState(false);
  const version = "XO_OS v1.0.0";

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const syncResp = await fetch("/api/google/status", {
          credentials: "include",
        });

        if (syncResp.ok) {
          const syncData = await syncResp.json();

          setSyncStatus(
            syncData.connected
              ? "Синхронизировано"
              : "Не синхронизировано"
          );

          if (syncData.last_synced_at) {
            const lastSyncDate = new Date(syncData.last_synced_at);

            setLastSync(
              `Последняя синхронизация: ${lastSyncDate.toLocaleString(
                "ru-RU"
              )}`
            );
          } else {
            setLastSync("Никогда не синхронизировалось");
          }
        }

        const healthResp = await fetch("/api/health", {
          credentials: "include",
        });

        setOnline(healthResp.ok);
      } catch (e) {
        console.error(
          "Failed to fetch sidebar status",
          e
        );

        setLastSync("Ошибка получения статуса");
      }
    };

    fetchStatus();

    const interval = setInterval(fetchStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  // --- Player stats (добавлено) ---
  const [playerStats, setPlayerStats] = useState({
    level: 0,
    xp: 0,
    xpToNext: 500,
  });

  useEffect(() => {
    if (!user) return;

    const loadStats = () => {
      fetch("/api/gamification/", { credentials: "include" })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
          }
          return res.json();
        })
        .then((data) => {
          if (!data) return;

          const safeLevel = Number.isFinite(data.level) ? data.level : 1;
          const safeXp = Number.isFinite(data.total_xp) ? data.total_xp : 0;
          const safeXpToNext = Number.isFinite(data.xp_remaining)
            ? data.xp_remaining
            : Math.max(0, safeLevel * 1000 - safeXp);

          setPlayerStats({
            level: safeLevel,
            xp: safeXp,
            xpToNext: safeXpToNext,
          });
        })
        .catch((err) => {
          console.warn("Failed to fetch player stats for sidebar:", err);
          if (user.level !== undefined) {
            const safeLevel = Number.isFinite(user.level) ? user.level : 1;
            const safeXp = Number.isFinite(user.xp) ? user.xp : 0;
            setPlayerStats({
              level: safeLevel,
              xp: safeXp,
              xpToNext: Math.max(0, safeLevel * 1000 - safeXp),
            });
          }
        });
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
  }, [user]);

  const xpTotal = (playerStats.xp || 0) + (playerStats.xpToNext || 0);
  const xpPercent =
    xpTotal > 0
      ? Math.min(100, ((playerStats.xp || 0) / xpTotal) * 100)
      : 0;
  const blocksFilled = Math.floor(xpPercent / 10);

  const navItems = [
    { id: "dashboard", Icon: FiHome, label: "Главная" },
    { id: "schedule", Icon: FiCalendar, label: "Расписание" },
    { id: "tasks", Icon: FiCheck, label: "Задачи" },
    { id: "projects", Icon: FiFolder, label: "Проекты" },
    { id: "stats", Icon: FiBarChart2, label: "Статистика" },
    { id: "achievements", Icon: FiAward, label: "Достижения" },
    { id: "settings", Icon: FiSettings, label: "Настройки" },
  ];

  return (
    <>
      {/* ============================================================
          DESKTOP / TABLET SIDEBAR (lg+)
      ============================================================ */}
      <aside
        className={`
          hidden lg:flex flex-col items-center
          ${collapsed ? "w-20" : "w-60"}
          h-fit
          m-4
          rounded-2xl
          overflow-hidden
          flex-shrink-0
          bg-panel
          border border-border
          shadow-md
          transition-[width]
          duration-300
          ease-[cubic-bezier(0.4,0,0.2,1)]
          will-change-[width]
        `}
      >
        {/* Логотип */}
        <div
          className={`
          flex
          items-center
          transition-all
          duration-300
          ${collapsed
              ? "justify-center px-2 py-5"
              : "justify-start px-5 py-5"
            }
        `}
        >
          <img
            src={Logo}
            alt="XO_OS Logo"
            className="h-8 w-auto flex-shrink-0"
          />

          <span
            className={`
            grid
            transition-all
            duration-300
            ease-out
            ${collapsed
                ? "grid-cols-[0fr] opacity-0 ml-0"
                : "grid-cols-[1fr] opacity-100 ml-3"
              }
          `}
          >
            <span className="overflow-hidden whitespace-nowrap text-sm font-bold">
              XO_OS
            </span>
          </span>
        </div>

        {/* Player Info Block */}
        <div
          className={`
          w-full
          px-5
          overflow-hidden
          transition-all
          duration-300
          ${collapsed
              ? "max-h-0 opacity-0 mb-0"
              : "max-h-40 opacity-100 mb-2"
            }
        `}
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-accent-blue rounded-xl flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
              {playerStats.level}
            </div>
            <div className="flex-1 min-w-0 space-y-1">
              <div className="text-[10px] text-text-secondary tracking-wider uppercase">
                ОПЕРАТИВНАЯ СИСТЕМА
              </div>
              <div className="flex items-center space-x-2">
                <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent-blue transition-all duration-500"
                    style={{ width: `${xpPercent}%` }}
                  />
                </div>
                <div className="text-[10px] text-text-secondary whitespace-nowrap">
                  {playerStats.xp} XP
                </div>
              </div>
              <div className="text-[10px] text-text-secondary">
                {playerStats.xpToNext > 0
                  ? `${playerStats.xpToNext} до след. ур.`
                  : "MAX"}
              </div>
            </div>
          </div>

          {/* 10-блочный прогресс — только 10, без дублей */}
          {playerStats.xpToNext > 0 && (
            <div className="flex items-center space-x-1 mt-3">
              {[...Array(10)].map((_, i) => (
                <span
                  key={i}
                  className={`w-3 h-3 rounded transition-colors duration-300 ${i < blocksFilled ? "bg-accent-blue" : "bg-accent-blue/20"
                    }`}
                />
              ))}
            </div>
          )}
        </div>

        {/* Слоган */}
        <div
          className={`
          px-5
          text-center
          text-xs
          text-text-secondary
          overflow-hidden
          whitespace-nowrap
          transition-all
          duration-300
          ${collapsed
              ? "max-h-0 opacity-0 mb-0"
              : "max-h-10 opacity-100 mb-5"
            }
        `}
        >
          Учись. Развивайся. Достигай.
        </div>

        {/* Навигация */}
        <nav className="w-full px-3 space-y-1">
          {navItems.map(({ id, Icon, label }) => {
            const isActive = id === activeSection;

            return (
              <button
                key={id}
                onClick={() => onSelect(id)}
                className={`
                flex
                items-center
                w-full
                h-11
                rounded-lg
                transition-[background-color,transform] duration-200 active:scale-[0.98]
                ${isActive
                    ? "font-bold text-text-primary bg-accent-blue/20 border-l-4 border-accent-blue_bright"
                    : "text-text-primary hover:bg-accent-blue/10"
                  }
              `}
                title={collapsed ? label : undefined}
              >
                <div
                  className={`
                  flex
                  items-center
                  flex-shrink-0
                  transition-all
                  duration-300
                  ${collapsed
                      ? "justify-center w-full"
                      : "justify-start w-full px-2"
                    }
                `}
                >
                  <Icon
                    className={`
                    h-5 w-5 flex-shrink-0
                    ${isActive
                        ? "text-accent-blue_bright"
                        : "text-text-secondary"
                      }
                    transition-colors
                    duration-200
                  `}
                  />

                  <span
                    className={`
                      grid
                      transition-all
                      duration-300
                      ease-out
                      ${collapsed
                        ? "grid-cols-[0fr] opacity-0 ml-0"
                        : "grid-cols-[1fr] opacity-100 ml-3"
                      }
                    `}
                  >
                    <span className="overflow-hidden whitespace-nowrap">
                      {label}
                    </span>
                  </span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Google Calendar */}
        <div
          className={`
          mt-auto
          px-5
          pb-4
          overflow-hidden
          transition-all
          duration-300
          ${collapsed
              ? "opacity-0 max-h-0 px-0"
              : "opacity-100 max-h-52"
            }
        `}
        >
          <div className="hidden [@media(min-height:850px)]:block mt-2">
            <div className="mb-1 text-xs">
              Google Calendar
            </div>

            <div className="flex items-center">
              <span
                className={`w-2 h-2 rounded-full mr-2 ${syncStatus === "Синхронизировано"
                  ? "bg-accent-green"
                  : "bg-red-500"
                  }`}
              />

              <span className="text-xs text-text-secondary">
                {syncStatus}
              </span>
            </div>
          </div>
          {/* Скрываем дату на низких экранах */}
          <div className="hidden [@media(min-height:850px)]:block mt-4">
            <div className="text-xs">
              Последняя синхронизация:
            </div>
            <div className="text-sm text-text-secondary break-all">
              {lastSync}
            </div>
          </div>

          {/* Версия — ВСЕГДА ВИДНА */}
          <div className="mt-2 text-xs">
            Версия:
          </div>
          <div className="font-mono text-xs text-text-secondary">
            {version}
          </div>

          {/* Скрываем статус соединения на низких экранах */}
          <div className="hidden [@media(min-height:850px)]:block mt-2">
            <div className="text-xs">
              Статус соединения:
            </div>
            <div className="text-sm text-text-secondary">
              {online ? "Онлайн" : "Офлайн"}
            </div>
          </div>
        </div>

        {/* Кнопка сворачивания */}
        <button
          onClick={() => setCollapsed((value) => !value)}
          className={`
          mx-3
          mb-3
          h-9
          w-9
          flex
          items-center
          justify-center
          rounded-lg
          bg-accent-blue/20
          hover:bg-accent-blue/30
          text-text-primary
          transition-[background-color,transform] duration-200 active:scale-[0.98]
          border
          border-border
        `}
          title={
            collapsed
              ? "Развернуть меню"
              : "Свернуть меню"
          }
        >
          {collapsed ? (
            <FiChevronRight className="w-5 h-5" />
          ) : (
            <FiChevronLeft className="w-5 h-5" />
          )}
        </button>
      </aside>
      {/* ============================================================
          MOBILE BOTTOM NAV (< lg)
      ============================================================ */}
      <nav
        className="
          lg:hidden
          fixed bottom-0 inset-x-0 z-40
          bg-panel/95 backdrop-blur-xl
          border-t border-border
          pb-[env(safe-area-inset-bottom)]
        "
      >
        {(() => {
          const activeIndex = Math.max(
            0,
            navItems.findIndex((item) => item.id === activeSection)
          );

          return (
            <div className="relative flex items-stretch justify-around h-16 px-1">
              {/* Скользящая подложка */}
              <span
                aria-hidden="true"
                className="
                  pointer-events-none absolute top-1.5 h-8
                  rounded-full bg-accent-blue/20
                  transition-transform duration-300
                  ease-[cubic-bezier(0.4,0,0.2,1)]
                  will-change-transform
                "
                style={{
                  width: `calc((100% - 0.5rem) / ${navItems.length})`,
                  left: "0.25rem",
                  transform: `translateX(${activeIndex * 100}%)`,
                }}
              />

              {navItems.map(({ id, Icon, label }) => {
                const isActive = id === activeSection;

                return (
                  <button
                    key={id}
                    onClick={() => onSelect(id)}
                    aria-label={label}
                    title={label}
                    className="
                      relative z-10
                      flex-1 min-w-0
                      flex flex-col items-center justify-center gap-1
                      transition-transform duration-150
                      active:scale-95
                    "
                  >
                    <span className="flex items-center justify-center h-8 w-12">
                      <Icon
                        className={`
                          h-5 w-5
                          transition-colors duration-200
                          ${isActive
                            ? "text-accent-blue"
                            : "text-text-secondary"
                          }
                        `}
                      />
                    </span>

                    <span
                      className={`
                        text-[9px] leading-none tracking-tight
                        transition-colors duration-200
                        ${isActive
                          ? "text-accent-blue font-semibold"
                          : "text-text-muted"
                        }
                      `}
                    >
                      {label}
                    </span>
                  </button>
                );
              })}
            </div>
          );
        })()}
      </nav>
    </>
  );
};

export default Sidebar;