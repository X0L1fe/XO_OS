import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiAlertCircle,
  FiArrowRight,
  FiCheckCircle,
  FiEye,
  FiEyeOff,
  FiKey,
  FiLoader,
  FiLock,
  FiShield,
} from "react-icons/fi";
import axios from "axios";

const PasswordResetPage = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState("form");
  const [form, setForm] = useState({
    password: "",
    confirm: "",
    token: "",
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    setForm((prev) => ({
      ...prev,
      token: token || "",
    }));

    if (!token) {
      setErrors({
        token: "Ссылка сброса не содержит токена.",
      });
    }
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: "",
      submit: "",
      token: prev.token,
    }));
  };

  const getErrorMessage = (error) => {
    return (
      error.response?.data?.message ||
      error.response?.data?.detail ||
      "Не удалось изменить пароль. Попробуйте ещё раз."
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (submitting) {
      return;
    }

    const nextErrors = {};

    if (!form.token) {
      nextErrors.token = "Отсутствует токен сброса пароля.";
    }

    if (!form.password) {
      nextErrors.password = "Введите новый пароль.";
    }

    if (!form.confirm) {
      nextErrors.confirm = "Повторите новый пароль.";
    }

    if (
      form.password &&
      form.confirm &&
      form.password !== form.confirm
    ) {
      nextErrors.confirm = "Пароли не совпадают.";
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setSubmitting(true);
    setErrors({});

    try {
      await axios.post(
        "/api/auth/reset-password",
        form,
        {
          withCredentials: true,
        }
      );

      setMessage(
        "Пароль успешно изменён. Теперь можно войти в аккаунт."
      );

      setStep("success");
    } catch (error) {
      console.error("Password reset failed:", error);

      setErrors({
        submit: getErrorMessage(error),
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (step === "success") {
    return (
      <AuthShell>
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-green/20 bg-accent-green/10 text-accent-green">
            <FiCheckCircle className="h-8 w-8" />
          </div>

          <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-green">
            XO_OS / SECURITY
          </p>

          <h1 className="mt-3 text-2xl font-bold text-text-primary">
            Пароль изменён
          </h1>

          <p className="mt-3 text-sm leading-6 text-text-secondary">
            {message}
          </p>

          <div className="mt-5 rounded-xl border border-border bg-background/50 p-4 text-left">
            <div className="flex items-start gap-3">
              <FiShield className="mt-0.5 h-4 w-4 shrink-0 text-accent-blue" />

              <p className="text-xs leading-5 text-text-muted">
                Используйте новый пароль при следующем входе.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate("/login")}
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-accent-blue px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-accent-blue/10 transition-colors hover:bg-accent-blue/90"
          >
            Перейти ко входу
            <FiArrowRight className="h-4 w-4" />
          </button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell>
      <div>
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-blue/20 bg-accent-blue/10 text-accent-blue">
            <FiKey className="h-8 w-8" />
          </div>

          <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-blue">
            XO_OS / SECURITY
          </p>

          <h1 className="mt-3 text-2xl font-bold text-text-primary">
            Новый пароль
          </h1>

          <p className="mt-3 text-sm leading-6 text-text-secondary">
            Создайте новый пароль для своего аккаунта.
          </p>
        </div>

        {errors.token && (
          <div className="mt-5 flex items-start gap-3 rounded-xl border border-accent-red/20 bg-accent-red/5 p-3.5">
            <FiAlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-accent-red" />

            <p className="text-xs leading-5 text-accent-red">
              {errors.token}
            </p>
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="mt-7 space-y-5"
        >
          <PasswordField
            id="password"
            name="password"
            label="Новый пароль"
            value={form.password}
            onChange={handleChange}
            error={errors.password}
            visible={showPassword}
            onToggleVisibility={() =>
              setShowPassword((value) => !value)
            }
            autoComplete="new-password"
          />

          <PasswordField
            id="confirm"
            name="confirm"
            label="Подтвердите пароль"
            value={form.confirm}
            onChange={handleChange}
            error={errors.confirm}
            visible={showConfirm}
            onToggleVisibility={() =>
              setShowConfirm((value) => !value)
            }
            autoComplete="new-password"
          />

          {errors.submit && (
            <div className="flex items-start gap-3 rounded-xl border border-accent-red/20 bg-accent-red/5 p-3.5">
              <FiAlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-accent-red" />

              <p className="text-xs leading-5 text-accent-red">
                {errors.submit}
              </p>
            </div>
          )}

          <div className="rounded-xl border border-border bg-background/50 p-4">
            <div className="flex items-start gap-3">
              <FiLock className="mt-0.5 h-4 w-4 shrink-0 text-accent-blue" />

              <div>
                <p className="text-xs font-medium text-text-primary">
                  Защита аккаунта
                </p>

                <p className="mt-1 text-xs leading-5 text-text-muted">
                  После смены пароля используйте только новый пароль для
                  входа в XO_OS.
                </p>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting || !form.token}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent-blue px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-accent-blue/10 transition-all hover:bg-accent-blue/90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {submitting ? (
              <>
                <FiLoader className="h-4 w-4 animate-spin" />
                Сохраняем...
              </>
            ) : (
              <>
                Сохранить пароль
                <FiArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </AuthShell>
  );
};

function AuthShell({ children }) {
  return (
    <div className="min-h-screen bg-background px-4 py-6 text-text-primary sm:px-6">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-180px] h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-accent-blue/10 blur-3xl" />
      </div>

      <div className="relative flex min-h-[calc(100vh-3rem)] items-center justify-center">
        <div className="w-full max-w-md">
          <div className="mb-5 flex items-center justify-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-accent-blue/20 bg-accent-blue/10 text-accent-blue">
              <FiKey className="h-4 w-4" />
            </div>

            <span className="text-sm font-semibold tracking-tight text-text-primary">
              XO_OS
            </span>
          </div>

          <div className="rounded-2xl border border-border bg-panel p-7 shadow-2xl shadow-black/20 sm:p-8">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

function PasswordField({
  id,
  name,
  label,
  value,
  onChange,
  error,
  visible,
  onToggleVisibility,
  autoComplete,
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-2 block text-xs font-medium text-text-secondary"
      >
        {label}
      </label>

      <div className="relative">
        <FiLock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />

        <input
          id={id}
          name={name}
          type={visible ? "text" : "password"}
          value={value}
          onChange={onChange}
          placeholder="••••••••"
          autoComplete={autoComplete}
          className={`w-full rounded-xl border bg-background/70 py-3 pl-10 pr-12 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted ${
            error
              ? "border-accent-red/40 focus:border-accent-red/60 focus:ring-2 focus:ring-accent-red/10"
              : "border-border focus:border-accent-blue/50 focus:ring-2 focus:ring-accent-blue/10"
          }`}
        />

        <button
          type="button"
          onClick={onToggleVisibility}
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1 text-text-muted transition-colors hover:bg-card hover:text-text-primary"
          aria-label={
            visible ? "Скрыть пароль" : "Показать пароль"
          }
        >
          {visible ? (
            <FiEyeOff className="h-4 w-4" />
          ) : (
            <FiEye className="h-4 w-4" />
          )}
        </button>
      </div>

      {error && (
        <p className="mt-1.5 text-xs text-accent-red">
          {error}
        </p>
      )}
    </div>
  );
}

export default PasswordResetPage;