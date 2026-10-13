import React, { useEffect, useRef, useState } from "react";
import { FiBell, FiCheck, FiTrash2 } from "react-icons/fi";

// ============================================================
// Форматирование даты — «5 минут назад», «вчера», «12.10.2026»
// ============================================================
const formatRelativeTime = (isoString) => {
    try {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMin = Math.floor(diffMs / 60000);

        if (diffMin < 1) return "только что";
        if (diffMin < 60) return `${diffMin} мин назад`;

        const diffHours = Math.floor(diffMin / 60);
        if (diffHours < 24) return `${diffHours} ч назад`;

        const diffDays = Math.floor(diffHours / 24);
        if (diffDays === 1) return "вчера";
        if (diffDays < 7) return `${diffDays} дн назад`;

        return date.toLocaleDateString("ru-RU", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
        });
    } catch {
        return "";
    }
};

// ============================================================
// Одна строка уведомления
// ============================================================
const NotificationRow = ({ notification, onMarkRead, onDelete }) => {
    const [hovered, setHovered] = useState(false);

    return (
        <div
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            className={`
        relative flex gap-3
        border-b border-border/50 px-4 py-3
        transition-colors duration-150
        ${notification.is_read ? "bg-transparent" : "bg-accentBlue/5"}
      `}
        >
            <div className="mt-1.5 h-2 w-2 shrink-0">
                {!notification.is_read && (
                    <span className="block h-2 w-2 rounded-full bg-accentBlue" />
                )}
            </div>

            <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-text-primary">
                    {notification.title}
                </div>

                {notification.message && (
                    <div className="mt-1 text-xs leading-5 text-text-secondary">
                        {notification.message}
                    </div>
                )}

                <div className="mt-1 text-[11px] text-text-muted">
                    {formatRelativeTime(notification.created_at)}
                </div>
            </div>

            {/* Кнопки действий — на hover */}
            <div
                className={`
          absolute right-3 top-3
          flex items-center gap-1
          transition-opacity duration-150
          ${hovered ? "opacity-100" : "opacity-0 pointer-events-none"}
        `}
            >
                {!notification.is_read && (
                    <button
                        type="button"
                        onClick={() => onMarkRead(notification.id)}
                        title="Отметить прочитанным"
                        className="
              flex h-6 w-6 items-center justify-center
              rounded-md border border-border bg-panel
              text-text-muted
              transition-all duration-150
              hover:border-accentBlue hover:text-accentBlue
            "
                    >
                        <FiCheck className="h-3.5 w-3.5" />
                    </button>
                )}

                <button
                    type="button"
                    onClick={() => onDelete(notification.id)}
                    title="Удалить"
                    className="
            flex h-6 w-6 items-center justify-center
            rounded-md border border-border bg-panel
            text-text-muted
            transition-all duration-150
            hover:border-accentRed hover:text-accentRed
          "
                >
                    <FiTrash2 className="h-3.5 w-3.5" />
                </button>
            </div>
        </div>
    );
};

// ============================================================
// Live-строка: прогресс переноса календаря
// ============================================================
const SwitchProgressRow = ({ progress }) => {
    if (!progress) return null;

    const percent = progress.percent || 0;
    const source = progress.source_calendar_name || "календаря";
    const target = progress.target_calendar_name || "календарь";
    const isCompleted = progress.status === "completed";
    const isFailed = progress.status === "failed";

    return (
        <div className="border-b border-border/50 bg-accentBlue/5 px-4 py-3">
            <div className="flex items-center gap-2">
                <span className="h-2 w-2 shrink-0 rounded-full bg-accentBlue animate-pulse" />
                <span className="text-sm font-medium text-text-primary">
                    {isFailed
                        ? `Ошибка переноса`
                        : isCompleted
                            ? `Перенос завершён`
                            : `Перенос событий`}
                </span>
            </div>

            <div className="mt-1.5 pl-4 text-xs text-text-secondary">
                {source} → {target}
            </div>

            {!isFailed && (
                <>
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-border">
                        <div
                            className={`
                h-full rounded-full
                transition-all duration-500 ease-out
                ${isCompleted ? "bg-accentGreen" : "bg-accentBlue"}
              `}
                            style={{ width: `${percent}%` }}
                        />
                    </div>

                    <div className="mt-1 flex justify-between text-[11px] text-text-muted">
                        <span>
                            {progress.processed} из {progress.total}
                        </span>
                        <span className="font-mono">{percent}%</span>
                    </div>
                </>
            )}

            {isFailed && progress.error_message && (
                <div className="mt-1 pl-4 text-[11px] text-accentRed">
                    {progress.error_message}
                </div>
            )}
        </div>
    );
};

// ============================================================
// Основной компонент
// ============================================================
const NotificationBell = () => {
    const [open, setOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [switchProgress, setSwitchProgress] = useState(null);
    const [loading, setLoading] = useState(false);

    const dropdownRef = useRef(null);

    // ---- Загрузка списка уведомлений ----
    const fetchNotifications = async () => {
        try {
            const resp = await fetch("/api/notifications", {
                credentials: "include",
            });
            if (resp.ok) {
                const data = await resp.json();
                setNotifications(data || []);
                setUnreadCount((data || []).filter((n) => !n.is_read).length);
            }
        } catch {
            // игнорируем
        }
    };

    // ---- Загрузка прогресса переноса календаря ----
    const fetchSwitchProgress = async () => {
        try {
            const resp = await fetch("/api/google/calendar/switch-progress", {
                credentials: "include",
            });
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.active || data.status === "completed" || data.status === "failed") {
                setSwitchProgress(data);
                // Если перенос идёт или только завершился — перезагружаем список уведомлений
                // (бэкенд мог создать уведомление «перенос завершён»)
                if (data.status === "completed") {
                    fetchNotifications();
                }
            } else {
                setSwitchProgress(null);
            }
        } catch {
            // игнорируем
        }
    };

    // ---- Первичная загрузка + опрос раз в 5 сек ----
    useEffect(() => {
        fetchNotifications();
        fetchSwitchProgress();

        const interval = setInterval(() => {
            fetchSwitchProgress();
            if (!open) {
                // Список обновляем реже, только когда панель закрыта
                fetchNotifications();
            }
        }, 5000);

        return () => clearInterval(interval);
    }, [open]);

    // ---- Закрытие по клику вне панели ----
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setOpen(false);
            }
        };
        if (open) {
            document.addEventListener("mousedown", handleClickOutside);
        }
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [open]);

    // ---- Действия ----
    const handleMarkRead = async (id) => {
        try {
            await fetch(`/api/notifications/${id}/read`, {
                method: "POST",
                credentials: "include",
            });
            setNotifications((prev) =>
                prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
            );
            setUnreadCount((prev) => Math.max(0, prev - 1));
        } catch {
            // игнорируем
        }
    };

    const handleMarkAllRead = async () => {
        try {
            await fetch("/api/notifications/read-all", {
                method: "POST",
                credentials: "include",
            });
            setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
            setUnreadCount(0);
        } catch {
            // игнорируем
        }
    };

    const handleDelete = async (id) => {
        try {
            const resp = await fetch(`/api/notifications/${id}`, {
                method: "DELETE",
                credentials: "include",
            });
            if (!resp.ok) return;

            // Плавно убираем из UI
            setNotifications((prev) => {
                const removed = prev.find((n) => n.id === id);
                if (removed && !removed.is_read) {
                    setUnreadCount((c) => Math.max(0, c - 1));
                }
                return prev.filter((n) => n.id !== id);
            });
        } catch {
            // игнорируем
        }
    };

    const handleDeleteAll = async () => {
        try {
            const resp = await fetch("/api/notifications", {
                method: "DELETE",
                credentials: "include",
            });
            if (!resp.ok) return;

            setNotifications([]);
            setUnreadCount(0);
        } catch {
            // игнорируем
        }
    };

    // ---- Логика «горит ли колокольчик» ----
    const switchActive = !!switchProgress && switchProgress.status === "running";
    const hasUnread = unreadCount > 0;
    const isGlowing = switchActive || hasUnread;

    // Бейдж: количество непрочитанных + 1 за прогресс, если он активен
    const badgeCount = unreadCount + (switchActive ? 1 : 0);

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Кнопка колокольчика */}
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className={`
          relative flex h-9 w-9 items-center justify-center
          rounded-lg
          transition-colors duration-200
          hover:bg-background/60
          ${open ? "bg-background/60" : ""}
        `}
                title="Уведомления"
            >
                <FiBell
                    className={`
            h-5 w-5
            transition-colors duration-200
            ${isGlowing ? "text-accentBlue" : "text-text-secondary"}
          `}
                />

                {/* Пульсирующее кольцо при активном переносе */}
                {switchActive && (
                    <span className="absolute inset-0 rounded-lg ring-2 ring-accentBlue/50 animate-pulse" />
                )}

                {/* Бейдж с числом */}
                {badgeCount > 0 && (
                    <span
                        className="
              absolute -right-0.5 -top-0.5 z-[100]
              flex h-4 min-w-[16px] items-center justify-center
              rounded-full bg-accentBlue
              px-1
              text-[10px] font-bold text-white
            "
                    >
                        {badgeCount > 9 ? "9+" : badgeCount}
                    </span>
                )}
            </button>

            {/* Выпадающая панель */}
            <div
                className={`
                        absolute right-0 top-12 z-[100]
                        w-96
                        origin-top-right
                        overflow-hidden
                        rounded-xl border border-border
                        bg-panel
                        shadow-xl
                        transition-all duration-300 ease-out
                        ${open
                        ? "opacity-100 scale-100 translate-y-0 pointer-events-auto"
                        : "opacity-0 scale-95 -translate-y-2 pointer-events-none duration-300"
                    }
                    `}
            >
                {/* Заголовок с кнопкой «Отметить все прочитанными» */}
                <div className="flex items-center justify-between border-b border-border/60 px-4 py-3">
                    <span className="text-sm font-semibold text-text-primary">
                        Уведомления
                    </span>

                    <div className="flex items-center gap-1">
                        {unreadCount > 0 && (
                            <button
                                type="button"
                                onClick={handleMarkAllRead}
                                title="Отметить все прочитанными"
                                className="
        flex items-center gap-1
        rounded-md px-2 py-1
        text-xs font-medium
        text-accentBlue
        transition-colors duration-150
        hover:bg-accentBlue/10
      "
                            >
                                <FiCheck className="h-3.5 w-3.5" />
                                Прочитать все
                            </button>
                        )}

                        {notifications.length > 0 && (
                            <button
                                type="button"
                                onClick={handleDeleteAll}
                                title="Удалить все"
                                className="
                                        flex items-center gap-1
                                        rounded-md px-2 py-1
                                        text-xs font-medium
                                        text-accentRed
                                        transition-colors duration-150
                                        hover:bg-accentRed/10
                                    "
                            >
                                <FiTrash2 className="h-3.5 w-3.5" />
                                Удалить все
                            </button>
                        )}
                    </div>
                </div>

                {/* Тело со скроллом: max-height ~3 строки */}
                <div className="max-h-80 overflow-y-auto">
                    {/* Live-прогресс переноса — всегда наверху */}
                    {switchProgress && (
                        <SwitchProgressRow progress={switchProgress} />
                    )}

                    {notifications.length === 0 && !switchProgress ? (
                        <div className="px-4 py-8 text-center text-sm text-text-muted">
                            Пока ничего нового
                        </div>
                    ) : (
                        notifications.map((n) => (
                            <NotificationRow
                                key={n.id}
                                notification={n}
                                onMarkRead={handleMarkRead}
                                onDelete={handleDelete}
                            />
                        )))
                    }
                </div>
            </div>

        </div>
    );
};

export default NotificationBell;