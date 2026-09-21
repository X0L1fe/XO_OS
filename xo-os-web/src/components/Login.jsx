import React, { useState } from "react";
import {
  FiLogIn,
  FiUserPlus,
  FiLock,
  FiMail,
  FiUser,
  FiEye,
  FiEyeOff,
} from "react-icons/fi";

import Logo from "../assets/logo.svg";

const Login = ({ onAuthenticated }) => {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const isLogin = mode === "login";

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError(null);

    try {
      let res;

      if (isLogin) {
        res = await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email,
            password,
          }),
        });
      } else {
        res = await fetch("/api/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email,
            password,
            name,
          }),
        });
      }

      if (!res.ok) {
        const data = await res.json();

        console.error("Auth error:", data);

        let message = "Ошибка запроса";

        if (typeof data.detail === "string") {
          message = data.detail;
        } else if (Array.isArray(data.detail)) {
          message = data.detail
            .map((item) => {
              const field = item.loc?.slice(-1)[0] || "field";
              return `${field}: ${item.msg}`;
            })
            .join("\n");
        } else if (data.message) {
          message = data.message;
        }

        throw new Error(message);
      }

      const authResponse = await fetch("/api/auth/status", {
        credentials: "include",
      });

      if (!authResponse.ok) {
        throw new Error(
          "Не удалось проверить созданную сессию"
        );
      }

      const authData = await authResponse.json();

      if (!authData.authenticated || !authData.user) {
        throw new Error(
          "Сервер не подтвердил авторизацию"
        );
      }

      onAuthenticated(authData);
    } catch (err) {
      console.error(err);
      setError(err.message || "Неизвестная ошибка");
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (newMode) => {
    if (loading) return;

    setMode(newMode);
    setError(null);

    // Не обязательно, но UX приятнее:
    setPassword("");
  };

  return (
    <div className="min-h-screen bg-background text-primary flex items-center justify-center px-6 py-10 relative overflow-hidden">
      {/* Ambient glow */}
      <div
        className="
          absolute
          w-[500px]
          h-[500px]
          rounded-full
          bg-accentBlue/10
          blur-[140px]
          pointer-events-none
        "
      />

      <div className="relative w-full max-w-md">
        {/* Main card */}
        <div
          className="
            bg-panel
            border border-border
            rounded-2xl
            p-8
            shadow-[0_20px_80px_rgba(0,0,0,0.35)]
          "
        >
          {/* Logo */}
          <div className="flex justify-center mb-7">
            <img
              src={Logo}
              alt="XO_OS"
              className="w-36 h-auto"
            />
          </div>

          {/* Heading */}
          <div className="text-center mb-7">
            <h1 className="text-2xl font-semibold tracking-tight">
              {isLogin
                ? "С возвращением"
                : "Создай свой профиль"}
            </h1>

            <p className="text-sm text-secondary mt-2">
              {isLogin
                ? "Войди в XO_OS и продолжи свой путь."
                : "Начни строить свою персональную систему."}
            </p>
          </div>

          {/* Mode switch */}
          <div
            className="
              flex
              p-1
              mb-7
              bg-background
              border border-border
              rounded-xl
            "
          >
            <button
              type="button"
              disabled={loading}
              onClick={() => switchMode("login")}
              className={`
                flex-1
                flex items-center justify-center gap-2
                py-2.5
                rounded-lg
                text-sm
                transition-all
                duration-200
                ${isLogin
                  ? "bg-accentBlue/15 text-accentBlue border border-accentBlue/20"
                  : "text-secondary hover:text-primary"
                }
              `}
            >
              <FiLogIn size={15} />
              Войти
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => switchMode("register")}
              className={`
                flex-1
                flex items-center justify-center gap-2
                py-2.5
                rounded-lg
                text-sm
                transition-all
                duration-200
                ${!isLogin
                  ? "bg-accentBlue/15 text-accentBlue border border-accentBlue/20"
                  : "text-secondary hover:text-primary"
                }
              `}
            >
              <FiUserPlus size={15} />
              Регистрация
            </button>
          </div>

          {/* Error */}
          {error && (
            <div
              className="
                mb-5
                px-4
                py-3
                rounded-xl
                border border-accentRed/30
                bg-accentRed/10
                text-accentRed
                text-sm
              "
            >
              {error}
            </div>
          )}

          {/* Form */}
          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >
            {/* Name */}
            {!isLogin && (
              <div>
                <label className="block text-xs font-medium text-secondary mb-2">
                  Имя
                </label>

                <div className="relative">
                  <FiUser
                    size={17}
                    className="
                      absolute
                      left-4
                      top-1/2
                      -translate-y-1/2
                      text-secondary
                    "
                  />

                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={loading}
                    placeholder="Как тебя зовут?"
                    className="
                      w-full
                      pl-11 pr-4 py-3
                      bg-background
                      border border-border
                      rounded-xl
                      text-primary
                      placeholder:text-secondary/40
                      focus:outline-none
                      focus:border-accentBlue
                      focus:ring-1
                      focus:ring-accentBlue/30
                      transition-all
                    "
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-xs font-medium text-secondary mb-2">
                Электронная почта
              </label>

              <div className="relative">
                <FiMail
                  size={17}
                  className="
                    absolute
                    left-4
                    top-1/2
                    -translate-y-1/2
                    text-secondary
                  "
                />

                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  placeholder="you@example.com"
                  className="
                    w-full
                    pl-11 pr-4 py-3
                    bg-background
                    border border-border
                    rounded-xl
                    text-primary
                    placeholder:text-secondary/40
                    focus:outline-none
                    focus:border-accentBlue
                    focus:ring-1
                    focus:ring-accentBlue/30
                    transition-all
                  "
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-medium text-secondary mb-2">
                Пароль
              </label>

              <div className="relative">
                <FiLock
                  size={17}
                  className="
                    absolute
                    left-4
                    top-1/2
                    -translate-y-1/2
                    text-secondary
                  "
                />

                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  placeholder="••••••••"
                  className="
                    w-full
                    pl-11 pr-12 py-3
                    bg-background
                    border border-border
                    rounded-xl
                    text-primary
                    placeholder:text-secondary/40
                    focus:outline-none
                    focus:border-accentBlue
                    focus:ring-1
                    focus:ring-accentBlue/30
                    transition-all
                  "
                />

                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  disabled={loading}
                  className="
                    absolute
                    right-4
                    top-1/2
                    -translate-y-1/2
                    text-secondary
                    hover:text-primary
                    transition-colors
                  "
                >
                  {showPassword ? (
                    <FiEyeOff size={17} />
                  ) : (
                    <FiEye size={17} />
                  )}
                </button>
              </div>
            </div>

            {/* Login-only helper */}
            {isLogin && (
              <div className="flex justify-end">
                <button
                  type="button"
                  disabled={loading}
                  className="
                    text-xs
                    text-secondary
                    hover:text-accentBlue
                    transition-colors
                  "
                >
                  Забыли пароль?
                </button>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="
                w-full
                py-3.5
                rounded-xl
                bg-accentBlue
                hover:bg-accentBlue/90
                disabled:opacity-50
                disabled:cursor-not-allowed
                text-white
                font-medium
                transition-all
                duration-200
                flex
                items-center
                justify-center
                gap-2
                shadow-[0_8px_30px_rgba(30,130,255,0.15)]
              "
            >
              {isLogin ? (
                <FiLogIn size={17} />
              ) : (
                <FiUserPlus size={17} />
              )}

              {loading
                ? "Подождите..."
                : isLogin
                  ? "Войти в XO_OS"
                  : "Создать аккаунт"}
            </button>
          </form>

          {/* Bottom switch */}
          <div className="mt-7 text-center">
            <span className="text-sm text-secondary">
              {isLogin
                ? "Нет аккаунта?"
                : "Уже есть аккаунт?"}
            </span>{" "}
            <button
              type="button"
              disabled={loading}
              onClick={() =>
                switchMode(isLogin ? "register" : "login")
              }
              className="
                text-sm
                text-accentYellow
                hover:text-accentYellow/80
                transition-colors
              "
            >
              {isLogin
                ? "Зарегистрироваться"
                : "Войти"}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-5">
          <span className="text-xs text-secondary">
            XO_OS · Personal Operating System
          </span>
        </div>
      </div>
    </div>
  );
};

export default Login;