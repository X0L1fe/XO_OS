import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  FiBookOpen,
  FiClock,
  FiFlag,
  FiPlay,
  FiPause,
  FiRefreshCw,
  FiZap,
  FiX,
  FiCheckCircle,
  FiPlus,
  FiFileText,
  FiLink,
  FiImage,
} from "react-icons/fi";

const FILTER_EVENT_NAME = "xo-os:schedule-filters-changed";
const GAMIFICATION_UPDATE_EVENT_NAME = "xo-os:gamification-updated";

const EMPTY_NOW = {
  taskTitle: "",
  taskDesc: "",
  timeEstimate: "",
  priority: "",
  xpReward: 0,
  time: "--:--",
  category: "",
  type: "idle",

  session_id: null,
  status: null,
  elapsed_seconds: 0,
  lesson_id: null,
  lesson_subject: "",
  lesson_description: "",
  goal_text: "",
  verification_status: null,
  completion_mode: null,
  xp_awarded: 0,
  ended_at: null,
  duration_seconds: null,
  evidence_provided: false,
  can_start_new_session: true,
};

export default function NowBlock() {
  const [now, setNow] = useState(EMPTY_NOW);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [currentTime, setCurrentTime] = useState(formatCurrentTime());

  const [completionMessage, setCompletionMessage] = useState(null);
  const [completionMessageType, setCompletionMessageType] = useState("");

  const [showCompleteModal, setShowCompleteModal] = useState(false);

  /*
   * completionMode intentionally lives separately from the request.
   * We pass the selected mode directly to submitCompletion()
   * instead of relying on an asynchronous setState().
   */
  const [completionMode, setCompletionMode] = useState(null);

  const [evidence, setEvidence] = useState([]);

  /*
   * Local timer state.
   *
   * elapsedSeconds is what the user sees.
   * timerStartedAtRef is used only while the session is running.
   * timerBaseSecondsRef stores the last backend-confirmed elapsed time.
   */
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const timerStartedAtRef = useRef(null);
  const timerBaseSecondsRef = useRef(0);

  /*
   * Prevents polling from visually jumping the timer backwards
   * while a local session transition is still being processed.
   */
  const transitionRef = useRef(false);

  /*
   * Prevent double-clicks on controls.
   */
  const actionInProgressRef = useRef(false);

  const hasTask = Boolean(now.taskTitle) || now.type === "focus";

  const isFocusActive =
    now.type === "focus" && now.status === "active";

  const isFocusPaused =
    now.type === "focus" && now.status === "paused";

  const isFocusCompleted =
    now.type === "focus" && now.status === "completed";

  /*
   * ------------------------------------------------------------------
   * NOW API
   * ------------------------------------------------------------------
   */

  const loadNow = useCallback(
    async (showRefreshing = false) => {
      if (showRefreshing) {
        setRefreshing(true);
      }

      try {
        const response = await fetch("/api/now", {
          credentials: "include",
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        const nextNow = {
          ...EMPTY_NOW,
          ...data,
        };

        setNow(nextNow);

        /*
         * Do not let a polling response overwrite the timer while
         * a pause/resume/complete request is being processed.
         */
        if (!transitionRef.current) {
          const backendElapsed = Number(
            nextNow.elapsed_seconds || 0
          );

          /*
           * Backend может быть немного позади локального отображения,
           * поэтому не сбрасываем работающий timer назад.
           */
          if (
            nextNow.type === "focus" &&
            nextNow.status === "active"
          ) {
            const localElapsed = elapsedSeconds;

            if (backendElapsed >= localElapsed) {
              timerBaseSecondsRef.current = backendElapsed;
              setElapsedSeconds(backendElapsed);
              timerStartedAtRef.current = Date.now();
            }
          } else if (
            nextNow.type === "focus" &&
            (
              nextNow.status === "paused" ||
              nextNow.status === "completed"
            )
          ) {
            timerBaseSecondsRef.current = backendElapsed;
            timerStartedAtRef.current = null;
            setElapsedSeconds(backendElapsed);
          } else {
            timerBaseSecondsRef.current = 0;
            timerStartedAtRef.current = null;
            setElapsedSeconds(0);
          }
        }
      } catch (error) {
        console.error("Failed to fetch current lesson:", error);

        /*
         * Don't destroy an active local session just because one
         * polling request failed.
         */
        if (!now.session_id) {
          setNow(EMPTY_NOW);
          setElapsedSeconds(0);
          timerStartedAtRef.current = null;
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [now.session_id]
  );

  /*
   * Initial load.
   */
  useEffect(() => {
    loadNow();
  }, [loadNow]);

  /*
   * Normal polling.
   *
   * 5 seconds while a focus session exists,
   * 15 seconds otherwise.
   */
  useEffect(() => {
    const intervalMs = now.type === "focus" ? 5000 : 15000;

    const interval = window.setInterval(() => {
      loadNow(true);
    }, intervalMs);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadNow, now.type]);

  /*
   * ------------------------------------------------------------------
   * LIVE CLOCK
   * ------------------------------------------------------------------
   */

  useEffect(() => {
    const updateClock = () => {
      setCurrentTime(formatCurrentTime());
    };

    updateClock();

    const interval = window.setInterval(updateClock, 1000);

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  /*
   * ------------------------------------------------------------------
   * TIMER
   * ------------------------------------------------------------------
   *
   * There is exactly ONE timer interval.
   *
   * Active:
   *   displayed = backend base + seconds since local start
   *
   * Paused/completed:
   *   displayed = frozen backend value
   */

  useEffect(() => {
    if (!isFocusActive) {
      timerStartedAtRef.current = null;
      return;
    }

    /*
     * Start/restart local timer from the current displayed value.
     */
    if (!timerStartedAtRef.current) {
      timerStartedAtRef.current = Date.now();
    }

    const interval = window.setInterval(() => {
      if (!timerStartedAtRef.current) {
        return;
      }

      const secondsSinceStart = Math.floor(
        (Date.now() - timerStartedAtRef.current) / 1000
      );

      setElapsedSeconds(
        timerBaseSecondsRef.current + secondsSinceStart
      );
    }, 250);

    return () => {
      window.clearInterval(interval);
    };
  }, [isFocusActive]);

  /*
   * Whenever backend sends a new focus state, synchronize the
   * local timer — unless we're in the middle of a button action.
   */
  useEffect(() => {
    if (transitionRef.current) {
      return;
    }

    if (now.type !== "focus") {
      timerBaseSecondsRef.current = 0;
      timerStartedAtRef.current = null;
      setElapsedSeconds(0);
      return;
    }

    const backendElapsed = Number(now.elapsed_seconds || 0);

    timerBaseSecondsRef.current = backendElapsed;

    if (now.status === "active") {
      /*
       * Only initialize the local clock if it isn't already running.
       * This prevents the 5-second polling from constantly resetting
       * the timer.
       */
      if (!timerStartedAtRef.current) {
        timerStartedAtRef.current = Date.now();
      }
    } else {
      timerStartedAtRef.current = null;
      setElapsedSeconds(backendElapsed);
    }
  }, [
    now.type,
    now.status,
    now.elapsed_seconds,
  ]);

  /*
   * ------------------------------------------------------------------
   * SSE
   * ------------------------------------------------------------------
   */

  useEffect(() => {
    const eventSource = new EventSource("/api/events");

    eventSource.onmessage = (event) => {
      let payload;
      try {
        payload = JSON.parse(event.data);
      } catch {
        return; // heartbeat / connected могут быть не JSON или в другом формате
      }

      if (!payload || typeof payload !== "object") {
        return;
      }

      if (payload.type === "xo-os:focus-updated") {
        window.dispatchEvent(new CustomEvent("xo-os:focus-updated"));
        loadNow(true);
      } else if (payload.type === "xo-os:gamification-updated") {
        window.dispatchEvent(
          new CustomEvent(GAMIFICATION_UPDATE_EVENT_NAME)
        );
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [loadNow]);

  /*
   * ------------------------------------------------------------------
   * COMPLETION MESSAGE
   * ------------------------------------------------------------------
   */

  useEffect(() => {
    if (!completionMessage) {
      return;
    }

    const timeout = window.setTimeout(() => {
      setCompletionMessage(null);
      setCompletionMessageType("");
    }, 4000);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [completionMessage]);

  /*
   * ------------------------------------------------------------------
   * ACTION HELPERS
   * ------------------------------------------------------------------
   */

  const beginAction = () => {
    if (actionInProgressRef.current) {
      return false;
    }

    actionInProgressRef.current = true;
    return true;
  };

  const endAction = () => {
    actionInProgressRef.current = false;
  };

  const showError = (message) => {
    setCompletionMessage(message);
    setCompletionMessageType("error");
  };

  /*
   * ------------------------------------------------------------------
   * START
   * ------------------------------------------------------------------
   */

  const handleStartFocus = async () => {
    if (!beginAction()) return;

    /*
     * Быстрая отсечка: если XP за это занятие уже начислен — не
     * ходим на бэк, сразу показываем сообщение.
     */
    if (
      now.type === "focus" &&
      now.status === "completed" &&
      Number(now.xp_awarded) > 0
    ) {
      showError("За это занятие XP уже получен — новая сессия недоступна.");
      endAction();
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("/api/focus/start", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        /*
         * Пытаемся вытащить осмысленное сообщение с бэка.
         */
        let detail = "";
        try {
          const errData = await response.json();
          detail =
            errData?.detail ||
            errData?.message ||
            "";
        } catch {
          /* ignore */
        }

        /*
         * Отдельно обрабатываем случай, когда бэк говорит,
         * что XP за это занятие уже начислен.
         * FastAPI-стиль: 400 или 409.
         */
        const alreadyAwarded =
          response.status === 409 ||
          /already been awarded/i.test(detail);

        if (alreadyAwarded) {
          showError(
            detail || "XP за это занятие уже начислен"
          );

          /*
           * Синхронизируем состояние с бэком, чтобы UI
           * показал completed + xp_awarded + verification_status.
           */
          await loadNow();
          return;
        }

        throw new Error(detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data && typeof data === "object") {
        const nextNow = {
          ...EMPTY_NOW,
          ...data,
        };

        setNow(nextNow);

        const elapsed = Number(nextNow.elapsed_seconds || 0);

        timerBaseSecondsRef.current = elapsed;
        setElapsedSeconds(elapsed);

        if (
          nextNow.type === "focus" &&
          nextNow.status === "active"
        ) {
          timerStartedAtRef.current = Date.now();
        } else {
          timerStartedAtRef.current = null;
        }
      }

      await loadNow();
    } catch (error) {
      console.error("Failed to start focus session:", error);
      showError(error.message || "Не удалось начать фокус-сессию");
    } finally {
      setLoading(false);
      endAction();
    }
  };

  /*
   * ------------------------------------------------------------------
   * PAUSE
   * ------------------------------------------------------------------
   */

  const handlePauseFocus = async () => {
    if (!now.session_id || !isFocusActive) {
      return;
    }

    if (!beginAction()) {
      return;
    }

    const sessionId = now.session_id;
    const frozenElapsed = elapsedSeconds;

    /*
     * Сначала останавливаем локальный timer.
     */
    transitionRef.current = true;

    timerBaseSecondsRef.current = frozenElapsed;
    timerStartedAtRef.current = null;
    setElapsedSeconds(frozenElapsed);

    /*
     * И сразу показываем PAUSED локально.
     * Не ждём polling.
     */
    setNow((previous) => ({
      ...previous,
      status: "paused",
      elapsed_seconds: frozenElapsed,
    }));

    try {
      setLoading(true);

      const response = await fetch(
        `/api/focus/${sessionId}/pause`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      /*
       * ВАЖНО:
       * после pause не вызываем loadNow() здесь.
       *
       * Backend уже получил pause.
       * Следующий обычный polling сам синхронизирует состояние.
       */
    } catch (error) {
      console.error(
        "Failed to pause focus session:",
        error
      );

      /*
       * Если API отклонил pause — возвращаем ACTIVE.
       */
      setNow((previous) => ({
        ...previous,
        status: "active",
        elapsed_seconds: frozenElapsed,
      }));

      timerBaseSecondsRef.current = frozenElapsed;
      timerStartedAtRef.current = Date.now();

      showError("Не удалось поставить на паузу");
    } finally {
      transitionRef.current = false;
      setLoading(false);
      endAction();
    }
  };

  /*
   * ------------------------------------------------------------------
   * RESUME
   * ------------------------------------------------------------------
   */

  const handleResumeFocus = async () => {
    if (!now.session_id || !isFocusPaused) {
      return;
    }

    if (!beginAction()) {
      return;
    }

    const sessionId = now.session_id;
    const frozenElapsed = elapsedSeconds;

    transitionRef.current = true;

    try {
      setLoading(true);

      const response = await fetch(
        `/api/focus/${sessionId}/resume`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      /*
       * Сразу переводим существующую сессию в ACTIVE.
       * session_id остаётся тем же.
       */
      setNow((previous) => ({
        ...previous,
        status: "active",
        elapsed_seconds: frozenElapsed,
      }));

      timerBaseSecondsRef.current = frozenElapsed;
      setElapsedSeconds(frozenElapsed);

      /*
       * Таймер начинает продолжать именно с frozenElapsed,
       * а не с нуля.
       */
      timerStartedAtRef.current = Date.now();
    } catch (error) {
      console.error(
        "Failed to resume focus session:",
        error
      );

      /*
       * Остаёмся на паузе.
       */
      timerStartedAtRef.current = null;
      timerBaseSecondsRef.current = frozenElapsed;
      setElapsedSeconds(frozenElapsed);

      setNow((previous) => ({
        ...previous,
        status: "paused",
        elapsed_seconds: frozenElapsed,
      }));

      showError("Не удалось продолжить");
    } finally {
      transitionRef.current = false;
      setLoading(false);
      endAction();
    }
  };

  /*
   * ------------------------------------------------------------------
   * COMPLETE
   * ------------------------------------------------------------------
   */

  const handleCompleteFocus = () => {
    if (!now.session_id || isFocusCompleted) {
      return;
    }

    setCompletionMode(null);
    setEvidence([]);
    setShowCompleteModal(true);
  };

  const handleCompleteModalClose = () => {
    if (actionInProgressRef.current) {
      return;
    }

    setShowCompleteModal(false);
    setCompletionMode(null);
    setEvidence([]);
  };

  /*
   * IMPORTANT:
   * mode is passed directly to this function.
   * We don't do:
   *
   * setCompletionMode("manual");
   * handleCompleteModalSubmit();
   *
   * because React state updates are asynchronous.
   */
  const handleCompleteModalSubmit = async (mode) => {
    if (!now.session_id || !mode) {
      return;
    }

    if (!beginAction()) {
      return;
    }

    /*
     * Stop the timer BEFORE talking to the backend.
     */
    transitionRef.current = true;

    const frozenElapsed = elapsedSeconds;

    timerBaseSecondsRef.current = frozenElapsed;
    timerStartedAtRef.current = null;
    setElapsedSeconds(frozenElapsed);

    try {
      setLoading(true);

      const response = await fetch(
        `/api/focus/${now.session_id}/complete`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            completion_mode: mode,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      /*
       * Immediately mark the local session as completed.
       * This prevents the timer from restarting while waiting
       * for polling/SSE.
       */
      setNow((previous) => ({
        ...previous,
        status: "completed",
        verification_status:
          data.verification_status ??
          previous.verification_status,
        elapsed_seconds:
          data.elapsed_seconds ??
          frozenElapsed,
      }));

      const finalElapsed = Number(
        data.elapsed_seconds ?? frozenElapsed
      );

      timerBaseSecondsRef.current = finalElapsed;
      timerStartedAtRef.current = null;
      setElapsedSeconds(finalElapsed);

      const isPending =
        data.completion_mode === "ai_verified" ||
        data.verification_status === "pending";

      if (isPending) {
        setCompletionMessage(
          "Отправлено на проверку AI. XP начислится после проверки."
        );
        setCompletionMessageType("pending");
      } else {
        setCompletionMessage(
          `Сессия завершена! +${data.xp_awarded || 0} XP`
        );
        setCompletionMessageType(
          data.verification_status === "approved" ? "success" : "error"
        );
      }

      setShowCompleteModal(false);
      setCompletionMode(null);
      setEvidence([]);

      /*
       * Refresh after local state has already been frozen.
       */
      await loadNow();
    } catch (error) {
      console.error(
        "Failed to complete focus session:",
        error
      );

      /*
       * If completion failed, restore the appropriate local state.
       *
       * If it was active, restart the timer.
       * If it was paused, keep it frozen.
       */
      if (isFocusActive) {
        timerBaseSecondsRef.current = frozenElapsed;
        timerStartedAtRef.current = Date.now();
      } else {
        timerBaseSecondsRef.current = frozenElapsed;
        timerStartedAtRef.current = null;
      }

      setElapsedSeconds(frozenElapsed);

      showError("Не удалось завершить сессию");
    } finally {
      transitionRef.current = false;
      setLoading(false);
      endAction();

      loadNow();
    }
  };
  /*
   * ------------------------------------------------------------------
   * ADD EVIDENC
   * ------------------------------------------------------------------
   */

  const handleAddEvidence = async (payload) => {
    if (!now.session_id) {
      throw new Error("Нет активной сессии");
    }

    const formData = new FormData();
    formData.append("type", payload.type);

    if (payload.type === "image") {
      if (!(payload.file instanceof File)) {
        throw new Error("Файл изображения не выбран");
      }
      formData.append("file", payload.file);
      if (payload.content) {
        formData.append("content", payload.content);
      }
    } else {
      formData.append("content", payload.content || "");
    }

    const response = await fetch(
      `/api/focus/${now.session_id}/evidence`,
      {
        method: "POST",
        credentials: "include",
        body: formData,
        // Content-Type намеренно не выставляем — браузер сам подставит
        // multipart/form-data с корректным boundary.
      }
    );

    if (!response.ok) {
      let detail = "";
      try {
        const err = await response.json();
        if (err && err.detail) {
          detail = `: ${err.detail}`;
        }
      } catch {
        // ignore
      }
      throw new Error(`Не удалось добавить (${response.status})${detail}`);
    }

    const created = await response.json();
    setEvidence((previous) => [...previous, created]);
    return created;
  };
  /*
   * ------------------------------------------------------------------
   * DISPLAY HELPERS
   * ------------------------------------------------------------------
   */

  const formattedElapsed = formatElapsedTime(
    elapsedSeconds
  );

  const statusLabel = isFocusActive
    ? "В ФОКУСЕ"
    : isFocusPaused
      ? "ПАУЗА"
      : isFocusCompleted
        ? "ЗАВЕРШЕНО"
        : "";

  const statusClass = isFocusActive
    ? "border-accentGreen/20 bg-accentGreen/10 text-accentGreen"
    : isFocusPaused
      ? "border-accentYellow/20 bg-accentYellow/10 text-accentYellow"
      : "border-border bg-background/60 text-secondary";

  const isActionDisabled =
    loading || actionInProgressRef.current;

  /*
   * ------------------------------------------------------------------
   * RENDER
   * ------------------------------------------------------------------
   */

  return (
    <section
      className="
        relative
        overflow-hidden
        rounded-2xl
        border
        border-border
        bg-panel
        transition-colors
        duration-200
        hover:border-accentBlue/20
      "
    >
      {/* Subtle accent — intentionally much quieter than the previous glow */}
      <div
        className="
          pointer-events-none
          absolute
          right-0
          top-0
          h-40
          w-40
          rounded-full
          bg-accentBlue/5
          blur-3xl
        "
      />

      {/* ------------------------------------------------------------ */}
      {/* HEADER */}
      {/* ------------------------------------------------------------ */}

      <div
        className="
          relative
          flex
          items-center
          justify-between
          border-b
          border-border
          px-6
          py-4
        "
      >
        <div className="flex items-center gap-3">
          <div
            className="
              flex
              h-9
              w-9
              items-center
              justify-center
              rounded-lg
              border
              border-accentBlue/20
              bg-accentBlue/10
              text-accentBlue
            "
          >
            {now.type === "focus" ? (
              <FiClock size={16} />
            ) : (
              <FiBookOpen size={16} />
            )}
          </div>

          <div>
            <p
              className="
                text-[10px]
                font-medium
                uppercase
                tracking-[0.18em]
                text-secondary
              "
            >
              {now.type === "focus"
                ? "Текущий фокус"
                : "Текущее состояние"}
            </p>

            <h2
              className="
                mt-0.5
                text-lg
                font-semibold
                tracking-tight
                text-primary
              "
            >
              СЕЙЧАС
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {refreshing && (
            <FiRefreshCw
              size={13}
              className="animate-spin text-secondary"
            />
          )}

          <span
            className="
              rounded-lg
              border
              border-border
              bg-background/50
              px-3
              py-1.5
              font-mono
              text-xs
              text-secondary
            "
          >
            {currentTime}
          </span>
        </div>
      </div>

      {/* ------------------------------------------------------------ */}
      {/* MESSAGE */}
      {/* ------------------------------------------------------------ */}

      {completionMessage && (
        <div
          className={`
            mx-6
            mt-4
            flex
            items-center
            justify-between
            gap-3
            rounded-lg
            border
            px-4
            py-3
            text-sm
            font-medium
            ${completionMessageType === "success"
              ? "border-accentGreen/20 bg-accentGreen/10 text-accentGreen"
              : completionMessageType === "error"
                ? "border-accentRed/20 bg-accentRed/10 text-accentRed"
                : "border-accentYellow/20 bg-accentYellow/10 text-accentYellow"
            }
          `}
        >
          <div>{completionMessage}</div>

          {completionMessageType !== "pending" && (
            <button
              type="button"
              className="
                rounded-md
                p-1
                transition-colors
                hover:bg-white/5
              "
              onClick={() => {
                setCompletionMessage(null);
                setCompletionMessageType("");
              }}
              aria-label="Закрыть сообщение"
            >
              <FiX size={14} />
            </button>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------ */}
      {/* CONTENT */}
      {/* ------------------------------------------------------------ */}

      <div className="relative p-6">
        {loading && !hasTask ? (
          <LoadingSkeleton />
        ) : now.type === "idle" ? (
          <IdleState
            onStart={handleStartFocus}
            disabled={loading}
          />
        ) : now.type === "lesson" ? (
          <LessonState
            now={now}
            onStart={handleStartFocus}
            disabled={loading}
          />
        ) : now.type === "focus" ? (
          <FocusState
            now={now}
            formattedElapsed={formattedElapsed}
            statusLabel={statusLabel}
            statusClass={statusClass}
            isFocusActive={isFocusActive}
            isFocusPaused={isFocusPaused}
            isFocusCompleted={isFocusCompleted}
            loading={loading}
            onPause={handlePauseFocus}
            onResume={handleResumeFocus}
            onComplete={handleCompleteFocus}
            onStart={handleStartFocus}
          />
        ) : (
          <div className="py-10 text-center text-sm text-secondary">
            Неизвестное состояние
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------ */}
      {/* COMPLETION MODAL */}
      {/* ------------------------------------------------------------ */}

      {showCompleteModal && (
        <CompletionModal
          completionMode={completionMode}
          loading={loading}
          evidence={evidence}
          onClose={handleCompleteModalClose}
          onSelect={(mode) => {
            setCompletionMode(mode);
          }}
          onSubmit={handleCompleteModalSubmit}
          onAddEvidence={handleAddEvidence}
        />
      )}
    </section>
  );
}

/* ================================================================== */
/* LOADING */
/* ================================================================== */

function LoadingSkeleton() {
  return (
    <div className="space-y-5 animate-pulse">
      <div className="h-7 w-2/3 rounded-lg bg-background" />
      <div className="h-4 w-1/3 rounded bg-background" />
      <div className="h-4 w-4/5 rounded bg-background" />

      <div className="grid grid-cols-2 gap-3">
        <div className="h-16 rounded-xl bg-background" />
        <div className="h-16 rounded-xl bg-background" />
      </div>

      <div className="h-11 rounded-xl bg-background" />
    </div>
  );
}

/* ================================================================== */
/* IDLE */
/* ================================================================== */

function IdleState({ onStart, disabled }) {
  return (
    <div
      className="
        flex
        min-h-[190px]
        flex-col
        items-center
        justify-center
        rounded-xl
        border
        border-dashed
        border-border
        bg-background/30
        px-6
        text-center
      "
    >
      <div
        className="
          mb-3
          flex
          h-11
          w-11
          items-center
          justify-center
          rounded-xl
          border
          border-border
          bg-background
          text-secondary
        "
      >
        <FiBookOpen size={18} />
      </div>

      <p className="text-sm font-medium text-primary">
        Сейчас нет активного занятия
      </p>

      <p className="mt-1 text-xs leading-5 text-secondary">
        Здесь появится текущее событие расписания.
      </p>

      <button
        type="button"
        disabled={disabled}
        onClick={onStart}
        className="
          mt-5
          flex
          w-full
          items-center
          justify-center
          gap-2
          rounded-xl
          bg-accentBlue
          px-4
          py-3
          text-sm
          font-semibold
          text-white
          transition-all
          duration-200
          hover:bg-accentBlue/90
          active:scale-[0.99]
          disabled:cursor-not-allowed
          disabled:opacity-50
        "
      >
        <FiPlay size={15} />
        НАЧАТЬ
      </button>
    </div>
  );
}

/* ================================================================== */
/* LESSON */
/* ================================================================== */

function LessonState({ now, onStart, disabled }) {
  return (
    <>
      <div>
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p
              className="
                text-2xl
                font-semibold
                leading-tight
                tracking-tight
                text-primary
              "
            >
              {now.lesson_subject || "Без названия"}
            </p>

            {now.category && (
              <CategoryBadge category={now.category} />
            )}
          </div>
        </div>

        {now.lesson_description && (
          <p
            className="
              mt-4
              max-w-3xl
              text-sm
              leading-6
              text-secondary
            "
          >
            {now.lesson_description}
          </p>
        )}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <MetaCard
          icon={<FiClock size={14} />}
          label="Время занятия"
          value={now.time_estimate || "Не указано"}
        />

        <MetaCard
          icon={<FiFlag size={14} />}
          label="Тип"
          value={formatLessonType(now.priority)}
        />
      </div>

      <div
        className="
          mt-4
          flex
          items-center
          justify-between
          rounded-xl
          border
          border-accentYellow/15
          bg-accentYellow/5
          px-4
          py-3
        "
      >
        <div className="flex items-center gap-2.5">
          <div
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              bg-accentYellow/10
              text-accentYellow
            "
          >
            <FiZap size={15} />
          </div>

          <span
            className="
              text-xs
              font-medium
              uppercase
              tracking-[0.14em]
              text-secondary
            "
          >
            Награда за фокус
          </span>
        </div>

        <span
          className="
            font-mono
            text-sm
            font-semibold
            text-accentYellow
          "
        >
          +{now.completion_mode === "manual" ? 3 : 10} XP
        </span>
      </div>

      {now.can_start_new_session !== false ? (
        <button
          type="button"
          disabled={disabled}
          onClick={onStart}
          className="
            mt-5
            flex
            w-full
            items-center
            justify-center
            gap-2.5
            rounded-xl
            bg-accentBlue
            px-4
            py-3
            text-sm
            font-semibold
            text-white
            transition-all
            duration-200
            hover:bg-accentBlue/90
            active:scale-[0.99]
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          <FiPlay size={15} />
          НАЧАТЬ ФОКУС
        </button>
      ) : (
        <div
          className="
            mt-5
            rounded-xl
            border
            border-border
            bg-background/30
            px-4
            py-3
            text-center
            text-xs
            text-secondary
          "
        >
          За это занятие XP уже получен. Следующее занятие появится
          автоматически.
        </div>
      )}
    </>
  );
}

/* ================================================================== */
/* FOCUS */
/* ================================================================== */

function FocusState({
  now,
  formattedElapsed,
  statusLabel,
  statusClass,
  isFocusActive,
  isFocusPaused,
  isFocusCompleted,
  loading,
  onPause,
  onResume,
  onComplete,
  onStart,
}) {
  return (
    <>
      {/* Header information */}
      <div>
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p
              className="
                text-2xl
                font-semibold
                leading-tight
                tracking-tight
                text-primary
              "
            >
              {now.lesson_subject || "Без урока"}
            </p>

            {now.category && (
              <CategoryBadge category={now.category} />
            )}
          </div>

          {statusLabel && (
            <span
              className={`
                shrink-0
                rounded-lg
                border
                px-2.5
                py-1.5
                text-[10px]
                font-semibold
                uppercase
                tracking-[0.14em]
                ${statusClass}
              `}
            >
              {statusLabel}
            </span>
          )}
        </div>

        {now.lesson_description && (
          <p
            className="
              mt-4
              max-w-3xl
              text-sm
              leading-6
              text-secondary
            "
          >
            {now.lesson_description}
          </p>
        )}

        {now.goal_text && (
          <div
            className="
              mt-3
              rounded-lg
              border
              border-border
              bg-background/30
              px-3
              py-2.5
            "
          >
            <span
              className="
                text-[10px]
                font-medium
                uppercase
                tracking-[0.14em]
                text-secondary
              "
            >
              Цель
            </span>

            <p className="mt-1 text-sm text-primary">
              {now.goal_text}
            </p>
          </div>
        )}
      </div>

      {/* Timer */}
      <div
        className="
          mt-6
          rounded-xl
          border
          border-border
          bg-background/40
          px-5
          py-5
        "
      >
        <div className="flex items-center justify-between">
          <div>
            <p
              className="
                text-[10px]
                font-medium
                uppercase
                tracking-[0.16em]
                text-secondary
              "
            >
              Затраченное время
            </p>

            <p
              className="
                mt-1
                font-mono
                text-4xl
                font-semibold
                tracking-tight
                text-primary
                tabular-nums
              "
            >
              {formattedElapsed}
            </p>
          </div>

          <div
            className={`
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-xl
              border
              ${statusClass}
            `}
          >
            {isFocusActive ? (
              <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-accentGreen" />
            ) : isFocusPaused ? (
              <FiPause size={17} />
            ) : (
              <FiCheckCircle size={17} />
            )}
          </div>
        </div>

        {/* Controls */}
        {!isFocusCompleted && (
          <div className="mt-5 grid grid-cols-2 gap-3">
            {isFocusActive ? (
              <button
                type="button"
                disabled={loading}
                onClick={onPause}
                className="
                  flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  border
                  border-accentYellow/20
                  bg-accentYellow/5
                  px-4
                  py-3
                  text-sm
                  font-medium
                  text-accentYellow
                  transition-colors
                  hover:bg-accentYellow/10
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                <FiPause size={16} />
                ПАУЗА
              </button>
            ) : (
              <button
                type="button"
                disabled={loading}
                onClick={onResume}
                className="
                  flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  border
                  border-accentGreen/20
                  bg-accentGreen/5
                  px-4
                  py-3
                  text-sm
                  font-medium
                  text-accentGreen
                  transition-colors
                  hover:bg-accentGreen/10
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                <FiPlay size={16} />
                ПРОДОЛЖИТЬ
              </button>
            )}

            <button
              type="button"
              disabled={loading}
              onClick={onComplete}
              className="
                flex
                items-center
                justify-center
                gap-2
                rounded-xl
                bg-accentBlue
                px-4
                py-3
                text-sm
                font-semibold
                text-white
                transition-colors
                hover:bg-accentBlue/90
                active:scale-[0.99]
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              <FiCheckCircle size={16} />
              ЗАВЕРШИТЬ
            </button>
          </div>
        )}

        {/* Completed */}
        {isFocusCompleted && (
          <div className="mt-5 space-y-3">
            <div
              className="
                flex
                items-center
                justify-between
                rounded-lg
                border
                border-accentGreen/20
                bg-accentGreen/5
                px-4
                py-3
              "
            >
              <div className="flex items-center gap-2">
                <FiCheckCircle size={15} className="text-accentGreen" />
                <span className="text-sm font-medium text-primary">
                  Фокус-сессия завершена
                </span>
              </div>

              <div className="flex items-center gap-3">
                {now.xp_awarded > 0 && (
                  <span className="font-mono text-sm font-semibold text-accentYellow">
                    +{now.xp_awarded} XP
                  </span>
                )}
                <span className="text-xs text-secondary">
                  {formatVerificationStatus(now.verification_status)}
                </span>
              </div>
            </div>

            {/*
             * Кнопка «начать новую сессию» доступна только
             * если бэк ещё не начислил XP за это занятие.
             * После начисления новую сессию на то же занятие
             * бэк отклоняет.
             */}
            {now.can_start_new_session !== false && (
              <button
                type="button"
                disabled={loading}
                onClick={onStart}
                className="
                  flex
                  w-full
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-accentBlue
                  px-4
                  py-3
                  text-sm
                  font-semibold
                  text-white
                  transition-colors
                  hover:bg-accentBlue/90
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                <FiPlay size={15} />
                НАЧАТЬ НОВУЮ СЕССИЮ
              </button>
            )}

            {now.can_start_new_session === false && (
              <p className="text-xs text-secondary">
                За это занятие XP уже получен. Следующее занятие
                появится автоматически после начала пары.
              </p>
            )}
          </div>
        )}
      </div>
    </>
  );
}

/* ================================================================== */
/* COMPLETION MODAL */
/* ================================================================== */

function CompletionModal({
  completionMode,
  loading,
  evidence,
  onClose,
  onSelect,
  onSubmit,
  onAddEvidence,
}) {
  const [addingType, setAddingType] = useState(null); // null | 'text' | 'url' | 'image'
  const [textValue, setTextValue] = useState("");
  const [urlValue, setUrlValue] = useState("");
  const [fileValue, setFileValue] = useState(null);
  const [addingError, setAddingError] = useState(null);
  const [addingInProgress, setAddingInProgress] = useState(false);

  const isAiMode = completionMode === "ai_verified";
  const isBusy = loading || addingInProgress;

  const canSubmit =
    !isBusy &&
    Boolean(completionMode) &&
    (!isAiMode || evidence.length > 0);

  const resetAdding = () => {
    setAddingType(null);
    setTextValue("");
    setUrlValue("");
    setFileValue(null);
    setAddingError(null);
  };

  const handleSelectMode = (mode) => {
    onSelect(mode);
    if (mode !== "ai_verified") {
      resetAdding();
    }
  };

  const handleAddClick = (type) => {
    if (addingType === type) {
      resetAdding();
      return;
    }
    setAddingType(type);
    setTextValue("");
    setUrlValue("");
    setFileValue(null);
    setAddingError(null);
  };

  const handleAddConfirm = async () => {
    if (!addingType) return;

    setAddingError(null);
    setAddingInProgress(true);

    try {
      if (addingType === "text") {
        const trimmed = textValue.trim();
        if (!trimmed) {
          throw new Error("Введите текст доказательства");
        }
        await onAddEvidence({ type: "text", content: trimmed });
      } else if (addingType === "url") {
        const trimmed = urlValue.trim();
        if (!trimmed) {
          throw new Error("Введите URL");
        }
        if (!/^https?:\/\//i.test(trimmed)) {
          throw new Error("URL должен начинаться с http:// или https://");
        }
        await onAddEvidence({ type: "url", content: trimmed });
      } else if (addingType === "image") {
        if (!fileValue) {
          throw new Error("Выберите изображение");
        }
        await onAddEvidence({
          type: "image",
          file: fileValue,
          content: fileValue.name,
        });
      }
      resetAdding();
    } catch (err) {
      setAddingError(err?.message || "Не удалось добавить доказательство");
    } finally {
      setAddingInProgress(false);
    }
  };

  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        items-center
        justify-center
        bg-black/60
        p-4
        backdrop-blur-sm
      "
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isBusy) {
          onClose();
        }
      }}
    >
      <div
        className="
          w-full
          max-w-md
          max-h-[90vh]
          overflow-y-auto
          rounded-2xl
          border
          border-border
          bg-panel
          p-6
          shadow-2xl
        "
        role="dialog"
        aria-modal="true"
        aria-labelledby="completion-title"
      >
        {/* HEADER */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div
              className="
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
              <FiCheckCircle size={18} />
            </div>

            <div>
              <p
                className="
                  text-[10px]
                  font-medium
                  uppercase
                  tracking-[0.18em]
                  text-secondary
                "
              >
                Фокус-сессия
              </p>

              <h2
                id="completion-title"
                className="
                  mt-0.5
                  text-lg
                  font-semibold
                  tracking-tight
                  text-primary
                "
              >
                ЗАВЕРШЕНИЕ
              </h2>
            </div>
          </div>

          <button
            type="button"
            disabled={isBusy}
            onClick={onClose}
            className="
              rounded-lg
              p-2
              text-secondary
              transition-colors
              hover:bg-background
              hover:text-primary
              disabled:opacity-40
            "
            aria-label="Закрыть"
          >
            <FiX size={18} />
          </button>
        </div>

        {/* MODE */}
        <p className="mt-6 text-sm text-secondary">
          Выберите способ завершения фокус-сессии.
        </p>

        <div className="mt-4 space-y-3">
          <CompletionOption
            selected={completionMode === "manual"}
            disabled={isBusy}
            icon={<FiCheckCircle size={16} />}
            title="Завершить вручную"
            description="Базовая награда — 3 XP"
            onClick={() => handleSelectMode("manual")}
          />

          <CompletionOption
            selected={completionMode === "ai_verified"}
            disabled={isBusy}
            icon={<FiZap size={16} />}
            title="Отправить на проверку AI"
            description="Основная награда — 10 XP + бонус за результат"
            onClick={() => handleSelectMode("ai_verified")}
          />
        </div>

        {/* EVIDENCE */}
        {isAiMode && (
          <div className="mt-6">
            <div className="flex items-center justify-between">
              <p
                className="
                  text-[10px]
                  font-medium
                  uppercase
                  tracking-[0.18em]
                  text-secondary
                "
              >
                Доказательства
              </p>

              <span className="text-[10px] font-medium text-secondary">
                {evidence.length} / 5
              </span>
            </div>

            <div className="mt-3 grid grid-cols-3 gap-2">
              <EvidenceAddButton
                icon={<FiFileText size={14} />}
                label="Текст"
                active={addingType === "text"}
                disabled={isBusy || evidence.length >= 5}
                onClick={() => handleAddClick("text")}
              />
              <EvidenceAddButton
                icon={<FiLink size={14} />}
                label="URL"
                active={addingType === "url"}
                disabled={isBusy || evidence.length >= 5}
                onClick={() => handleAddClick("url")}
              />
              <EvidenceAddButton
                icon={<FiImage size={14} />}
                label="Скрин"
                active={addingType === "image"}
                disabled={isBusy || evidence.length >= 5}
                onClick={() => handleAddClick("image")}
              />
            </div>

            {addingType && (
              <div className="mt-3 rounded-xl border border-border bg-background/40 p-3">
                {addingType === "text" && (
                  <textarea
                    value={textValue}
                    onChange={(e) => setTextValue(e.target.value)}
                    disabled={addingInProgress}
                    placeholder="Опишите, что было сделано..."
                    rows={3}
                    className="
                      w-full
                      resize-none
                      rounded-lg
                      border
                      border-border
                      bg-background
                      px-3
                      py-2
                      text-sm
                      text-primary
                      placeholder:text-secondary
                      focus:border-accentBlue/40
                      focus:outline-none
                      disabled:opacity-60
                    "
                  />
                )}

                {addingType === "url" && (
                  <input
                    type="url"
                    value={urlValue}
                    onChange={(e) => setUrlValue(e.target.value)}
                    disabled={addingInProgress}
                    placeholder="https://..."
                    className="
                      w-full
                      rounded-lg
                      border
                      border-border
                      bg-background
                      px-3
                      py-2
                      text-sm
                      text-primary
                      placeholder:text-secondary
                      focus:border-accentBlue/40
                      focus:outline-none
                      disabled:opacity-60
                    "
                  />
                )}

                {addingType === "image" && (
                  <div>
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      disabled={addingInProgress}
                      onChange={(e) =>
                        setFileValue(e.target.files?.[0] || null)
                      }
                      className="
                        block
                        w-full
                        text-xs
                        text-secondary
                        file:mr-3
                        file:rounded-lg
                        file:border-0
                        file:bg-background
                        file:px-3
                        file:py-2
                        file:text-xs
                        file:font-medium
                        file:text-primary
                        hover:file:bg-background/80
                        disabled:opacity-60
                      "
                    />

                    {fileValue && (
                      <p className="mt-2 truncate text-xs text-secondary">
                        {fileValue.name} ·{" "}
                        {(fileValue.size / 1024).toFixed(0)} KB
                      </p>
                    )}
                  </div>
                )}

                {addingError && (
                  <p className="mt-2 text-xs text-accentRed">
                    {addingError}
                  </p>
                )}

                <div className="mt-3 flex justify-end gap-2">
                  <button
                    type="button"
                    disabled={addingInProgress}
                    onClick={resetAdding}
                    className="
                      rounded-lg
                      border
                      border-border
                      bg-background/40
                      px-3
                      py-1.5
                      text-xs
                      font-medium
                      text-secondary
                      transition-colors
                      hover:bg-background
                      disabled:opacity-50
                    "
                  >
                    Отмена
                  </button>

                  <button
                    type="button"
                    disabled={addingInProgress}
                    onClick={handleAddConfirm}
                    className="
                      flex
                      items-center
                      gap-1.5
                      rounded-lg
                      bg-accentBlue
                      px-3
                      py-1.5
                      text-xs
                      font-semibold
                      text-white
                      transition-colors
                      hover:bg-accentBlue/90
                      disabled:opacity-50
                    "
                  >
                    {addingInProgress ? (
                      <>
                        <FiRefreshCw
                          size={12}
                          className="animate-spin"
                        />
                        Отправка
                      </>
                    ) : (
                      "Добавить"
                    )}
                  </button>
                </div>
              </div>
            )}

            {evidence.length > 0 && (
              <div className="mt-3 space-y-2">
                {evidence.map((ev) => (
                  <EvidenceListItem key={ev.id} evidence={ev} />
                ))}
              </div>
            )}

            {evidence.length === 0 && !addingType && (
              <p className="mt-3 text-xs text-secondary">
                Добавьте хотя бы одно доказательство, чтобы отправить на
                проверку AI.
              </p>
            )}
          </div>
        )}

        {/* ACTIONS */}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <button
            type="button"
            disabled={isBusy}
            onClick={onClose}
            className="
              rounded-xl
              border
              border-border
              bg-background/40
              px-4
              py-3
              text-sm
              font-medium
              text-secondary
              transition-colors
              hover:bg-background
              hover:text-primary
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            ОТМЕНА
          </button>

          <button
            type="button"
            disabled={!canSubmit}
            onClick={() => onSubmit(completionMode)}
            className="
              flex
              items-center
              justify-center
              gap-2
              rounded-xl
              bg-accentBlue
              px-4
              py-3
              text-sm
              font-semibold
              text-white
              transition-colors
              hover:bg-accentBlue/90
              disabled:cursor-not-allowed
              disabled:opacity-40
            "
          >
            {loading ? (
              <>
                <FiRefreshCw size={15} className="animate-spin" />
                ОБРАБОТКА
              </>
            ) : (
              <>
                <FiCheckCircle size={15} />
                ЗАВЕРШИТЬ
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

function EvidenceAddButton({ icon, label, active, disabled, onClick }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`
        flex
        items-center
        justify-center
        gap-1.5
        rounded-lg
        border
        px-2
        py-2
        text-xs
        font-medium
        transition-all
        ${active
          ? "border-accentBlue/40 bg-accentBlue/10 text-accentBlue"
          : "border-border bg-background/40 text-secondary hover:border-accentBlue/20 hover:text-primary"
        }
        disabled:cursor-not-allowed
        disabled:opacity-50
      `}
    >
      {icon}
      {label}
    </button>
  );
}

function EvidenceListItem({ evidence }) {
  let icon = <FiFileText size={13} />;
  let preview = evidence.content || "";

  if (evidence.type === "url") {
    icon = <FiLink size={13} />;
  } else if (evidence.type === "image") {
    icon = <FiImage size={13} />;
  }

  return (
    <div
      className="
        flex
        items-center
        gap-2.5
        rounded-lg
        border
        border-border
        bg-background/30
        px-3
        py-2
      "
    >
      <div
        className="
          flex
          h-7
          w-7
          shrink-0
          items-center
          justify-center
          rounded-md
          bg-background
          text-secondary
        "
      >
        {icon}
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate text-xs text-primary">{preview}</p>
        <p
          className="
            text-[10px]
            uppercase
            tracking-wider
            text-secondary
          "
        >
          {evidence.type}
        </p>
      </div>
    </div>
  );
}

/* ================================================================== */
/* COMPLETION OPTION */
/* ================================================================== */

function CompletionOption({
  selected,
  disabled,
  icon,
  title,
  description,
  onClick,
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`
        flex
        w-full
        items-center
        gap-3
        rounded-xl
        border
        px-4
        py-3
        text-left
        transition-all
        duration-150
        ${selected
          ? "border-accentBlue/40 bg-accentBlue/10"
          : "border-border bg-background/30 hover:border-accentBlue/20 hover:bg-background/60"
        }
        disabled:cursor-not-allowed
        disabled:opacity-50
      `}
      aria-pressed={selected}
    >
      <div
        className={`
          flex
          h-9
          w-9
          shrink-0
          items-center
          justify-center
          rounded-lg
          ${selected
            ? "bg-accentBlue/15 text-accentBlue"
            : "bg-background text-secondary"
          }
        `}
      >
        {icon}
      </div>

      <div className="min-w-0">
        <p className="text-sm font-medium text-primary">
          {title}
        </p>

        <p className="mt-0.5 text-xs text-secondary">
          {description}
        </p>
      </div>
    </button>
  );
}

/* ================================================================== */
/* SMALL UI COMPONENTS */
/* ================================================================== */

function CategoryBadge({ category }) {
  return (
    <div
      className="
        mt-3
        inline-flex
        items-center
        gap-2
        rounded-lg
        border
        border-accentBlue/15
        bg-accentBlue/10
        px-2.5
        py-1.5
      "
    >
      <FiBookOpen
        size={12}
        className="text-accentBlue"
      />

      <span
        className="
          text-[10px]
          font-semibold
          uppercase
          tracking-[0.14em]
          text-accentBlue
        "
      >
        {category}
      </span>
    </div>
  );
}

function MetaCard({ icon, label, value }) {
  return (
    <div
      className="
        rounded-xl
        border
        border-border
        bg-background/40
        px-4
        py-3
      "
    >
      <div className="flex items-center gap-2 text-secondary">
        {icon}

        <span
          className="
            text-[10px]
            font-medium
            uppercase
            tracking-[0.14em]
          "
        >
          {label}
        </span>
      </div>

      <p
        className="
          mt-2
          font-mono
          text-sm
          font-medium
          text-primary
        "
      >
        {value}
      </p>
    </div>
  );
}

/* ================================================================== */
/* HELPERS */
/* ================================================================== */

function formatCurrentTime() {
  return new Intl.DateTimeFormat("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
}

function formatElapsedTime(seconds) {
  const safeSeconds = Math.max(
    0,
    Number(seconds) || 0
  );

  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor(
    (safeSeconds % 3600) / 60
  );
  const secs = safeSeconds % 60;

  const parts = [];

  if (hours > 0) {
    parts.push(String(hours).padStart(2, "0"));
  }

  parts.push(String(minutes).padStart(2, "0"));
  parts.push(String(secs).padStart(2, "0"));

  return parts.join(":");
}

function formatLessonType(type) {
  const normalized = String(type || "")
    .trim()
    .toUpperCase();

  switch (normalized) {
    case "LECTURE":
      return "Лекция";

    case "PRACTICE":
      return "Практика";

    case "LAB":
      return "Лабораторная";

    case "EXAM":
      return "Экзамен";

    default:
      return type || "Занятие";
  }
}

function formatVerificationStatus(status) {
  switch (status) {
    case "approved":
      return "Подтверждено";

    case "rejected":
      return "Отклонено";

    case "partial":
      return "Частично";

    case "pending":
      return "На проверке";

    default:
      return "Не требуется";
  }
}