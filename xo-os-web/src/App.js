import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';

import EmailVerificationPage from './pages/EmailVerificationPage';
import PasswordResetPage from './pages/PasswordResetPage';
import EmailChangePage from './pages/EmailChangePage';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ScheduleList from './components/ScheduleList';
import StatsSection from './components/StatsSection';
import DonutChart from './components/StatsSection/DonutChart';
import WeeklyChart from './components/StatsSection/WeeklyChart';
import Achievements from './components/Achievements';
import CalendarObsidianBlock from './components/CalendarObsidianBlock';
import PlayerCard from './components/PlayerCard';
import NowBlock from './components/NowBlock';
import RecentChanges from './components/RecentChanges';
import NextEvent from './components/NextEvent';
import Settings from './components/Settings';
import Login from "./components/Login";
import Onboarding from "./components/Onboarding"; // New onboarding component

function App() {
  const [section, setSection] = useState("dashboard"); // будет переопределено, если не авторизован
  const [user, setUser] = useState(false);
  const [loadingAuth, setLoadingAuth] = useState(true); // пока проверяем статус
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);

  const location = useLocation();
  useEffect(() => {
    const path = location.pathname;
    // Если путь относится к вашим обычным разделам, обновляем section
    if (path === '/dashboard') setSection('dashboard');
    else if (path === '/schedule') setSection('schedule');
    else if (path === '/stats') setSection('stats');
    else if (path === '/achievements') setSection('achievements');
    else if (path === '/settings') setSection('settings');
    // для verify/reset/change будем обрабатываться ниже через Routes
  }, [location]);

  // ---- Проверяем, авторизован ли пользователь при монтировании ----
  useEffect(() => {
    const checkAuth = async () => {
      console.log('Checking authentication...');
      try {
        const resp = await fetch("/api/auth/status", {
          credentials: "include", // отправляем куку сессии
        });
        if (!resp.ok) {
          throw new Error(`HTTP ${resp.status}`);
        }
        const data = await resp.json();
        if (data.authenticated && data.user) {
          setUser({
            ...data.user,
            onboarding_completed: data.onboarding_completed,
          });
          setSection("dashboard"); // сразу показываем дашборд
        }
        else {
          setUser(null);
        }
      } catch (e) {
        console.error("Ошибка проверки auth:", e);
        setUser(null);
      } finally {
        console.log('checkAuth finished');
        setLoadingAuth(false);
      }
    };
    checkAuth();
  }, []);

  // ---- Колбэк, который вызывается из Login после успешного входа/регистрации ----
  const handleAuthenticated = (authData) => {
    if (!authData) {
      setUser(null);
      return;
    }
    setUser({
      ...authData.user,
      onboarding_completed: authData.onboarding_completed ?? false,
    });
  };
  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {
      console.error("Logout failed", e);
    }
    setUser(null);
    setSection("dashboard");
    // Redirect to login page after logout
    window.location.href = "/login";
  };

  // Handle onboarding completion
  const handleOnboardingCompleted = () => {
    setOnboardingCompleted(true);
  };

  // Если проверка ещё идёт – показываем спиннер
  if (loadingAuth) {
    return (
      <div className="min-h-screen bg-background text-primary flex items-center justify-center">
        <div className="text-accentBlue animate-pulse">
          Запуск XO_OS...
        </div>
      </div>
    );
  }

  // Если не авторизован – показываем только экран входа
  if (!user) {
    // Неавторизованный пользователь всё ещё может видеть подтверждающие страницы
    return (
      <Routes>
        <Route path="/verify-email" element={<EmailVerificationPage />} />
        <Route path="/reset-password" element={<PasswordResetPage />} />
        <Route path="/change-email" element={<EmailChangePage />} />
        {/* Показываем login на других путях */}
        <Route path="*" element={<Login onAuthenticated={handleAuthenticated} />} />
      </Routes>
    );
  }

  // Если пользователь авторизован지만 не прошел онбординг
  if (!user.onboarding_completed && !onboardingCompleted) {
    return (
      <Onboarding
        user={user}
        handleAuthenticated={handleAuthenticated}
        onboardingCompleted={handleOnboardingCompleted}
      />
    );
  }

  // ---------- Основной интерфейс (виден только после авторизации) ----------
  return (
    <div className="min-h-screen bg-background text-primary font-sans">
      <div className="flex min-h-screen">
        <Sidebar
          onSelect={setSection}
          activeSection={section}
          user={user}
        />

        <div className="flex-1 min-w-0 flex flex-col overflow-hidden">
          <Header onLogout={handleLogout} />

          <main className="flex-1 p-6 overflow-y-auto space-y-6">
            {section === "dashboard" && (
              <div className="flex-1 min-w-0 flex flex-row space-x-4">
                {/* Left column (main content) ~65% */}
                <div className="w-[65%] flex flex-col space-y-4">
                  <PlayerCard user={user} />
                  <NowBlock />
                  <ScheduleList mode="today" />
                  <RecentChanges />
                  <div className="flex-1"></div> {/* Lower left area - free space */}
                </div>
                {/* Right column (right rail) ~35% */}
                <div className="w-[35%] flex flex-col space-y-4">
                                    <DonutChart />
                  <WeeklyChart />
                  <Achievements />
                  <div className="flex flex-col space-y-2">
                    <NextEvent />
                    <CalendarObsidianBlock />
                  </div>
                </div>
              </div>
            )}
            {section === "schedule" && <ScheduleList mode="all" />}
            {section === "stats" && <StatsSection />}
            {section === "achievements" && <Achievements />}
            {section === "settings" && <Settings />}
            {/* Дополнительные секции можно добавить здесь */}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;