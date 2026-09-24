import React, { useCallback, useEffect, useState } from "react";
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
  FiAlertTriangle,
} from "react-icons/fi";

const FILTER_EVENT_NAME =
  "xo-os:schedule-filters-changed";
const GAMIFICATION_UPDATE_EVENT_NAME =
  "xo-os:gamification-updated";

const EMPTY_NOW = {
  taskTitle: "",
  taskDesc: "",
  timeEstimate: "",
  priority: "",
  xpReward: 0,
  time": "--:--",
  category: "",
};

export default function NowBlock() {
  const [now, setNow] = useState(EMPTY_NOW);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [currentTime, setCurrentTime] = useState(
    formatCurrentTime()
  );
  // State for showing a temporary completion message
  const [completionMessage, setCompletionMessage] = useState(null);
  const [completionMessageType, setCompletionMessageType] = useState(''); // 'success' or 'error'

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

        setNow({
          ...EMPTY_NOW,
          ...data,
        });
        // Clear any completion message when we get new data (unless we are showing a completion message that we want to keep for a bit)
        // We'll handle the completion message separately with a timeout.
      } catch (error) {
        console.error(
          "Failed to fetch current lesson:",
          error
        );

        setNow(EMPTY_NOW);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    []
  );

  /*
   * Initial load + automatic refresh.
   */
  useEffect(() => {
    loadNow();

    const interval = window.setInterval(() => {
      loadNow(true);
    }, 15000);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadNow]);

  /*
   * Live clock.
   */
  useEffect(() => {
    const updateClock = () => {
      setCurrentTime(formatCurrentTime());
    };

    updateClock();

    const interval = window.setInterval(
      updateClock,
      1000
    );

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  /*
   * Listen to Server-Sent Events for real-time updates
   * When we receive events, we dispatch the corresponding window events
   * so that the existing event listeners continue to work.
   */
  useEffect(() => {
    // Connect to the SSE endpoint
    const eventSource = new EventSource("/api/events");

    // Handle focus updated events
    eventSource.addEventListener("xo-os:focus-updated", (event) => {
      // Dispatch the custom event for backward compatibility
      window.dispatchEvent(new CustomEvent("xo-os:focus-updated"));
      // Reload the now block to get updated focus session data
      loadNow(true);
    });

    // Handle gamification updated events
    eventSource.addEventListener("xo-os:gamification-updated", (event) => {
      // Dispatch the custom event for backward compatibility
      window.dispatchEvent(new CustomEvent("xo-os:gamification-updated"));
    });

    // Handle connection errors
    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
    };

    // Clean up the event source when the component unmounts
    return () => {
      eventSource.close();
    };
  }, [loadNow]);

  /*
   * Handle completion message timeout
   */
  useEffect(() => {
    if (completionMessage) {
      const timeout = setTimeout(() => {
        setCompletionMessage(null);
        setCompletionMessageType('');
      }, 3000); // 3 seconds

      return () => {
        clearTimeout(timeout);
      };
    }
  }, [completionMessage]);

  const hasTask = Boolean(now.taskTitle) || now.type === 'focus';

  // Determine if we are in a focus session that is active or paused
  const isFocusActive = now.type === 'focus' && now.status === 'active';
  const isFocusPaused = now.type === 'focus' && now.status === 'paused';
  const isFocusCompleted = now.type === 'focus' && now.status === 'completed';

  // Format the elapsed time for display
  const formatElapsedTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    const parts = [];
    if (hours > 0) {
      parts.push(String(hours).padStart(2, '0'));
    }
    parts.push(String(minutes).padStart(2, '0'));
    parts.push(String(secs).padStart(2, '0'));
    return parts.join(':');
  };

  // Start a focus session
  const handleStartFocus = async () => {
    try {
      setLoading(true);
      // We don't have the lesson_id or goal_text from the now block, but the backend will determine the current lesson.
      // We'll just call the start endpoint without parameters.
      const response = await fetch("/api/focus/start", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // The response will contain the session data, but we will update via polling.
    } catch (error) {
      console.error("Failed to start focus session:", error);
      setCompletionMessage("Не удалось начать фокус-сессию");
      setCompletionMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // Pause the focus session
  const handlePauseFocus = async () => {
    if (!now.session_id) return;
    try {
      setLoading(true);
      const response = await fetch(
        `/api/focus/${now.session_id}/pause`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      // Update via polling
    } catch (error) {
      console.error("Failed to pause focus session:", error);
      setCompletionMessage("Не удалось поставить на паузу");
      setCompletionMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // Resume the focus session
  const handleResumeFocus = async () => {
    if !now.session_id) return;
    try {
      setLoading(true);
      const response = await fetch(
        `/api/focus/${now.session_id}/resume`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      // Update via polling
    } catch (error) {
      console.error("Failed to resume focus session:", error);
      setCompletionMessage("Не удалось продолжить");
      setCompletionMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // Complete the focus session - this will show a modal
  // We'll handle the modal state in this component for simplicity.
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [completionMode, setCompletionMode] = useState(null); // 'manual' or 'ai_verified'
  const [evidence, setEvidence] = useState([]); // For AI verification, we might need to collect evidence

  const handleCompleteFocus = async () => {
    // We are going to show a modal to choose completion mode and optionally add evidence.
    setShowCompleteModal(true);
  };

  const handleCompleteModalClose = () => {
    setShowCompleteModal(false);
    setCompletionMode(null);
    setEvidence([]);
  };

  const handleCompleteModalSubmit = async () => {
    if (!now.session_id) {
      setShowCompleteModal(false);
      return;
    }

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
            completion_mode: completionMode,
            evidence: evidence,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // We expect the response to contain the session data after completion.
      // However, for AI verification, the verification might be pending.
      // We will update via polling and also show a completion message.

      setCompletionMessage(
        `Сессия завершена! +${data.xp_awarded || 0} XP`
      );
      setCompletionMessageType(
        data.verification_status === 'approved' ? 'success' : 'pending'
      );

      // Close the modal
      setShowCompleteModal(false);
      setCompletionMode(null);
      setEvidence([]);
    } catch (error) {
      console.error("Failed to complete focus session:", error);
      setCompletionMessage("Не удалось завершить сессию");
      setCompletionMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // If we are in a focus session, we want to update the elapsed time more frequently
  // We'll use a separate interval for the timer.
  useEffect(() => {
    if (isFocusActive || isFocusPaused) {
      const timerInterval = window.setInterval(() => {
        // We don't need to fetch the whole state, just update the elapsed time.
        // But we don't have the started_at and paused state in the component state.
        // So we will rely on the polling of the now endpoint to update the elapsed seconds.
        // We'll just set a shorter polling interval for the now endpoint when in focus.
        // However, we already have a 15s interval. Let's change it to 5s when in focus.
        // We'll adjust the loadNow interval dynamically? Alternatively, we can just use a separate timer for the display.
        // We'll compute the elapsed time based on the started_at and paused_at that we have in the now state.
        // But we don't store the started_at in the component state.
        // We will store the started_at and paused_at in the component state when we get the focus session.
        // Let's change the now state to include more fields for focus sessions.
        // We already have: session_id, status, lesson_id, lesson_subject, lesson_description, goal_text, started_at, elapsed_seconds.
        // We can use the elapsed_seconds from the now state for the timer.
        // So we don't need a separate timer for the display, we can just use the elapsed_seconds from the state.
        // However, the elapsed_seconds in the state is updated only every 15s by the polling.
        // We want to update the display every second.
        // Therefore, we will start a timer that updates the displayed elapsed time every second,
        // but we will keep the actual elapsed_seconds from the state as the source of truth for when we need to send to the backend.
        // We'll store the elapsed time for display in a separate state variable.
        // We'll initialize it from the now.elapsed_seconds and then update it every second.
        // When we get a new now state, we reset the display elapsed time to the now.elapsed_seconds.
      }, 1000);

      return () => {
        window.clearInterval(timerInterval);
      };
    }
  }, [isFocusActive, isFocusPaused, now.elapsed_seconds]);

  // We'll create a state variable for the displayed elapsed time.
  const [displayedElapsedSeconds, setDisplayedElapsedSeconds] = useState(0);

  useEffect(() => {
    if (isFocusActive || isFocusPaused) {
      // Initialize the displayed elapsed time from the now state
      setDisplayedElapsedSeconds(now.elapsed_seconds || 0);

      const interval = window.setInterval(() => {
        setDisplayedElapsedSeconds((prev) => prev + 1);
      }, 1000);

      return () => {
        window.clearInterval(interval);
      };
    } else {
      setDisplayedElapsedSeconds(0);
    }
  }, [isFocusActive, isFocusPaused, now.elapsed_seconds]);

  // When we get a new now state that is a focus session, we reset the displayed elapsed time to the now.elapsed_seconds
  useEffect(() => {
    if (now.type === 'focus' && (now.status === 'active' || now.status === 'paused')) {
      setDisplayedElapsedSeconds(now.elapsed_seconds || 0);
    }
  }, [now.type, now.status, now.elapsed_seconds]);

  const formattedDisplayedElapsed = formatElapsedTime(displayedElapsedSeconds);

  return (
    <section
      className="
        group
        relative
        overflow-hidden
        rounded-2xl
        border
        border-border
        bg-panel
        p-6
        transition-all
        duration-300
        ease-out
        hover:border-accentBlue/30
        hover:shadow-[0_12px_40px_rgba(0,0,0,0.22)]
      "
    >
      {/* Glow */}
      <div
        className="
          pointer-events-none
          absolute
          -right-16
          -top-16
          h-32
          w-32
          rounded-full
          bg-accentBlue/10
          blur-3xl
          opacity-50
          transition-opacity
          duration-300
          group-hover:opacity-80
        "
      />

      {/* Header */}
      <div
        className="
          relative
          flex
          items-center
          justify-between
          border-b
          border-border
          pb-4
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
              rounded-xl
              border
              border-accentBlue/20
              bg-accentBlue/10
              text-accentBlue
              transition-all
              duration-300
              group-hover:border-accentBlue/30
              group-hover:bg-accentBlue/15
            "
          >
            {now.type === 'focus' ? (
              <FiClock size={16} />
            ) : (
              <FiBookOpen size={16} />
            )}
          </div>

          <div>
            <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-secondary">
              {now.type === 'focus' ? 'Текущий фокус' : 'Сегодняшнее занятие'}
            </p>

            <h2 className="mt-0.5 text-lg font-semibold tracking-tight text-primary">
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
              bg-background/60
              px-3
              py-1.5
              font-mono
              text-xs
              font-medium
              text-secondary
            "
          >
            {currentTime}
          </span>
        </div>
      </div>

      {/* Completion Message Banner */}
      {completionMessage && (
        <div
          className="
            mt-4
            px-4
            py-2
            rounded-lg
            text-sm
            font-medium
            flex
            items-center
            justify-between
            ${completionMessageType === 'success'
              ? 'bg-accentGreen/10 border border-accentGreen/20 text-accentGreen'
              : completionMessageType === 'error'
                ? 'bg-accentRed/10 border border-accentRed/20 text-accentRed'
                : 'bg-accentYellow/10 border border-accentYellow/20 text-accentYellow'}
          "
        >
          <div>{completionMessage}</div>
          {completionMessageType !== 'pending' && (
            <FiX
              size={14}
              className="cursor-pointer"
              onClick={() => {
                setCompletionMessage(null);
                setCompletionMessageType('');
              }}
            />
          )}
        </div>
      )}

      {/* Content */}
      <div className="relative mt-5">
        {loading ? (
          <div className="space-y-4 animate-pulse">
            <div className="h-8 w-2/3 rounded-lg bg-background" />
            <div className="h-4 w-24 rounded bg-background" />
            <div className="h-4 w-4/5 rounded bg-background" />

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="h-12 rounded-xl bg-background" />
              <div className="h-12 rounded-xl bg-background" />
            </div>

            <div className="h-12 rounded-xl bg-background" />
          </div>
        ) : now.type === 'idle' ? (
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
              bg-background/40
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
              className="
                mt-5
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
                py-3
                text-sm
                font-semibold
                text-white
                shadow-[0_8px_24px_rgba(30,130,255,0.14)]
                transition-all
                duration-200
                ease-out
                hover:-translate-y-0.5
                hover:bg-accentBlue/90
                hover:shadow-[0_12px_30px_rgba(30,130,255,0.2)]
                active:translate-y-0
                active:scale-[0.99]
              "
              onClick={handleStartFocus}
            >
              <FiPlay size={15} />
              НАЧАТЬ
            </button>
          </div>
        ) : now.type === 'lesson' ? (
          <>
            {/* Main */}
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
                    {now.lesson_subject}
                  </p>

                  {now.category && (
                    <div className="mt-3 inline-flex items-center gap-2 rounded-lg border border-accentBlue/15 bg-accentBlue/10 px-2.5 py-1.5">
                      <FiBookOpen
                        size={12}
                        className="text-accentBlue"
                      />

                      <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-accentBlue">
                        {now.category}
                      </span>
                    </div>
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

            {/* Meta */}
            <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div
                className="
                  rounded-xl
                  border
                  border-border
                  bg-background/50
                  px-4
                  py-3
                  transition-all
                  duration-200
                  hover:border-accentBlue/20
                  hover:bg-background/70
                "
              >
                <div className="flex items-center gap-2 text-secondary">
                  <FiClock size={14} />

                  <span className="text-[10px] font-medium uppercase tracking-[0.14em]">
                    Время занятия
                  </span>
                </div>

                <p className="mt-2 font-mono text-sm font-medium text-primary">
                  {now.time_estimate || "Не указано"}
                </p>
              </div>

              <div
                className="
                  rounded-xl
                  border
                  border-border
                  bg-background/50
                  px-4
                  py-3
                  transition-all
                  duration-200
                  hover:border-accentYellow/20
                  hover:bg-background/70
                "
              >
                <div className="flex items-center gap-2 text-secondary">
                  <FiFlag size={14} />

                  <span className="text-[10px] font-medium uppercase tracking-[0.14em]">
                    Тип
                  </span>
                </div>

                <p className="mt-2 text-sm font-medium text-primary">
                  {formatLessonType(now.priority)}
                </p>
              </div>
            </div>

            {/* XP Preview and Start Button */}
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

                <span className="text-xs font-medium uppercase tracking-[0.14em] text-secondary">
                  Награда за фокус
                </span>
              </div>

              <span className="font-mono text-sm font-semibold text-accentYellow">
                +{now.completion_mode === 'manual' ? 3 : 10} XP
              </span>
            </div>

            <button
              type="button"
              className="
                mt-5
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
                py-3
                text-sm
                font-semibold
                text-white
                shadow-[0_8px_24px_rgba(30,130,255,0.14)]
                transition-all
                duration-200
                ease-out
                hover:-translate-y-0.5
                hover:bg-accentBlue/90
                hover:shadow-[0_12px_30px_rgba(30,130,255,0.2)]
                active:translate-y-0
                active:scale-[0.99]
              "
              onClick={handleStartFocus}
            >
              <FiPlay size={15} />
              НАЧАТЬ ФОКУС
            </button>
          </>
        ) : now.type === 'focus' ? (
          <>
            {/* Main */}
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
                    {now.lesson_subject || 'Без урока'}
                  </p>

                  {now.category && (
                    <div className="mt-3 inline-flex items-center gap-2 rounded-lg border border-accentBlue/15 bg-accentBlue/10 px-2.5 py-1.5">
                      <FiBookOpen
                        size={12}
                        className="text-accentBlue"
                      />

                      <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-accentBlue">
                        {now.category}
                      </span>
                    </div>
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

              {now.goal_text && (
                <p
                  className="
                    mt-2
                    text-sm
                    leading-5
                    text-secondary
                  "
                >
                  Цель: {now.goal_text}
                </p>
              )}
            </div>

            {/* Timer and Controls */}
            <div className="mt-6">
              <div className="text-center mb-4">
                <p className="text-xs font-medium uppercase tracking-[0.14em] text-secondary">
                  Затраченное время
                </p>
                <p className="font-mono text-2xl font-semibold text-primary">
                  {formattedDisplayedElapsed}
                </p>
              </div>

              <div className="flex items-center justify-between">
                {isFocusActive && (
                  <>
                    <button
                      type="button"
                      className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        rounded-xl
                        border
                        border-accentYellow/20
                        bg-accentYellow/5
                        px-3
                        py-2
                        text-sm
                        font-medium
                        text-accentYellow
                        hover:bg-accentYellow/10
                      "
                      onClick={handlePauseFocus}
                    >
                      <FiPause size={16} />
                      ПАУЗА
                    </button>

                    <button
                      type="button"
                      className="
                        ml-3
                        flex
                        items-center
                        justify-center
                        gap-2
                        rounded-xl
                        border
                        border-accentBlue/20
                        bg-accentBlue
                        px-3
                        py-2
                        text-sm
                        font-semibold
                        text-white
                        shadow-[0_8px_24px_rgba(30,130,255,0.14)]
                        transition-all
                        duration-200
                        ease-out
                        hover:-translate-y-0.5
                        hover:bg-accentBlue/90
                        hover:shadow-[0_12px_30px_rgba(30,130,255,0.2)]
                        active:translate-y-0
                        active:scale-[0.99]
                      "
                      onClick={handleCompleteFocus}
                    >
                      <FiCheckCircle size={16} />
                      ЗАВЕРШИТЬ
                    </button>
                  </>
                )}

                {isFocusPaused && (
                  <>
                    <button
                      type="button"
                      className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        rounded-xl
                        border
                        border-accentYellow/20
                        bg-accentYellow/5
                        px-3
                        py-2
                        text-sm
                        font-medium
                        text-accentYellow
                        hover:bg-accentYellow/10
                      "
                      onClick={handleResumeFocus}
                    >
                      <FiPlay size={16} />
                      ПРОДОЛЖИТЬ
                    </button>

                    <button
                      type="button"
                      className="
                        ml-3
                        flex
                        items-center
                        justify-center
                        gap-2
                        rounded-xl
                        border
                        border-accentBlue/20
                        bg-accentBlue
                        px-3
                        py-2
                        text-sm
                        font-semibold
                        text-white
                        shadow-[0_8px_24px_rgba(30,130,255,0.14)]
                        transition-all
                        duration-200
                        ease-out
                        hover:-translate-y-0.5
                        hover:bg-accentBlue/90
                        hover:shadow-[0_12px_30px_rgba(30,130,255,0.2)]
                        active:translate-y-0
                        active:scale-[0.99]
                      "
                      onClick={handleCompleteFocus}
                    >
                      <FiCheckCircle size={16} />
                      ЗАВЕРШИТЬ
                    </button>
                  </>
                )}

                {isFocusCompleted && (
                  <div>
                    <span className="text-xs font-medium uppercase tracking-[0.14em] text-secondary">
                      Статус:
                    </span>
                    <span className="font-mono text-sm font-medium">
                      {now.verification_status === 'approved'
                        ? 'Подтверждено'
                        : now.verification_status === 'rejected'
                          ? 'Отклонено'
                          : now.verification_status === 'partial'
                            ? 'Частично'
                            : 'Не требуется'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div>Неизвестное состояние</div>
        )}
      </div>

      {/* Complete Focus Session Modal */}
      {showCompleteModal && (
        <div
          className="
            fixed
            inset-0
            bg-black/50
            flex
            items-center
            justify-center
            z-50
            backdrop-blur-sm
          "
        >
          <div
            className="
              relative
              bg-panel
              rounded-2xl
              p-6
              w-96
              max-w-full
              shadow-2xl
              border
              border-border
            "
          >
            <div className="flex items-center justify-between mb-4">
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
                  <FiBookOpen size={18} />
                </div>

                <div>
                  <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-secondary">
                    Как завершить фокус-сессию?
                  </p>

                  <h2 className="mt-0.5 text-lg font-semibold tracking-tight text-primary">
                    ЗАВЕРШЕНИЕ
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="
                  p-1
                  rounded-xl
                  border
                  border-transparent
                  hover:border-accentBlue/20
                  hover:bg-accentBlue/5
                "
                onClick={handleCompleteModalClose}
              >
                <FiX size={18} className="text-secondary" />
              </button>
            </div>

            <div className="mb-6">
              <p className="text-[10px] font-medium uppercase tracking-[0.14em] text-secondary">
                Выберите способ завершения:
              </p>
              <div className="mt-4 space-y-3">
                <div
                  className="
                    flex
                    items-center
                    justify-between
                    rounded-xl
                    border
                    border-accentBlue/20
                    bg-accentBlue/5
                    px-4
                    py-3
                  "
                >
                  <div className="flex items-center gap-3">
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
                      <FiZap size={14} />
                    </div>

                    <div>
                      <span className="text-xs font-medium uppercase tracking-[0.14em]">
                        Завершить вручную
                      </span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="
                      w-full
                      text-left
                      py-2
                      px-3
                      rounded-lg
                      border
                      border-transparent
                      hover:bg-accentBlue/5
                    "
                    onClick={() => {
                      setCompletionMode('manual');
                      setEvidence([]);
                      handleCompleteModalSubmit();
                    }}
                  >
                    Получить базовую награду (3 XP)
                  </button>
                </div>

                {/* AI Verification Option - only show if AI verification is enabled in user settings */}
                {/* We don't have the user settings in this component, so we'll assume it's enabled for now.
                   In a real implementation, we would fetch the user settings or have it passed in via context or props. */}
                <div
                  className="
                    flex
                    items-center
                    justify-between
                    rounded-xl
                    border
                    border-accentBlue/20
                    bg-accentBlue/5
                    px-4
                    py-3
                  "
                >
                  <div className="flex items-center gap-3">
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
                      <FiZap size={14} />
                    </div>

                    <div>
                      <span className="text-xs font-medium uppercase tracking-[0.14em]">
                        Отправить на проверку AI
                      </span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="
                      w-full
                      text-left
                      py-2
                      px-3
                      rounded-lg
                      border
                      border-transparent
                      hover:bg-accentBlue/5
                    "
                    onClick={() => {
                      setCompletionMode('ai_verified');
                      // We would need to collect evidence here, but for now we'll leave it empty.
                      // In a real implementation, we would show a form to add evidence.
                      setEvidence([]);
                      handleCompleteModalSubmit();
                    }}
                  >
                    Получить основную награду (10 XP) + бонус за результат
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      )}
    </section>
  );
}

function formatCurrentTime() {
  return new Intl.DateTimeFormat("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
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