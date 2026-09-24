import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiAlertCircle,
  FiArrowRight,
  FiCheckCircle,
  FiLoader,
  FiMail,
} from "react-icons/fi";
import axios from "axios";

const EmailVerificationPage = () => {
  const navigate = useNavigate();

  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const verifyEmail = async () => {
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");

      if (!token) {
        setStatus("error");
        setMessage("Ссылка подтверждения не содержит токена.");
        return;
      }

      try {
        await axios.get("/api/auth/verify-email", {
          params: { token },
          withCredentials: true,
        });

        setStatus("success");
        setMessage("Ваш email успешно подтверждён.");
      } catch (error) {
        console.error("Email verification failed:", error);

        const serverMessage =
          error.response?.data?.message ||
          error.response?.data?.detail;

        setStatus("error");
        setMessage(
          serverMessage ||
            "Не удалось подтвердить email. Ссылка могла устареть или быть недействительной."
        );
      }
    };

    verifyEmail();
  }, []);

  const isSuccess = status === "success";

  if (status === "loading") {
    return (
      <AuthShell>
        <div className="text-center">
          <StatusIcon loading />

          <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-blue">
            XO_OS / ACCOUNT
          </p>

          <h1 className="mt-3 text-2xl font-bold text-text-primary">
            Подтверждение почты
          </h1>

          <p className="mt-3 text-sm leading-6 text-text-secondary">
            Проверяем ссылку подтверждения. Это займёт несколько секунд.
          </p>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell>
      <div className="text-center">
        <StatusIcon success={isSuccess} />

        <p
          className={`mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] ${
            isSuccess ? "text-accent-green" : "text-accent-red"
          }`}
        >
          XO_OS / EMAIL
        </p>

        <h1 className="mt-3 text-2xl font-bold text-text-primary">
          {isSuccess ? "Почта подтверждена" : "Не удалось подтвердить"}
        </h1>

        <p className="mt-3 text-sm leading-6 text-text-secondary">
          {message}
        </p>

        <div className="mt-7">
          <button
            type="button"
            onClick={() =>
              navigate(isSuccess ? "/login" : "/")
            }
            className={`inline-flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition-all ${
              isSuccess
                ? "bg-accent-blue text-white shadow-lg shadow-accent-blue/10 hover:bg-accent-blue/90"
                : "border border-border bg-background text-text-primary hover:border-accent-blue/30 hover:bg-card"
            }`}
          >
            {isSuccess ? (
              <>
                Перейти ко входу
                <FiArrowRight className="h-4 w-4" />
              </>
            ) : (
              "Вернуться на главную"
            )}
          </button>
        </div>

        {isSuccess && (
          <div className="mt-5 flex items-center justify-center gap-2 text-xs text-text-muted">
            <FiMail className="h-3.5 w-3.5" />
            Email привязан к вашему аккаунту
          </div>
        )}
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

function StatusIcon({ success = false, loading = false }) {
  if (loading) {
    return (
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-blue/20 bg-accent-blue/10 text-accent-blue">
        <FiLoader className="h-7 w-7 animate-spin" />
      </div>
    );
  }

  if (success) {
    return (
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-green/20 bg-accent-green/10 text-accent-green">
        <FiCheckCircle className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-red/20 bg-accent-red/10 text-accent-red">
      <FiAlertCircle className="h-8 w-8" />
    </div>
  );
}

export default EmailVerificationPage;