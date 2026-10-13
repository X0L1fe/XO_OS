import React, { useEffect, useState } from 'react';
import { AiOutlineLogout, AiOutlineSearch } from 'react-icons/ai';
import NotificationBell from './NotificationBell';

export default function Header({ onLogout }) {
  const [user, setUser] = useState(null);
  const [online, setOnline] = useState(false);
  const [switchProgress, setSwitchProgress] = useState(null);
  const [showCompleted, setShowCompleted] = useState(false);

  useEffect(() => {
    let stopped = false;
    let pollInterval = null;
    let hideTimeout = null;

    const poll = async () => {
      if (stopped) return;
      try {
        const resp = await fetch("/api/google/calendar/switch-progress", {
          credentials: "include",
        });
        if (!resp.ok) return;
        const data = await resp.json();

        if (!data.active && data.status !== "completed" && data.status !== "failed") {
          setSwitchProgress(null);
          return;
        }

        setSwitchProgress(data);

        if (data.status === "completed" || data.status === "failed") {
          // Показываем финальное состояние 5 секунд и скрываем
          setShowCompleted(true);
          clearInterval(pollInterval);
          hideTimeout = setTimeout(() => {
            setSwitchProgress(null);
            setShowCompleted(false);
          }, 5000);
        }
      } catch (e) {
        // тихо игнорируем сетевые ошибки
      }
    };

    // Проверяем сразу при монтировании
    poll();
    pollInterval = setInterval(poll, 1500);

    return () => {
      stopped = true;
      if (pollInterval) clearInterval(pollInterval);
      if (hideTimeout) clearTimeout(hideTimeout);
    };
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const resp = await fetch('/api/auth/me', { credentials: 'include' });
        if (resp.ok) {
          const data = await resp.json();
          if (data.authenticated) {
            setUser(data.user);
          }
        }
      } catch (e) {
        console.error('Failed to fetch user', e);
      }
    };

    const checkHealth = async () => {
      try {
        const resp = await fetch('/api/health', { credentials: 'include' });
        setOnline(resp.ok);
      } catch (e) {
        setOnline(false);
      }
    };

    fetchUser();
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogoutClick = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      onLogout();
    } catch (e) {
      console.error('Logout failed', e);
    }
  };

  if (!user) {
    return null; // или показывать гостя
  }

  const SwitchProgressToast = ({ data }) => {
    if (!data) return null;

    const percent = data.percent || 0;
    const isCompleted = data.status === "completed";
    const isFailed = data.status === "failed";

    const sourceName = data.source_calendar_name || "календаря";
    const targetName = data.target_calendar_name || "календарь";

    let label;
    if (isCompleted) {
      label = `Перенос событий из ${sourceName} в ${targetName} завершён`;
    } else if (isFailed) {
      label = `Ошибка переноса: ${data.error_message || "неизвестно"}`;
    } else {
      label = `Перенос событий из ${sourceName} в ${targetName} готов на`;
    }

    return (
      <div
        className="
          fixed top-20 right-6 z-50
          w-96 rounded-2xl
          border border-border
          bg-panel
          px-5 py-4
          shadow-lg
          transition-all duration-300
        "
      >
        <div className="text-sm font-medium text-text-primary">
          {label}
        </div>

        {!isFailed && (
          <>
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-border">
              <div
                className={`
                  h-full rounded-full
                  transition-all duration-500 ease-out
                  ${isCompleted ? "bg-accentGreen" : "bg-accentBlue"}
                `}
                style={{ width: `${percent}%` }}
              />
            </div>

            <div className="mt-1.5 flex justify-between text-xs text-text-muted">
              <span>
                {data.processed} из {data.total}
              </span>
              <span className="font-mono">{percent}%</span>
            </div>
          </>
        )}

        {isFailed && (
          <div className="mt-2 text-xs text-accentRed">
            {data.error_message || "Не удалось завершить перенос"}
          </div>
        )}
      </div>
    );
  };

  return (
    <header className="bg-panel/80 backdrop-blur-sm border-b border-border/50 relative z-40">
      <div className="px-6 py-4 flex items-center justify-between">
        {/* Левая часть - поиск как системное поле ввода */}
        <div className="flex items-center space-x-3 flex-1 max-w-2xl">
          <div className="relative">
            <AiOutlineSearch
              className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/60"
            />
            <input
              type="text"
              placeholder="Поиск по задачам, проектам, расписанию..."
              className="w-full pl-10 pr-4 py-2 bg-background/80 backdrop-blur border-none rounded-xl
                         text-primary placeholder-secondary/70 focus:outline-none focus:ring-2
                         focus:ring-accentBlue/50 focus:ring-offset-2 focus:ring-offset-bg/80
                         transition-all duration-200"
            />
          </div>
        </div>

        {/* Правая часть - статус и пользователь в компактном виде */}
        <div className="flex items-center space-x-6">
          {/* Область пользователя как профиль/статус */}
          <div className="relative flex items-center space-x-3">

            {/* Уведомления */}
            <NotificationBell />

            {/* Аватар/инициалы пользователя */}
            <div className="w-8 h-8 bg-accentBlue/20 rounded-xl flex items-center justify-center">
              {user.name ? (
                <span className="text-accentBlue font-medium uppercase">{user.name
                  .split(' ')
                  .map(n => n[0])
                  .join('')
                  .toUpperCase()
                  .substring(0, 2)}
                </span>
              ) : (
                <span className="text-accentBlue font-medium uppercase">AV</span>
              )}
            </div>

            {/* Информация о пользователе */}
            <div className="space-y-1 text-left">
              <div className="text-xs font-medium whitespace-nowrap">{user.name}</div>
              <div className="flex items-center space-x-2 text-xs">
                <span className="w-2 h-2 bg-accentYellow/20 rounded">
                  <span className="w-1 h-1 bg-accentYellow rounded mx-auto mt-0.5" />
                </span>
                <span className="text-accentYellow/80 font-medium">{user.level || 0}</span>
              </div>
            </div>
          </div>

          {/* Статус онлайн/офлайн и выход */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs">
              <span className="w-2 h-2 bg-accentGreen/20 rounded">
                <span className="w-1 h-1 bg-accentGreen rounded mx-auto mt-0.5" />
              </span>
              <span>{online ? 'Онлайн' : 'Офлайн'}</span>
            </div>

            <button
              type="button"
              onClick={handleLogoutClick}
              className="
                group flex items-center space-x-2 text-xs
                cursor-pointer
                rounded-lg px-2 py-1
                text-secondary
                transition-all duration-200
                hover:bg-accentRed/10
                hover:text-accentRed
              "
            >
              <AiOutlineLogout
                className="
                  h-4 w-4
                  text-secondary/60
                  transition-colors duration-200
                  group-hover:text-accentRed
                "
              />
              <span className="ml-1">Выход</span>
            </button>
          </div>
        </div>
      </div>

      {/* Тонкая светящаяся линия снизу для эффекта глубины */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-accentBlue/20 to-transparent" />
    </header>
  );
}