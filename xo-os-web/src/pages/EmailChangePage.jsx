import React, { useEffect, useMemo, useState } from "react";
import {
  FiAlertCircle,
  FiArrowLeft,
  FiArrowRight,
  FiCheckCircle,
  FiLoader,
  FiLock,
  FiMail,
  FiShield,
  FiCheck,
} from "react-icons/fi";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

const EmailChangePage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState("confirmIntent");
  const [form, setForm] = useState({
    intentToken: "",
    newEmail: "",
    password: "",
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");

    if (!token) {
      setErrors({
        intentToken: "Отсутствует токен подтверждения.",
      });
      return;
    }

    setForm((prev) => ({
      ...prev,
      intentToken: token,
    }));

    setErrors((prev) => ({
      ...prev,
      intentToken: "",
    }));
  }, [location.search]);

  const title = useMemo(() => {
    switch (step) {
      case "confirmIntent":
        return "Подтверждение смены email";
      case "enterNew":
        return "Новый email";
      default:
        return "Запрос отправлен";
    }
  }, [step]);

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
    }));
  };

  const getErrorMessage = (error, fallback) => {
    return (
      error.response?.data?.message ||
      error.response?.data?.detail ||
      fallback
    );
  };

  const handleConfirmIntent = async () => {
    if (!form.intentToken) {
      setErrors({
        intentToken: "Токен подтверждения отсутствует.",
      });
      return;
    }

    if (submitting) {
      return;
    }

    setSubmitting(true);
    setErrors({});

    try {
      await axios.post(
        "/api/auth/confirm-email-change-intent",
        {
          token: form.intentToken,
        },
        {
          withCredentials: true,
        }
      );

      setStep("enterNew");
    } catch (error) {
      console.error("Failed to confirm email change intent:", error);

      setErrors({
        submit: getErrorMessage(
          error,
          "Не удалось подтвердить намерение изменить email."
        ),
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitNewEmail = async (event) => {
    event.preventDefault();

    if (submitting) {
      return;
    }

    const nextErrors = {};

    const email = form.newEmail.trim();

    if (!email) {
      nextErrors.newEmail = "Введите новый email.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      nextErrors.newEmail = "Некорректный формат email.";
    }

    if (!form.password) {
      nextErrors.password = "Введите текущий пароль.";
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setSubmitting(true);
    setErrors({});

    try {
      await axios.post(
        "/api/auth/request-email-change",
        {
          intentToken: form.intentToken,
          newEmail: email,
          password: form.password,
        },
        {
          withCredentials: true,
        }
      );

      setMessage(
        "На новый email отправлено письмо с подтверждением."
      );

      setStep("success");
    } catch (error) {
      console.error("Failed to request email change:", error);

      setErrors({
        submit: getErrorMessage(
          error,
          "Не удалось отправить запрос на смену email."
        ),
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (step === "success") {
    return (
      <AuthShell>
        <div className="text-center">
          <StatusIcon success />

          <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-green">
            XO_OS / EMAIL CHANGE
          </p>

          <h1 className="mt-3 text-2xl font-bold text-text-primary">
            Запрос отправлен
          </h1>

          <p className="mt-3 text-sm leading-6 text-text-secondary">
            {message}
          </p>

          <div className="mt-5 rounded-xl border border-border bg-background/50 p-4 text-left">
            <div className="flex items-start gap-3">
              <FiShield className="mt-0.5 h-4 w-4 shrink-0 text-accent-blue" />

              <p className="text-xs leading-5 text-text-muted">
                Откройте письмо и перейдите по ссылке подтверждения.
                После подтверждения новый адрес будет установлен как
                основной email аккаунта.
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

  if (step === "confirmIntent") {
    return (
      <AuthShell>
        <div>
          <StepIndicator current={1} />

          <div className="mt-8 text-center">
            <StatusIcon intent />

            <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-blue">
              XO_OS / SECURITY
            </p>

            <h1 className="mt-3 text-2xl font-bold text-text-primary">
              {title}
            </h1>

            <p className="mt-3 text-sm leading-6 text-text-secondary">
              Мы получили запрос на изменение вашего электронного адреса.
              Подтвердите, что хотите продолжить.
            </p>
          </div>

          {errors.intentToken && (
            <InlineError message={errors.intentToken} />
          )}

          {errors.submit && (
            <InlineError message={errors.submit} />
          )}

          <div className="mt-6 space-y-3">
            <button
              type="button"
              onClick={handleConfirmIntent}
              disabled={submitting || !form.intentToken}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent-blue px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-accent-blue/10 transition-all hover:bg-accent-blue/90 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {submitting ? (
                <>
                  <FiLoader className="h-4 w-4 animate-spin" />
                  Проверяем...
                </>
              ) : (
                <>
                  Продолжить
                  <FiArrowRight className="h-4 w-4" />
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => navigate("/")}
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-border bg-background px-4 py-3 text-sm font-medium text-text-secondary transition-colors hover:border-accent-blue/30 hover:bg-card hover:text-text-primary disabled:opacity-50"
            >
              <FiArrowLeft className="h-4 w-4" />
              Отменить
            </button>
          </div>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell>
      <div>
        <StepIndicator current={2} />

        <div className="mt-8">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-blue">
            XO_OS / EMAIL CHANGE
          </p>

          <h1 className="mt-3 text-2xl font-bold text-text-primary">
            {title}
          </h1>

          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Укажите новый email и текущий пароль для подтверждения
            личности.
          </p>
        </div>

        <form
          onSubmit={handleSubmitNewEmail}
          className="mt-7 space-y-5"
        >
          <Field
            id="newEmail"
            name="newEmail"
            type="email"
            label="Новый email"
            icon={<FiMail className="h-4 w-4" />}
            placeholder="you@example.com"
            value={form.newEmail}
            onChange={handleChange}
            error={errors.newEmail}
            autoComplete="email"
          />

          <Field
            id="password"
            name="password"
            type="password"
            label="Текущий пароль"
            icon={<FiLock className="h-4 w-4" />}
            placeholder="••••••••"
            value={form.password}
            onChange={handleChange}
            error={errors.password}
            autoComplete="current-password"
          />

          {errors.submit && (
            <InlineError message={errors.submit} />
          )}

          <div className="rounded-xl border border-border bg-background/50 p-3.5">
            <div className="flex items-start gap-3">
              <FiShield className="mt-0.5 h-4 w-4 shrink-0 text-accent-blue" />

              <p className="text-xs leading-5 text-text-muted">
                После отправки запроса на новый адрес придёт письмо
                подтверждения.
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent-blue px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-accent-blue/10 transition-all hover:bg-accent-blue/90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {submitting ? (
              <>
                <FiLoader className="h-4 w-4 animate-spin" />
                Отправляем...
              </>
            ) : (
              <>
                Отправить запрос
                <FiArrowRight className="h-4 w-4" />
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => setStep("confirmIntent")}
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-border bg-background px-4 py-3 text-sm font-medium text-text-secondary transition-colors hover:border-accent-blue/30 hover:bg-card hover:text-text-primary disabled:opacity-50"
          >
            <FiArrowLeft className="h-4 w-4" />
            Назад
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
              <FiMail className="h-4 w-4" />
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

function StepIndicator({ current }) {
  return (
    <div className="flex items-center gap-2">
      {[1, 2].map((step) => {
        const active = step === current;
        const completed = step < current;

        return (
          <React.Fragment key={step}>
            <div
              className={`flex h-7 w-7 items-center justify-center rounded-full border text-[10px] font-semibold ${
                active || completed
                  ? "border-accent-blue/30 bg-accent-blue/10 text-accent-blue"
                  : "border-border bg-background text-text-muted"
              }`}
            >
              {completed ? <FiCheck className="h-3.5 w-3.5" /> : step}
            </div>

            {step < 2 && (
              <div className="h-px flex-1 bg-border" />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

function StatusIcon({ intent = false, success = false }) {
  if (success) {
    return (
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-green/20 bg-accent-green/10 text-accent-green">
        <FiCheckCircle className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-blue/20 bg-accent-blue/10 text-accent-blue">
      {intent ? (
        <FiShield className="h-8 w-8" />
      ) : (
        <FiMail className="h-8 w-8" />
      )}
    </div>
  );
}

function Field({
  id,
  name,
  type,
  label,
  icon,
  placeholder,
  value,
  onChange,
  error,
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
        <div className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted">
          {icon}
        </div>

        <input
          id={id}
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          className={`w-full rounded-xl border bg-background/70 py-3 pl-10 pr-4 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted ${
            error
              ? "border-accent-red/40 focus:border-accent-red/60 focus:ring-2 focus:ring-accent-red/10"
              : "border-border focus:border-accent-blue/50 focus:ring-2 focus:ring-accent-blue/10"
          }`}
        />
      </div>

      {error && (
        <p className="mt-1.5 text-xs text-accent-red">
          {error}
        </p>
      )}
    </div>
  );
}

function InlineError({ message }) {
  return (
    <div className="mt-4 flex items-start gap-3 rounded-xl border border-accent-red/20 bg-accent-red/5 p-3.5">
      <FiAlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-accent-red" />

      <p className="text-xs leading-5 text-accent-red">
        {message}
      </p>
    </div>
  );
}

export default EmailChangePage;