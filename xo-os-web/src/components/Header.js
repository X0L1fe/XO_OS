import React, { useEffect, useState } from 'react';
import { AiOutlineLogout, AiOutlineSearch } from 'react-icons/ai';

export default function Header({ onLogout }) {
  const [user, setUser] = useState(null);
  const [syncStatus, setSyncStatus] = useState('Синхронизировано');
  const [lastCheck, setLastCheck] = useState('сегодня 14:32');
  const [online, setOnline] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const resp = await fetch('/api/auth/me', {
          credentials: 'include'
        });
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

    const fetchStatus = async () => {
      try {
        const syncResp = await fetch('/api/google/status', { credentials: 'include' });
        if (syncResp.ok) {
          const syncData = await syncResp.json();
          setSyncStatus(syncData.connected ? 'Синхронизировано' : 'Не синхронизировано');
        }
        const onlineResp = await fetch('/api/health', { credentials: 'include' });
        if (onlineResp.ok) {
          setOnline(true);
        } else {
          setOnline(false);
        }
        // Update last check time
        setLastCheck(new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }));
      } catch (e) {
        console.error('Failed to fetch status', e);
      }
    };

    fetchUser();
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
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

  return (
    <header className="bg-panel/80 backdrop-blur-sm border-b border-border/50 relative">
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
          {/* Статус синхронизации */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="w-2.5 h-2.5 bg-accentGreen/20 rounded">
              <span className="w-1.5 h-1.5 bg-accentGreen rounded mx-auto mt-0.5" />
            </span>
            <span className="whitespace-nowrap">{syncStatus}</span>
          </div>

          {/* Время последней проверки */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-secondary/60">Последняя проверка:</span>
            <span className="whitespace-nowrap font-mono">{lastCheck}</span>
          </div>

          {/* Область пользователя как профиль/статус */}
          <div className="relative flex items-center space-x-3">
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

            <div className="flex items-center space-x-2 text-xs cursor-pointer hover:text-accentBlue transition-colors duration-200" onClick={handleLogoutClick}>
              <AiOutlineLogout className="h-4 w-4 text-secondary/60" />
              <span className="ml-1">Выход</span>
            </div>
          </div>
        </div>
      </div>

      {/* Тонкая светящаяся линия снизу для эффекта глубины */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-accentBlue/20 to-transparent" />
    </header>
  );
}