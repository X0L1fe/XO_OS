import React, { useState } from "react";
import {
  FiAlertCircle,
  FiCheckCircle,
  FiEye,
  FiEyeOff,
  FiLoader,
  FiLock,
  FiLogIn,
  FiMail,
  FiShield,
  FiUser,
  FiUserPlus,
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
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [registrationMessage, setRegistrationMessage] = useState("");

  const isLogin = mode === "login";

  const parseApiError = async (response) => {
    try {
      const data = await response.json();

      if (typeof data.detail === "string") {
        return data.detail;
      }

      if (Array.isArray(data.detail)) {
        return data.detail
          .map((item) => {
            const field = item.loc?.slice(-1)[0] || "field";
            return `${field}: ${item.msg}`;
          })
          .join("\n");
      }

      if (typeof data.message === "string") {
        return data.message;
      }

      return "Ошибка запроса";
    } catch {
      return `HTTP ${response.status}`;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      /*
       * LOGIN
       */
      if (isLogin) {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email: email.trim(),
            password,
          }),
        });

        if (!response.ok) {
          const message = await parseApiError(response);
          throw new Error(message);
        }

        /*
         * После логина сервер должен создать session_token.
         * Теперь проверяем состояние авторизации.
         */
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

        return;
      }

      /*
       * REGISTRATION
       */
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email: email.trim(),
          password,
          name: name.trim(),
        }),
      });

      if (!response.ok) {
        const message = await parseApiError(response);
        throw new Error(message);
      }

      const data = await response.json();

      /*
       * ВАЖНО:
       *
       * REGISTER НЕ АВТОРИЗУЕТ ПОЛЬЗОВАТЕЛЯ.
       * Backend специально НЕ создаёт session.
       *
       * Поэтому здесь нельзя делать /api/auth/status
       * и нельзя вызывать onAuthenticated().
       */
      setRegistrationMessage(
        data?.message ||
          "Проверочное письмо отправлено на вашу электронную почту. Проверьте почту и перейдите по ссылке для подтверждения аккаунта."
      );

      setRegistrationSuccess(true);

      /*
       * Пароль очищаем, email оставляем,
       * чтобы после подтверждения пользователю было удобно войти.
       */
      setPassword("");
    } catch (err) {
      console.error(err);

      setError(
        err.message || "Неизвестная ошибка"
      );
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (newMode) => {
    if (loading) {
      return;
    }

    setMode(newMode);
    setError(null);
    setRegistrationSuccess(false);
    setRegistrationMessage("");
    setPassword("");
  };

  /*
   * REGISTRATION SUCCESS SCREEN
   */
  if (registrationSuccess) {
    return (
      <div
        className="
          relative
          flex
          min-h-screen
          items-center
          justify-center
          overflow-hidden
          bg-background
          px-5
          py-10
          text-primary
        "
      >
        {/* Ambient background */}
        <div
          className="
            pointer-events-none
            absolute
            left-1/2
            top-1/2
            h-[520px]
            w-[520px]
            -translate-x-1/2
            -translate-y-1/2
            rounded-full
            bg-accentBlue/8
            blur-[150px]
          "
        />

        <div className="relative w-full max-w-md">
          <div
            className="
              overflow-hidden
              rounded-3xl
              border
              border-border
              bg-panel/95
              shadow-[0_24px_100px_rgba(0,0,0,0.42)]
              backdrop-blur-xl
            "
          >
            <div className="h-px w-full bg-gradient-to-r from-transparent via-accentBlue/60 to-transparent" />

            <div className="p-7 text-center sm:p-8">
              {/* Logo */}
              <div className="mb-8 flex justify-center">
                <div
                  className="
                    rounded-2xl
                    border
                    border-border
                    bg-background/50
                    px-5
                    py-3
                    shadow-[0_8px_30px_rgba(0,0,0,0.18)]
                  "
                >
                  <img
                    src={Logo}
                    alt="XO_OS"
                    className="h-auto w-32"
                  />
                </div>
              </div>

              {/* Success icon */}
              <div
                className="
                  mx-auto
                  flex
                  h-16
                  w-16
                  items-center
                  justify-center
                  rounded-2xl
                  border
                  border-accentGreen/20
                  bg-accentGreen/10
                  text-accentGreen
                "
              >
                <FiCheckCircle size={30} />
              </div>

              <p
                className="
                  mt-6
                  text-[11px]
                  font-semibold
                  uppercase
                  tracking-[0.18em]
                  text-accentGreen
                "
              >
                XO_OS / ACCOUNT
              </p>

              <h1 className="mt-3 text-2xl font-semibold tracking-tight text-primary">
                Аккаунт создан
              </h1>

              <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-secondary">
                {registrationMessage}
              </p>

              {/* Email */}
              <div
                className="
                  mt-6
                  flex
                  items-center
                  gap-3
                  rounded-xl
                  border
                  border-border
                  bg-background/50
                  px-4
                  py-3
                  text-left
                "
              >
                <FiMail
                  size={17}
                  className="shrink-0 text-accentBlue"
                />

                <div className="min-w-0">
                  <p className="text-[10px] uppercase tracking-wide text-secondary">
                    Email
                  </p>

                  <p className="mt-0.5 truncate text-sm font-medium text-primary">
                    {email}
                  </p>
                </div>
              </div>

              {/* Info */}
              <div
                className="
                  mt-4
                  rounded-xl
                  border
                  border-accentBlue/15
                  bg-accentBlue/5
                  p-4
                  text-left
                "
              >
                <div className="flex items-start gap-3">
                  <FiShield
                    size={16}
                    className="mt-0.5 shrink-0 text-accentBlue"
                  />

                  <p className="text-xs leading-5 text-secondary">
                    Откройте письмо и перейдите по ссылке
                    подтверждения. После этого аккаунт можно будет
                    использовать для входа в XO_OS.
                  </p>
                </div>
              </div>

              {/* Login */}
              <button
                type="button"
                onClick={() => switchMode("login")}
                className="
                  mt-6
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
                  py-3.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-[0_10px_30px_rgba(30,130,255,0.14)]
                  transition-all
                  duration-200
                  hover:-translate-y-0.5
                  hover:bg-accentBlue/90
                "
              >
                <FiLogIn size={17} />
                Перейти ко входу
              </button>
            </div>
          </div>

          <div className="mt-5 text-center">
            <span className="text-[11px] tracking-wide text-secondary/70">
              XO_OS · Personal Operating System
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="
        relative
        flex
        min-h-screen
        items-center
        justify-center
        overflow-hidden
        bg-background
        px-5
        py-10
        text-primary
      "
    >
      {/* Ambient background */}
      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-1/2
          h-[520px]
          w-[520px]
          -translate-x-1/2
          -translate-y-1/2
          rounded-full
          bg-accentBlue/8
          blur-[150px]
        "
      />

      <div
        className="
          pointer-events-none
          absolute
          left-[18%]
          top-[20%]
          h-32
          w-32
          rounded-full
          bg-accentYellow/4
          blur-[90px]
        "
      />

      <div className="relative w-full max-w-md">
        {/* Main card */}
        <div
          className="
            overflow-hidden
            rounded-3xl
            border
            border-border
            bg-panel/95
            shadow-[0_24px_100px_rgba(0,0,0,0.42)]
            backdrop-blur-xl
          "
        >
          {/* Top accent */}
          <div className="h-px w-full bg-gradient-to-r from-transparent via-accentBlue/60 to-transparent" />

          <div className="p-7 sm:p-8">
            {/* Logo */}
            <div className="mb-8 flex justify-center">
              <div
                className="
                  rounded-2xl
                  border
                  border-border
                  bg-background/50
                  px-5
                  py-3
                  shadow-[0_8px_30px_rgba(0,0,0,0.18)]
                "
              >
                <img
                  src={Logo}
                  alt="XO_OS"
                  className="h-auto w-32"
                />
              </div>
            </div>

            {/* Heading */}
            <div className="mb-7 text-center">
              <div
                className="
                  mx-auto
                  mb-4
                  flex
                  h-10
                  w-10
                  items-center
                  justify-center
                  rounded-xl
                  border
                  border-accentBlue/20
                  bg-accentBlue/10
                  text-accentBlue
                "
              >
                <FiShield size={17} />
              </div>

              <h1 className="text-2xl font-semibold tracking-tight text-primary">
                {isLogin
                  ? "С возвращением"
                  : "Создай свой профиль"}
              </h1>

              <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-secondary">
                {isLogin
                  ? "Войди в XO_OS и продолжи свой путь."
                  : "Начни строить свою персональную систему."}
              </p>
            </div>

            {/* Mode switch */}
            <div
              className="
                mb-7
                grid
                grid-cols-2
                gap-1
                rounded-xl
                border
                border-border
                bg-background/60
                p-1
              "
            >
              <button
                type="button"
                disabled={loading}
                onClick={() => switchMode("login")}
                className={`
                  flex
                  items-center
                  justify-center
                  gap-2
                  rounded-lg
                  px-3
                  py-2.5
                  text-sm
                  font-medium
                  transition-all
                  duration-300
                  ease-out
                  disabled:cursor-not-allowed

                  ${
                    isLogin
                      ? "border border-accentBlue/20 bg-accentBlue/10 text-accentBlue shadow-[0_4px_18px_rgba(30,130,255,0.08)]"
                      : "border border-transparent text-secondary hover:bg-white/[0.03] hover:text-primary"
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
                  flex
                  items-center
                  justify-center
                  gap-2
                  rounded-lg
                  px-3
                  py-2.5
                  text-sm
                  font-medium
                  transition-all
                  duration-300
                  ease-out
                  disabled:cursor-not-allowed

                  ${
                    !isLogin
                      ? "border border-accentBlue/20 bg-accentBlue/10 text-accentBlue shadow-[0_4px_18px_rgba(30,130,255,0.08)]"
                      : "border border-transparent text-secondary hover:bg-white/[0.03] hover:text-primary"
                  }
                `}
              >
                <FiUserPlus size={15} />
                Регистрация
              </button>
            </div>

            {/* Error */}
            <div
              className={`
                overflow-hidden
                transition-all
                duration-300
                ease-out

                ${
                  error
                    ? "mb-5 max-h-40 opacity-100"
                    : "mb-0 max-h-0 opacity-0"
                }
              `}
            >
              <div
                className="
                  flex
                  items-start
                  gap-3
                  rounded-xl
                  border
                  border-accentRed/20
                  bg-accentRed/8
                  px-4
                  py-3
                  text-sm
                  leading-5
                  text-accentRed
                "
              >
                <FiAlertCircle
                  size={16}
                  className="mt-0.5 shrink-0"
                />

                <span className="whitespace-pre-line">
                  {error}
                </span>
              </div>
            </div>

            {/* Form */}
            <form
              onSubmit={handleSubmit}
              className="space-y-5"
            >
              {/* Name */}
              {!isLogin && (
                <div>
                  <label className="mb-2 block text-xs font-medium text-secondary">
                    Имя
                  </label>

                  <div className="group relative">
                    <FiUser
                      size={17}
                      className="
                        pointer-events-none
                        absolute
                        left-4
                        top-1/2
                        -translate-y-1/2
                        text-secondary
                        transition-colors
                        duration-200
                        group-focus-within:text-accentBlue
                      "
                    />

                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) =>
                        setName(e.target.value)
                      }
                      disabled={loading}
                      placeholder="Как тебя зовут?"
                      className="
                        w-full
                        rounded-xl
                        border
                        border-border
                        bg-background
                        py-3
                        pl-11
                        pr-4
                        text-sm
                        text-primary
                        outline-none
                        transition-all
                        duration-200
                        placeholder:text-secondary/35
                        hover:border-border/80
                        focus:border-accentBlue/60
                        focus:bg-background/80
                        focus:ring-4
                        focus:ring-accentBlue/10
                        disabled:cursor-not-allowed
                        disabled:opacity-50
                      "
                    />
                  </div>
                </div>
              )}

              {/* Email */}
              <div>
                <label className="mb-2 block text-xs font-medium text-secondary">
                  Электронная почта
                </label>

                <div className="group relative">
                  <FiMail
                    size={17}
                    className="
                      pointer-events-none
                      absolute
                      left-4
                      top-1/2
                      -translate-y-1/2
                      text-secondary
                      transition-colors
                      duration-200
                      group-focus-within:text-accentBlue
                    "
                  />

                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) =>
                      setEmail(e.target.value)
                    }
                    disabled={loading}
                    placeholder="you@example.com"
                    autoComplete="email"
                    className="
                      w-full
                      rounded-xl
                      border
                      border-border
                      bg-background
                      py-3
                      pl-11
                      pr-4
                      text-sm
                      text-primary
                      outline-none
                      transition-all
                      duration-200
                      placeholder:text-secondary/35
                      hover:border-border/80
                      focus:border-accentBlue/60
                      focus:bg-background/80
                      focus:ring-4
                      focus:ring-accentBlue/10
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                    "
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="mb-2 block text-xs font-medium text-secondary">
                  Пароль
                </label>

                <div className="group relative">
                  <FiLock
                    size={17}
                    className="
                      pointer-events-none
                      absolute
                      left-4
                      top-1/2
                      -translate-y-1/2
                      text-secondary
                      transition-colors
                      duration-200
                      group-focus-within:text-accentBlue
                    "
                  />

                  <input
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    required
                    value={password}
                    onChange={(e) =>
                      setPassword(e.target.value)
                    }
                    disabled={loading}
                    placeholder="••••••••"
                    autoComplete={
                      isLogin
                        ? "current-password"
                        : "new-password"
                    }
                    className="
                      w-full
                      rounded-xl
                      border
                      border-border
                      bg-background
                      py-3
                      pl-11
                      pr-12
                      text-sm
                      text-primary
                      outline-none
                      transition-all
                      duration-200
                      placeholder:text-secondary/35
                      hover:border-border/80
                      focus:border-accentBlue/60
                      focus:bg-background/80
                      focus:ring-4
                      focus:ring-accentBlue/10
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                    "
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword((prev) => !prev)
                    }
                    disabled={loading}
                    aria-label={
                      showPassword
                        ? "Скрыть пароль"
                        : "Показать пароль"
                    }
                    className="
                      absolute
                      right-3
                      top-1/2
                      flex
                      h-8
                      w-8
                      -translate-y-1/2
                      items-center
                      justify-center
                      rounded-lg
                      text-secondary
                      transition-all
                      duration-200
                      hover:bg-white/[0.04]
                      hover:text-primary
                      active:scale-95
                      disabled:cursor-not-allowed
                      disabled:opacity-50
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

              {/* Forgot password */}
              {isLogin && (
                <div className="flex justify-end">
                  <button
                    type="button"
                    disabled={loading}
                    className="
                      text-xs
                      font-medium
                      text-secondary
                      transition-colors
                      duration-200
                      hover:text-accentBlue
                      disabled:cursor-not-allowed
                      disabled:opacity-50
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
                  py-3.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-[0_10px_30px_rgba(30,130,255,0.14)]
                  transition-all
                  duration-200
                  ease-out
                  hover:-translate-y-0.5
                  hover:bg-accentBlue/90
                  hover:shadow-[0_14px_36px_rgba(30,130,255,0.2)]
                  active:translate-y-0
                  active:scale-[0.99]
                  disabled:cursor-not-allowed
                  disabled:opacity-55
                  disabled:hover:translate-y-0
                  disabled:hover:shadow-none
                "
              >
                {loading ? (
                  <FiLoader
                    size={17}
                    className="animate-spin"
                  />
                ) : isLogin ? (
                  <FiLogIn size={17} />
                ) : (
                  <FiUserPlus size={17} />
                )}

                <span>
                  {loading
                    ? "Подождите..."
                    : isLogin
                      ? "Войти в XO_OS"
                      : "Создать аккаунт"}
                </span>
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
                  switchMode(
                    isLogin
                      ? "register"
                      : "login"
                  )
                }
                className="
                  ml-1
                  text-sm
                  font-medium
                  text-accentYellow
                  transition-all
                  duration-200
                  hover:text-accentYellow/80
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                {isLogin
                  ? "Зарегистрироваться"
                  : "Войти"}
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-5 text-center">
          <span className="text-[11px] tracking-wide text-secondary/70">
            XO_OS · Personal Operating System
          </span>
        </div>
      </div>
    </div>
  );
};

export default Login;