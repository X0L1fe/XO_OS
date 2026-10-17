import React, { useState, useEffect, useMemo } from "react";
import {
  FiShield,
  FiCalendar,
  FiSend,
  FiBookOpen,
  FiSettings as FiSettingsIcon,
  FiCheckCircle,
  FiAlertCircle,
  FiRefreshCw,
  FiCopy,
  FiExternalLink,
  FiSave,
  FiChevronRight,
  FiChevronDown,
  FiXCircle,
  FiDroplet,
  FiUsers,
  FiSearch,
  FiLoader,
  FiArrowRight,
  FiCheck,
} from "react-icons/fi";

const COLOR_OPTIONS = [
  { key: "LECTURE", label: "Лекции (ЛК)" },
  { key: "PRACTICE", label: "Практики (ПЗ)" },
  { key: "LAB", label: "Лабораторные (ЛР)" },
  { key: "EXAM", label: "Экзамены (Э)" },
];
const CUSTOM_SLOT_KEYS = [
  "custom_1", "custom_2", "custom_3",
  "custom_4", "custom_5", "custom_6",
];

const SectionIcon = ({ children, tone = "blue" }) => {
  const toneClasses = {
    blue: "bg-accent-blue/10 text-accent-blue border-accent-blue/20",
    yellow: "bg-accent-yellow/10 text-accent-yellow border-accent-yellow/20",
    green: "bg-accent-green/10 text-accent-green border-accent-green/20",
    purple: "bg-accent-purple/10 text-accent-purple border-accent-purple/20",
  };

  return (
    <div
      className={`
        flex h-10 w-10 shrink-0
        items-center justify-center
        rounded-lg border
        ${toneClasses[tone]}
      `}
    >
      {children}
    </div>
  );
};


const StatusBadge = ({
  type = "neutral",
  children,
}) => {
  const styles = {
    success:
      "border-accent-green/20 bg-accent-green/10 text-accent-green",
    error:
      "border-accent-red/20 bg-accent-red/10 text-accent-red",
    warning:
      "border-accent-yellow/20 bg-accent-yellow/10 text-accent-yellow",
    neutral:
      "border-border bg-background text-text-secondary",
    blue:
      "border-accent-blue/20 bg-accent-blue/10 text-accent-blue",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-2
        rounded-full border
        px-3 py-1.5
        text-xs font-medium
        ${styles[type]}
      `}
    >
      {children}
    </span>
  );
};


const PrimaryButton = ({
  children,
  icon: Icon,
  className = "",
  ...props
}) => {
  return (
    <button
      {...props}
      className={`
        inline-flex
        items-center
        justify-center
        gap-2
        rounded-lg
        border
        border-accent-blue
        bg-accent-blue
        px-4
        py-2.5
        text-sm
        font-semibold
        text-white
        shadow-[0_0_18px_rgba(22,131,255,0.12)]
        transition-all
        duration-180
        hover:bg-accent-blue/90
        hover:shadow-[0_0_22px_rgba(22,131,255,0.20)]
        focus:outline-none
        focus:ring-2
        focus:ring-accent-blue/30
        disabled:cursor-not-allowed
        disabled:opacity-50
        ${className}
      `}
    >
      {Icon && <Icon className="h-4 w-4" />}
      {children}
    </button>
  );
};


const SecondaryButton = ({
  children,
  icon: Icon,
  className = "",
  ...props
}) => {
  return (
    <button
      {...props}
      className={`
        inline-flex
        items-center
        justify-center
        gap-2
        rounded-lg
        border
        border-border
        bg-background
        px-4
        py-2.5
        text-sm
        font-medium
        text-text-primary
        transition-all
        duration-180
        hover:border-accent-blue/40
        hover:bg-accent-blue/10
        hover:text-accent-blue
        focus:outline-none
        focus:ring-2
        focus:ring-accent-blue/20
        disabled:cursor-not-allowed
        disabled:opacity-50
        ${className}
      `}
    >
      {Icon && <Icon className="h-4 w-4" />}
      {children}
    </button>
  );
};


const DangerButton = ({
  children,
  icon: Icon,
  className = "",
  ...props
}) => {
  return (
    <button
      {...props}
      className={`
        inline-flex
        items-center
        justify-center
        gap-2
        rounded-lg
        border
        border-accent-red/25
        bg-accent-red/10
        px-4
        py-2.5
        text-sm
        font-medium
        text-accent-red
        transition-all
        duration-180
        hover:border-accent-red/40
        hover:bg-accent-red/15
        focus:outline-none
        focus:ring-2
        focus:ring-accent-red/20
        disabled:cursor-not-allowed
        disabled:opacity-50
        ${className}
      `}
    >
      {Icon && <Icon className="h-4 w-4" />}
      {children}
    </button>
  );
};


const SettingSection = ({
  icon,
  title,
  description,
  children,
}) => {
  return (
    <section className="rounded-xl border border-border bg-panel p-5">
      <div className="flex items-start gap-4">
        {icon}

        <div className="min-w-0 flex-1">
          <h3 className="text-base font-semibold text-text-primary">
            {title}
          </h3>

          <p className="mt-1 text-sm leading-6 text-text-secondary">
            {description}
          </p>
        </div>
      </div>

      <div className="mt-5 border-t border-border/60 pt-5">
        {children}
      </div>
    </section>
  );
};

const Settings = () => {
  // ============================================================
  // GOOGLE CALENDAR COLOR
  // ============================================================

  const [palette, setPalette] = useState([]);
  const [customColors, setCustomColors] = useState({});
  const [lessonColors, setLessonColors] = useState({});
  const [colorsSaving, setColorsSaving] = useState(false);
  const [colorsError, setColorsError] = useState(null);
  const [colorsSuccess, setColorsSuccess] = useState(false);
  const [expandedColorType, setExpandedColorType] = useState(null);

  // ============================================================
  // GOOGLE
  // ============================================================

  const [googleConnected, setGoogleConnected] = useState(() => {
    try {
      const val = localStorage.getItem("googleConnected");
      return val !== null ? JSON.parse(val) : false;
    } catch {
      return false;
    }
  });

  // ============================================================
  // GOOGLE CALENDAR SELECTION
  // ============================================================

  const [calendars, setCalendars] = useState([]);
  const [selectedCalendar, setSelectedCalendar] = useState(null); // Default to null (no selection)
  const [calendarLoading, setCalendarLoading] = useState(false);
  const [calendarError, setCalendarError] = useState(null);
  const [calendarSuccess, setCalendarSuccess] = useState(false);

  // ============================================================
  // OBSIDIAN
  // ============================================================

  const [obsidianPath, setObsidianPath] = useState("");

  // ============================================================
  // GENERAL
  // ============================================================

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // ============================================================
  // GROUP (УЧЕБНАЯ ГРУППА)
  // ============================================================

  const [currentGroup, setCurrentGroup] = useState(null);
  const [groups, setGroups] = useState([]);
  const [groupSearch, setGroupSearch] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");
  const [groupsLoading, setGroupsLoading] = useState(true);
  const [groupsError, setGroupsError] = useState(null);
  const [groupSaving, setGroupSaving] = useState(false);
  const [groupSaveError, setGroupSaveError] = useState(null);
  const [groupSaveSuccess, setGroupSaveSuccess] = useState(false);

  // ============================================================
  // TELEGRAM
  // ============================================================

  const [telegramLinked, setTelegramLinked] = useState(false);
  const [telegramId, setTelegramId] = useState(null);
  const [telegramLinkedAt, setTelegramLinkedAt] = useState(null);

  const [telegramCode, setTelegramCode] = useState("");
  const [telegramCodeExpiresAt, setTelegramCodeExpiresAt] = useState(null);

  const [telegramLoading, setTelegramLoading] = useState(false);
  const [telegramError, setTelegramError] = useState(null);
  const [telegramMessage, setTelegramMessage] = useState(null);

  // ============================================================
  // GOOGLE COLOR
  // ============================================================

  useEffect(() => {
    if (!googleConnected) {
      setLessonColors({});
      setPalette([]);
      setCustomColors({});
      return;
    }

    Promise.all([
      fetch("/api/google/colors", { credentials: "include" }).then(r => r.json()),
      fetch("/api/google/colors/palette", { credentials: "include" }).then(r => r.json()),
    ])
      .then(([colorsData, paletteData]) => {
        setLessonColors(colorsData.colors || {});
        setPalette(paletteData.palette || []);
        setCustomColors(paletteData.custom_colors || {});
      })
      .catch(() => { });
  }, [googleConnected]);



  // ============================================================
  // GOOGLE STATUS
  // ============================================================

  useEffect(() => {
    const checkStatus = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/google/status", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        setGoogleConnected(data.connected || false);

        localStorage.setItem(
          "googleConnected",
          JSON.stringify(data.connected || false)
        );
      } catch (err) {
        console.error("Failed to check Google status:", err);
        setError("Не удалось проверить статус подключения к Google");
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
  }, []);

  // ============================================================
  // GOOGLE CALENDARS FETCH
  // ============================================================

  useEffect(() => {
    const fetchCalendars = async () => {
      if (!googleConnected) {
        // If Google is not connected, reset to default
        setCalendars([{ id: "primary", summary: "Основной календарь" }]);
        setSelectedCalendar(null);
        return;
      }

      setCalendarLoading(true);
      setCalendarError(null);
      setCalendarSuccess(false);

      try {
        const response = await fetch("/api/google/calendars", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        setCalendars(data.calendars || [{ id: "primary", summary: "Основной календарь" }]);

        if (data.selected_calendar_id) {
          setSelectedCalendar(data.selected_calendar_id);
        }
        // If we don't have a selected calendar yet, keep it as null (no selection)
        // User must explicitly select a calendar
      } catch (err) {
        console.error("Failed to fetch Google calendars:", err);
        setCalendarError("Не удалось загрузить список календарей");
        // Fallback to primary calendar
        setCalendars([{ id: "primary", summary: "Основной календарь" }]);
        setSelectedCalendar(null);
      } finally {
        setCalendarLoading(false);
      }
    };

    // Fetch calendars when googleConnected changes
    fetchCalendars();
  }, [googleConnected]);

  // ============================================================
  // OBSIDIAN PATH
  // ============================================================

  useEffect(() => {
    const loadObsidianPath = async () => {
      try {
        const response = await fetch("/api/obsidian/path", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const path = data.path || "";

        setObsidianPath(path);

        if (path) {
          localStorage.setItem("obsidianPath", path);
        }
      } catch (err) {
        console.error("Failed to load Obsidian path:", err);

        try {
          const val = localStorage.getItem("obsidianPath");

          if (val !== null) {
            setObsidianPath(val);
          }
        } catch (e) {
          console.error(
            "Failed to read Obsidian path from localStorage:",
            e
          );
        }
      }
    };

    loadObsidianPath();
  }, []);

  // ============================================================
  // TELEGRAM STATUS
  // ============================================================

  useEffect(() => {
    const loadTelegramStatus = async () => {
      setTelegramLoading(true);
      setTelegramError(null);

      try {
        const response = await fetch("/api/telegram/status", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        setTelegramLinked(Boolean(data.linked));
        setTelegramId(data.telegram_id ?? null);
        setTelegramLinkedAt(data.linked_at ?? null);
      } catch (err) {
        console.error("Failed to load Telegram status:", err);
        setTelegramError(
          "Не удалось проверить статус подключения Telegram"
        );
      } finally {
        setTelegramLoading(false);
      }
    };

    loadTelegramStatus();
  }, []);

  // ============================================================
  // CURRENT GROUP (через /api/mais/current-group)
  // ============================================================

  useEffect(() => {
    const loadCurrentGroup = async () => {
      try {
        const response = await fetch("/api/mais/current-group", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Бэк отдаёт имя группы прямо в поле "group"
        setCurrentGroup(data.group ?? null);
      } catch (err) {
        console.error("Failed to load current MAIS group:", err);
      }
    };

    loadCurrentGroup();
  }, []);

  // ============================================================
  // GROUPS LIST
  // ============================================================

  useEffect(() => {
    const fetchGroups = async () => {
      setGroupsLoading(true);
      setGroupsError(null);

      try {
        const response = await fetch("/api/mais/groups", {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setGroups(Array.isArray(data.groups) ? data.groups : []);
      } catch (err) {
        console.error("Failed to fetch groups:", err);
        setGroupsError("Не удалось загрузить список групп.");
      } finally {
        setGroupsLoading(false);
      }
    };

    fetchGroups();
  }, []);
  // Когда узнали текущую группу — предзаполняем selectedGroup
  useEffect(() => {
    if (currentGroup) {
      setSelectedGroup(currentGroup);
    }
  }, [currentGroup]);

  // ============================================================
  // GOOGLE CONNECT
  // ============================================================

  const handleGoogleConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      window.location.href = "/api/google/auth";
    } catch (err) {
      console.error("Failed to initiate Google connection:", err);
      setError("Не удалось инициализировать подключение к Google");
      setLoading(false);
    }
  };

  // ============================================================
  // GOOGLE DISCONNECT
  // ============================================================

  const handleGoogleDisconnect = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/google/disconnect", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setGoogleConnected(false);

        localStorage.setItem(
          "googleConnected",
          JSON.stringify(false)
        );
      } else {
        throw new Error(data.message || "Unknown error");
      }
    } catch (err) {
      console.error("Failed to disconnect Google:", err);
      setError("Не удалось отключить аккаунт Google");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // GOOGLE CALENDAR SELECT
  // ============================================================

  const handleCalendarSelect = (calendarId) => {
    setSelectedCalendar(calendarId);
    setCalendarSuccess(false);
  };

  const handleCalendarSave = async () => {
    setCalendarLoading(true);
    setCalendarError(null);
    setCalendarSuccess(false);

    try {
      const response = await fetch("/api/google/calendar/select", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          calendar_id: selectedCalendar,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.status === "success") {
        setCalendarSuccess(true);
        if (data.warning) {
          setCalendarError(data.warning);  // покажем как предупреждение
        }
      } else {
        throw new Error(data.message || "Не удалось сохранить выбор календаря");
      }
    } catch (err) {
      console.error("Failed to save Google calendar selection:", err);
      setCalendarError(err.message || "Не удалось сохранить выбор календаря");
    } finally {
      setCalendarLoading(false);
    }
  };

  // ============================================================
  // GOOGLE CALENDAR COLORS
  // ============================================================

  const handleColorsSave = async () => {
    setColorsSaving(true);
    setColorsError(null);
    setColorsSuccess(false);

    try {
      const [r1, r2] = await Promise.all([
        fetch("/api/google/colors", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ colors: lessonColors }),
        }),
        fetch("/api/google/colors/custom", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ custom_colors: customColors }),
        }),
      ]);

      if (!r1.ok || !r2.ok) {
        throw new Error(`HTTP ${r1.status} / ${r2.status}`);
      }

      setColorsSuccess(true);
    } catch (err) {
      console.error("Failed to save colors:", err);
      setColorsError(err.message || "Не удалось сохранить цвета");
    } finally {
      setColorsSaving(false);
    }
  };

  // ============================================================
  // TELEGRAM GENERATE LINK CODE
  // ============================================================

  const handleTelegramLink = async () => {
    setTelegramLoading(true);
    setTelegramError(null);
    setTelegramMessage(null);

    try {
      const response = await fetch("/api/telegram/link", {
        method: "POST",
        credentials: "include",
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail || `HTTP error! status: ${response.status}`
        );
      }

      setTelegramCode(data.code || "");
      setTelegramCodeExpiresAt(data.expires_at || null);
      setTelegramMessage(
        "Код создан. Отправьте его нашему Telegram-боту."
      );
    } catch (err) {
      console.error("Failed to generate Telegram link code:", err);

      setTelegramError(
        err.message || "Не удалось создать код привязки Telegram"
      );
    } finally {
      setTelegramLoading(false);
    }
  };

  // ============================================================
  // TELEGRAM STATUS REFRESH
  // ============================================================

  const handleTelegramRefresh = async () => {
    setTelegramLoading(true);
    setTelegramError(null);

    try {
      const response = await fetch("/api/telegram/status", {
        credentials: "include",
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail || `HTTP error! status: ${response.status}`
        );
      }

      setTelegramLinked(Boolean(data.linked));
      setTelegramId(data.telegram_id ?? null);
      setTelegramLinkedAt(data.linked_at ?? null);

      if (data.linked) {
        setTelegramCode("");
        setTelegramCodeExpiresAt(null);

        setTelegramMessage(
          "Telegram успешно подключён."
        );
      }
    } catch (err) {
      console.error("Failed to refresh Telegram status:", err);

      setTelegramError(
        "Не удалось обновить статус Telegram"
      );
    } finally {
      setTelegramLoading(false);
    }
  };

  // ============================================================
  // TELEGRAM UNLINK
  // ============================================================

  const handleTelegramUnlink = async () => {
    setTelegramLoading(true);
    setTelegramError(null);
    setTelegramMessage(null);

    try {
      const response = await fetch("/api/telegram/unlink", {
        method: "POST",
        credentials: "include",
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail || `HTTP error! status: ${response.status}`
        );
      }

      if (!data.success) {
        throw new Error(
          data.message || "Не удалось отвязать Telegram"
        );
      }

      setTelegramLinked(false);
      setTelegramId(null);
      setTelegramLinkedAt(null);
      setTelegramCode("");
      setTelegramCodeExpiresAt(null);

      setTelegramMessage(
        "Telegram успешно отвязан."
      );
    } catch (err) {
      console.error("Failed to unlink Telegram:", err);

      setTelegramError(
        err.message || "Не удалось отвязать Telegram"
      );
    } finally {
      setTelegramLoading(false);
    }
  };

  // ============================================================
  // COPY TELEGRAM CODE
  // ============================================================

  const handleCopyTelegramCode = async () => {
    if (!telegramCode) {
      return;
    }

    try {
      await navigator.clipboard.writeText(telegramCode);
      setTelegramMessage("Код скопирован в буфер обмена.");
    } catch (err) {
      console.error("Failed to copy Telegram code:", err);

      setTelegramMessage(
        "Не удалось автоматически скопировать код."
      );
    }
  };

  // ============================================================
  // OBSIDIAN SAVE
  // ============================================================

  const handleObsidianSave = async (e) => {
    e.preventDefault();

    const path = e.target.elements.obsidianPath.value.trim();

    if (!path) {
      alert("Пожалуйста, укажите путь к папке Обсидиан");
      return;
    }

    try {
      const response = await fetch("/api/obsidian/path", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          vault: path,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      setObsidianPath(data.path);

      localStorage.setItem(
        "obsidianPath",
        data.path
      );

      alert(`Obsidian path saved: ${data.path}`);
    } catch (err) {
      console.error("Failed to save Obsidian path:", err);

      alert(
        "Не удалось сохранить путь к Обсидиан. Пожалуйста, попробуйте снова."
      );
    }
  };

  // ============================================================
  // GROUPS FILTER
  // ============================================================

  const filteredGroups = useMemo(() => {
    const term = groupSearch.trim().toLowerCase();

    if (!term) {
      return groups;
    }

    return groups.filter((group) => {
      const name = String(group.name || "").toLowerCase();
      const fac = String(group.fac || "").toLowerCase();
      const level = String(group.level || "").toLowerCase();
      const course = String(group.course || "").toLowerCase();

      return (
        name.includes(term) ||
        fac.includes(term) ||
        level.includes(term) ||
        course.includes(term)
      );
    });
  }, [groups, groupSearch]);

  // ============================================================
  // GROUP SAVE
  // ============================================================

  const handleGroupSave = async () => {
    if (!selectedGroup) {
      setGroupSaveError("Выберите группу.");
      return;
    }

    if (selectedGroup === currentGroup) {
      setGroupSaveError("Это уже ваша текущая группа.");
      return;
    }

    setGroupSaving(true);
    setGroupSaveError(null);
    setGroupSaveSuccess(false);

    try {
      const groupResponse = await fetch("/api/mais/group", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          group_name: selectedGroup,
        }),
      });

      if (!groupResponse.ok) {
        const data = await groupResponse.json().catch(() => null);

        throw new Error(
          data?.detail ||
          data?.message ||
          "Не удалось сохранить выбранную группу."
        );
      }

      const importResponse = await fetch("/api/mais/import", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          group_name: selectedGroup,
        }),
      });

      if (!importResponse.ok) {
        const data = await importResponse.json().catch(() => null);

        throw new Error(
          data?.detail ||
          data?.message ||
          "Не удалось импортировать расписание."
        );
      }

      // Перезапрашиваем текущую группу с бэкенда
      const statusResponse = await fetch("/api/mais/current-group", {
        credentials: "include",
      });

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setCurrentGroup(statusData.group ?? null);
      }

      setGroupSaveSuccess(true);
    } catch (err) {
      console.error("Failed to save group:", err);
      setGroupSaveError(
        err.message || "Не удалось изменить группу."
      );
    } finally {
      setGroupSaving(false);
    }
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-background p-6 space-y-6">
      <div className="mb-6">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-accent-blue">
            Система
          </p>

          <h2 className="mt-1 text-2xl font-bold tracking-tight text-text-primary">
            Настройки
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-text-secondary">
            Управление интеграциями, календарем и подключёнными сервисами XO_OS.
          </p>
        </div>
      </div>

      {/* ======================================================
          GOOGLE ACCOUNT
      ======================================================= */}
      <SettingSection
        icon={
          <SectionIcon tone="blue">
            <FiShield className="h-5 w-5" />
          </SectionIcon>
        }
        title="Google аккаунт"
        description="Подключите Google аккаунт для синхронизации расписания и работы с Google Calendar."
      >
        {loading ? (
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />

            <span className="text-sm text-text-secondary">
              Проверка подключения...
            </span>
          </div>
        ) : error ? (
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge type="error">
              <FiAlertCircle className="h-4 w-4" />
              {error}
            </StatusBadge>
          </div>
        ) : googleConnected ? (
          <div className="flex flex-wrap items-center justify-between gap-4">
            <StatusBadge type="success">
              <FiCheckCircle className="h-4 w-4" />
              Google подключён
            </StatusBadge>

            <DangerButton
              onClick={handleGoogleDisconnect}
              icon={FiXCircle}
            >
              Отключить Google
            </DangerButton>
          </div>
        ) : (
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <StatusBadge type="neutral">
              <FiXCircle className="h-4 w-4" />
              Не подключён
            </StatusBadge>

            <PrimaryButton
              onClick={handleGoogleConnect}
              disabled={loading}
              icon={FiShield}
            >
              Подключить Google
            </PrimaryButton>
          </div>
        )}
      </SettingSection>

      {/* ======================================================
          GOOGLE CALENDAR COLOR
      ======================================================= */}
      {googleConnected && (
        <SettingSection
          icon={
            <SectionIcon tone="purple">
              <FiCalendar className="h-5 w-5" />
            </SectionIcon>
          }
          title="Цвета событий"
          description="Настройте цвет каждого типа занятия в Google Calendar."
        >
          <div className="space-y-2">
            {[
              { key: "LECTURE", label: "Лекции (ЛК)" },
              { key: "PRACTICE", label: "Практики (ПЗ)" },
              { key: "LAB", label: "Лабораторные (ЛР)" },
              { key: "EXAM", label: "Экзамены (Э)" },
            ].map(({ key, label }) => {
              const isOpen = expandedColorType === key;
              const selectedColorId = lessonColors[key];
              const selectedColor = selectedColorId?.startsWith("xo_os_")
                ? palette.find((c) => `xo_os_${c.key}` === selectedColorId)
                : null;

              const selectedCustom = selectedColorId?.startsWith("custom_")
                ? customColors[selectedColorId]
                : null;

              return (
                <div
                  key={key}
                  className="overflow-hidden rounded-lg border border-border bg-background"
                >
                  {/* Заголовок строки — кликабельный */}
                  <button
                    type="button"
                    onClick={() => setExpandedColorType(isOpen ? null : key)}
                    className="
                      flex w-full items-center justify-between gap-3
                      px-4 py-3
                      text-left
                      transition-colors duration-150
                      hover:bg-accent-blue/5
                      focus:outline-none
                    "
                  >
                    <span className="text-sm font-medium text-text-primary">
                      {label}
                    </span>

                    <div className="flex items-center gap-3">
                      {/* Выбранный цвет как кружок */}
                      {(selectedColor || selectedCustom) ? (
                        <div
                          className="h-5 w-5 rounded-full border border-white/20"
                          style={{
                            backgroundColor: (selectedColor || selectedCustom).hex,
                            boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.18)",
                          }}
                          title={selectedColor ? selectedColor.name : (selectedCustom.name || "Свой цвет")}
                        />
                      ) : (
                        <div className="h-5 w-5 rounded-full border border-dashed border-border" />
                      )}

                      {/* Стрелка, крутится при раскрытии */}
                      <FiChevronDown
                        className={`
                          h-4 w-4 text-text-muted
                          transition-transform duration-200
                          ${isOpen ? "rotate-180" : ""}
                        `}
                      />
                    </div>
                  </button>

                  {/* Раскрывающийся блок с кружками */}
                  <div
                    className={`
                      grid transition-[grid-template-rows,opacity] duration-300 ease-out
                      ${isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}
                    `}
                  >
                    <div className="overflow-hidden">
                      <div className="border-t border-border/40 px-4 py-4">

                        <div className="grid grid-cols-6 gap-2">
                          {/* 24 палитровых */}
                          {palette.map((color) => {
                            const value = `xo_os_${color.key}`;
                            const selected = selectedColorId === value;
                            return (
                              <button
                                key={color.key}
                                type="button"
                                title={color.name}
                                onClick={() => setLessonColors({ ...lessonColors, [key]: value })}
                                className={`
                                  h-8 w-8 rounded-full border-2
                                  transition-all duration-150
                                  hover:scale-110
                                  hover:shadow-[0_0_14px_rgba(255,255,255,0.85)]
                                  focus:outline-none
                                  ${selected ? "border-white ring-2 ring-white/40" : "border-transparent"}
                                `}
                                style={{
                                  backgroundColor: color.hex,
                                  boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.18)",
                                }}
                              />
                            );
                          })}

                          {/* 6 кастомных слотов */}
                          {CUSTOM_SLOT_KEYS.map((slot) => {
                            const custom = customColors[slot];
                            const selected = selectedColorId === slot;

                            // Пустой слот: клик открывает пикер, после выбора цвет сразу назначается типу
                            if (!custom) {
                              return (
                                <label
                                  key={slot}
                                  title="Добавить свой цвет"
                                  className="relative flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border-2 border-dashed border-text-muted hover:scale-110 transition-all duration-150"
                                >
                                  <FiDroplet className="h-3.5 w-3.5 text-text-muted" />
                                  <input
                                    type="color"
                                    defaultValue="#888888"
                                    className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
                                    onChange={(e) => {
                                      const hex = e.target.value;
                                      setCustomColors({ ...customColors, [slot]: { hex, name: "" } });
                                    }}
                                  />
                                </label>
                              );
                            }

                            // Заполненный слот: большой круг — назначить, маленькая капля — редактировать HEX
                            return (
                              <div key={slot} className="relative h-8 w-8">
                                <button
                                  type="button"
                                  title={custom.name || "Свой цвет"}
                                  onClick={() => setLessonColors({ ...lessonColors, [key]: slot })}
                                  className={`
                                h-8 w-8 rounded-full border-2
                                transition-all duration-150
                                hover:scale-110
                                hover:shadow-[0_0_14px_rgba(255,255,255,0.85)]
                                focus:outline-none
                                ${selected ? "border-white ring-2 ring-white/40" : "border-transparent"}
                              `}
                                  style={{
                                    backgroundColor: custom.hex,
                                    boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.18)",
                                  }}
                                />

                                <label
                                  title="Изменить цвет"
                                  className="
                                absolute -right-0.5 -bottom-0.5
                                flex h-3.5 w-3.5 cursor-pointer items-center justify-center
                                rounded-full border border-border bg-background
                                opacity-0 transition-opacity
                                hover:opacity-100
                              "
                                >
                                  <FiDroplet className="h-2 w-2 text-text-muted" />
                                  <input
                                    type="color"
                                    value={custom.hex}
                                    className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
                                    onChange={(e) =>
                                      setCustomColors({
                                        ...customColors,
                                        [slot]: { ...custom, hex: e.target.value },
                                      })
                                    }
                                  />
                                </label>
                              </div>
                            );
                          })}
                        </div>

                        {/* Кнопка сброса */}
                        <div className="mt-3 flex justify-end">
                          <button
                            type="button"
                            onClick={() =>
                              setLessonColors({ ...lessonColors, [key]: null })
                            }
                            className="
                            rounded-md px-3 py-1 text-[11px] font-medium
                            text-text-muted
                            transition-colors duration-150
                            hover:bg-background hover:text-text-primary
                          "
                          >
                            По умолчанию
                          </button>
                        </div>


                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              {colorsSuccess && (
                <StatusBadge type="success">
                  <FiCheckCircle className="h-4 w-4" />
                  Цвета сохранены
                </StatusBadge>
              )}
              {colorsError && (
                <StatusBadge type="error">
                  <FiAlertCircle className="h-4 w-4" />
                  {colorsError}
                </StatusBadge>
              )}
            </div>

            <PrimaryButton
              onClick={handleColorsSave}
              disabled={colorsSaving}
              icon={FiSave}
            >
              {colorsSaving ? "Сохранение..." : "Сохранить"}
            </PrimaryButton>
          </div>
        </SettingSection>
      )}

      {/* ======================================================
          GOOGLE CALENDAR SELECTION
      ======================================================= */}
      {googleConnected && (
        <SettingSection
          icon={
            <SectionIcon tone="blue">
              <FiCalendar className="h-5 w-5" />
            </SectionIcon>
          }
          title="Календарь Google"
          description="Выберите календарь, в который XO_OS будет синхронизировать расписание МАИ."
        >
          {calendarLoading ? (
            <div className="flex items-center gap-3">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />

              <span className="text-sm text-text-secondary">
                Загрузка календарей...
              </span>
            </div>
          ) : calendarError ? (
            <div className="flex flex-col gap-3">
              <StatusBadge type="error">
                <FiAlertCircle className="h-4 w-4" />
                {calendarError}
              </StatusBadge>

              <SecondaryButton
                onClick={() => {
                  setCalendarLoading(true);
                  setCalendarError(null);
                }}
                icon={FiRefreshCw}
              >
                Повторить
              </SecondaryButton>
            </div>
          ) : (
            <div className="space-y-4">
              {calendarSuccess && (
                <StatusBadge type="success">
                  <FiCheckCircle className="h-4 w-4" />
                  Выбор календаря сохранён
                </StatusBadge>
              )}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-text-muted">
                  Доступные календари
                </label>

                <div className="overflow-hidden rounded-lg border border-border">
                  {calendars.length === 0 ? (
                    <div className="px-4 py-6 text-center text-sm text-text-secondary">
                      Календари не найдены
                    </div>
                  ) : (
                    <div className="divide-y divide-border/60">
                      <button
                        type="button"
                        onClick={() => handleCalendarSelect(null)}
                        className={`
                    flex w-full items-center justify-between gap-4
                    px-4 py-3
                    text-left
                    transition-colors
                    duration-180
                    ${selectedCalendar === null
                            ? "bg-accent-blue/10"
                            : "bg-background hover:bg-accent-blue/5"
                          }
                  `}
                      >
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-text-primary">
                            Не выбран
                          </p>

                          <p className="mt-0.5 text-xs text-text-muted">
                            Синхронизация отключена
                          </p>
                        </div>

                        {selectedCalendar === null && (
                          <StatusBadge type="blue">
                            <FiCheckCircle className="h-3.5 w-3.5" />
                            Выбрано
                          </StatusBadge>
                        )}
                      </button>

                      {calendars.map((calendar) => {
                        const selected =
                          selectedCalendar === calendar.id;

                        return (
                          <button
                            key={calendar.id}
                            type="button"
                            onClick={() =>
                              handleCalendarSelect(calendar.id)
                            }
                            className={`
                        flex w-full items-center justify-between gap-4
                        px-4 py-3
                        text-left
                        transition-colors
                        duration-180
                        ${selected
                                ? "bg-accent-blue/10"
                                : "bg-background hover:bg-accent-blue/5"
                              }
                      `}
                          >
                            <div className="min-w-0">
                              <p className="truncate text-sm font-medium text-text-primary">
                                {calendar.summary}
                              </p>

                              {calendar.id !== "primary" && (
                                <p className="mt-0.5 truncate font-mono text-[11px] text-text-muted">
                                  {calendar.id}
                                </p>
                              )}
                            </div>

                            {selected && (
                              <StatusBadge type="blue">
                                <FiCheckCircle className="h-3.5 w-3.5" />
                                Выбрано
                              </StatusBadge>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end">
                <PrimaryButton
                  onClick={handleCalendarSave}
                  disabled={calendarLoading || selectedCalendar === null}
                  icon={FiSave}
                >
                  Сохранить выбор
                </PrimaryButton>
              </div>
            </div>
          )}
        </SettingSection>
      )}

      {/* ======================================================
          УЧЕБНАЯ ГРУППА
      ======================================================= */}
      <SettingSection
        icon={
          <SectionIcon tone="green">
            <FiUsers className="h-5 w-5" />
          </SectionIcon>
        }
        title="Учебная группа"
        description="Группа используется для импорта расписания из МАИ. При смене группы расписание будет импортировано заново."
      >
        {/* Текущая группа */}
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-background px-4 py-3">
          <div>
            <p className="text-xs uppercase tracking-wider text-text-muted">
              Текущая группа
            </p>

            <p className="mt-1 text-sm font-semibold text-text-primary">
              {currentGroup || "Не задана"}
            </p>
          </div>

          {currentGroup ? (
            <StatusBadge type="success">
              <FiCheckCircle className="h-4 w-4" />
              Активна
            </StatusBadge>
          ) : (
            <StatusBadge type="warning">
              <FiAlertCircle className="h-4 w-4" />
              Не выбрана
            </StatusBadge>
          )}
        </div>

        {/* Поиск */}
        <div className="mb-4">
          <label
            htmlFor="settings-group-search"
            className="mb-2 block text-xs font-medium uppercase tracking-wider text-text-muted"
          >
            Поиск группы
          </label>

          <div className="relative">
            <FiSearch className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />

            <input
              id="settings-group-search"
              type="text"
              value={groupSearch}
              onChange={(e) => setGroupSearch(e.target.value)}
              placeholder="Группа, факультет, курс или уровень"
              className="
                w-full
                rounded-lg
                border
                border-border
                bg-background
                py-3
                pl-10
                pr-4
                text-sm
                text-text-primary
                placeholder:text-text-muted
                transition-all
                duration-180
                focus:border-accent-blue/50
                focus:outline-none
                focus:ring-2
                focus:ring-accent-blue/10
              "
            />
          </div>
        </div>

        {/* Список групп */}
        <div className="overflow-hidden rounded-lg border border-border bg-background">
          <div className="max-h-[320px] overflow-y-auto">
            {groupsLoading ? (
              <div className="flex min-h-[200px] flex-col items-center justify-center">
                <FiLoader className="h-5 w-5 animate-spin text-accent-blue" />

                <p className="mt-3 text-xs text-text-muted">
                  Загружаем список групп...
                </p>
              </div>
            ) : groupsError ? (
              <div className="flex min-h-[200px] flex-col items-center justify-center px-6 text-center">
                <FiAlertCircle className="h-5 w-5 text-accent-red" />

                <p className="mt-3 text-sm text-accent-red">
                  {groupsError}
                </p>
              </div>
            ) : filteredGroups.length === 0 ? (
              <div className="flex min-h-[200px] flex-col items-center justify-center px-6 text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-card text-text-muted">
                  <FiSearch className="h-4 w-4" />
                </div>

                <p className="mt-3 text-sm font-medium text-text-primary">
                  Группы не найдены
                </p>

                <p className="mt-1 max-w-xs text-xs leading-5 text-text-muted">
                  Попробуйте изменить поисковый запрос.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-border/60">
                {filteredGroups.map((group) => {
                  const isSelected = selectedGroup === group.name;
                  const isCurrent = currentGroup === group.name;

                  return (
                    <button
                      key={group.name}
                      type="button"
                      onClick={() => {
                        setSelectedGroup(group.name);
                        setGroupSaveError(null);
                        setGroupSaveSuccess(false);
                      }}
                      className={`
                        group w-full px-4 py-3 text-left transition-colors
                        ${isSelected ? "bg-accent-blue/10" : "hover:bg-card/70"}
                      `}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`
                            flex h-9 w-9 shrink-0 items-center justify-center
                            rounded-lg border
                            ${isSelected
                              ? "border-accent-blue/30 bg-accent-blue/10 text-accent-blue"
                              : "border-border bg-background text-text-muted"
                            }
                          `}
                        >
                          {isSelected ? (
                            <FiCheck className="h-4 w-4" />
                          ) : (
                            <FiUsers className="h-4 w-4" />
                          )}
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="truncate text-sm font-semibold text-text-primary">
                              {group.name}
                            </p>

                            {isCurrent && (
                              <span className="rounded-full border border-accent-green/20 bg-accent-green/5 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-accent-green">
                                текущая
                              </span>
                            )}

                            {isSelected && !isCurrent && (
                              <span className="rounded-full border border-accent-blue/20 bg-accent-blue/5 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-accent-blue">
                                выбрано
                              </span>
                            )}
                          </div>

                          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-text-muted">
                            {group.fac && <span>{group.fac}</span>}
                            {group.level && <span>{group.level}</span>}
                            {group.course && <span>{group.course} курс</span>}
                          </div>
                        </div>

                        <FiChevronRight
                          className={`
                            h-4 w-4 shrink-0 transition-transform
                            ${isSelected
                              ? "translate-x-0.5 text-accent-blue"
                              : "text-text-muted group-hover:translate-x-0.5"
                            }
                          `}
                        />
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Ошибки / успех / кнопка */}
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-col gap-2">
            {groupSaveSuccess && (
              <StatusBadge type="success">
                <FiCheckCircle className="h-4 w-4" />
                Группа обновлена, расписание импортировано
              </StatusBadge>
            )}

            {groupSaveError && (
              <StatusBadge type="error">
                <FiAlertCircle className="h-4 w-4" />
                {groupSaveError}
              </StatusBadge>
            )}
          </div>

          <PrimaryButton
            onClick={handleGroupSave}
            disabled={
              groupSaving ||
              !selectedGroup ||
              selectedGroup === currentGroup
            }
            icon={groupSaving ? FiLoader : FiArrowRight}
          >
            {groupSaving ? "Сохраняем..." : "Сменить группу"}
          </PrimaryButton>
        </div>
      </SettingSection>

      {/* ======================================================
          TELEGRAM
      ======================================================= */}
      <SettingSection
        icon={
          <SectionIcon tone="blue">
            <FiSend className="h-5 w-5" />
          </SectionIcon>
        }
        title="Telegram"
        description="Используйте Telegram-бота XO_OS как дополнительный интерфейс для импорта расписания и быстрых действий."
      >
        {telegramLoading ? (
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />

            <span className="text-sm text-text-secondary">
              Проверка подключения...
            </span>
          </div>
        ) : telegramError ? (
          <div className="flex flex-col gap-3">
            <StatusBadge type="error">
              <FiAlertCircle className="h-4 w-4" />
              {telegramError}
            </StatusBadge>

            <div>
              <SecondaryButton
                onClick={handleTelegramRefresh}
                icon={FiRefreshCw}
              >
                Обновить статус
              </SecondaryButton>
            </div>
          </div>
        ) : telegramLinked ? (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <StatusBadge type="success">
                <FiCheckCircle className="h-4 w-4" />
                Telegram подключён
              </StatusBadge>

              <div className="flex flex-wrap gap-2">
                <SecondaryButton
                  onClick={handleTelegramRefresh}
                  icon={FiRefreshCw}
                >
                  Обновить
                </SecondaryButton>

                <DangerButton
                  onClick={handleTelegramUnlink}
                  icon={FiXCircle}
                >
                  Отвязать
                </DangerButton>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs uppercase tracking-wider text-text-muted">
                  Telegram ID
                </p>

                <p className="mt-2 font-mono text-sm text-text-primary">
                  {telegramId}
                </p>
              </div>

              <div className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs uppercase tracking-wider text-text-muted">
                  Подключён
                </p>

                <p className="mt-2 text-sm text-text-primary">
                  {telegramLinkedAt
                    ? new Date(
                      telegramLinkedAt
                    ).toLocaleString("ru-RU")
                    : "—"}
                </p>
              </div>
            </div>

            {telegramMessage && (
              <StatusBadge type="success">
                <FiCheckCircle className="h-4 w-4" />
                {telegramMessage}
              </StatusBadge>
            )}
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <StatusBadge type="neutral">
                <FiXCircle className="h-4 w-4" />
                Telegram не подключён
              </StatusBadge>

              <PrimaryButton
                onClick={handleTelegramLink}
                disabled={telegramLoading}
                icon={FiSend}
              >
                Получить код привязки
              </PrimaryButton>
            </div>

            {telegramCode && (
              <div className="rounded-xl border border-accent-blue/20 bg-accent-blue/5 p-5">
                <div className="flex flex-col gap-4">
                  <div>
                    <p className="text-sm font-semibold text-text-primary">
                      Код привязки
                    </p>

                    <p className="mt-1 text-xs leading-5 text-text-secondary">
                      Код одноразовый. Используйте кнопку ниже,
                      чтобы открыть Telegram и автоматически передать код боту.
                    </p>
                  </div>

                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                    <code className="flex-1 rounded-lg border border-border bg-background px-4 py-3 font-mono text-lg tracking-[0.18em] text-accent-blue">
                      {telegramCode}
                    </code>

                    <SecondaryButton
                      onClick={handleCopyTelegramCode}
                      icon={FiCopy}
                    >
                      Копировать
                    </SecondaryButton>
                  </div>

                  {telegramCodeExpiresAt && (
                    <div className="flex items-center gap-2 text-xs text-text-muted">
                      <FiAlertCircle className="h-4 w-4" />

                      <span>
                        Действует до{" "}
                        {new Date(
                          telegramCodeExpiresAt
                        ).toLocaleTimeString("ru-RU")}
                      </span>
                    </div>
                  )}

                  <div className="flex flex-col gap-2 sm:flex-row">
                    <a
                      href={`https://t.me/XO_OS_bot?start=${telegramCode}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="
                  inline-flex
                  items-center
                  justify-center
                  gap-2
                  rounded-lg
                  border
                  border-accent-blue
                  bg-accent-blue
                  px-4
                  py-2.5
                  text-sm
                  font-semibold
                  text-white
                  transition-all
                  duration-180
                  hover:bg-accent-blue/90
                  hover:shadow-[0_0_20px_rgba(22,131,255,0.18)]
                "
                    >
                      <FiExternalLink className="h-4 w-4" />
                      Открыть Telegram
                    </a>

                    <SecondaryButton
                      onClick={handleTelegramRefresh}
                      icon={FiRefreshCw}
                    >
                      Проверить подключение
                    </SecondaryButton>
                  </div>
                </div>
              </div>
            )}

            {telegramMessage && (
              <StatusBadge type="success">
                <FiCheckCircle className="h-4 w-4" />
                {telegramMessage}
              </StatusBadge>
            )}
          </div>
        )}
      </SettingSection>

      {/* ======================================================
          OBSIDIAN INTEGRATION
      ======================================================= */}
      <SettingSection
        icon={
          <SectionIcon tone="purple">
            <FiBookOpen className="h-5 w-5" />
          </SectionIcon>
        }
        title="Obsidian"
        description="Укажите локальный путь к vault для экспорта расписания и связанных материалов."
      >
        <form
          onSubmit={handleObsidianSave}
          className="space-y-4"
        >
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-text-muted">
              Путь к vault
            </label>

            <input
              type="text"
              name="obsidianPath"
              defaultValue={obsidianPath}
              placeholder="/Users/yourname/Vaults/MyKnowledge"
              className="
          w-full
          rounded-lg
          border
          border-border
          bg-background
          px-4
          py-3
          text-sm
          text-text-primary
          placeholder:text-text-muted
          transition-all
          duration-180
          focus:border-accent-blue/50
          focus:outline-none
          focus:ring-2
          focus:ring-accent-blue/10
        "
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              {obsidianPath ? (
                <StatusBadge type="success">
                  <FiCheckCircle className="h-4 w-4" />
                  Путь сохранён
                </StatusBadge>
              ) : (
                <span className="text-xs text-text-muted">
                  Путь ещё не настроен
                </span>
              )}
            </div>

            <PrimaryButton
              type="submit"
              icon={FiSave}
            >
              Сохранить путь
            </PrimaryButton>
          </div>
        </form>

        {obsidianPath && (
          <div className="mt-4 rounded-lg border border-border bg-background px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-text-muted">
              Текущий путь
            </p>

            <p className="mt-1 break-all font-mono text-xs text-text-secondary">
              {obsidianPath}
            </p>
          </div>
        )}
      </SettingSection>

      {/* ======================================================
          OTHER SETTINGS
      ======================================================= */}
      <SettingSection
        icon={
          <SectionIcon tone="yellow">
            <FiSettingsIcon className="h-5 w-5" />
          </SectionIcon>
        }
        title="Другие настройки"
        description="Дополнительные параметры XO_OS, которые будут доступны по мере развития системы."
      >
        <div className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
          <div>
            <p className="text-sm font-medium text-text-primary">
              Дополнительные модули
            </p>

            <p className="mt-1 text-xs text-text-muted">
              Раздел подготовлен для будущих настроек.
            </p>
          </div>

          <FiChevronRight className="h-5 w-5 text-text-muted" />
        </div>
      </SettingSection>
    </div>
  );
};

export default Settings;