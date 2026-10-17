import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  FiCalendar,
  FiCheck,
  FiCheckCircle,
  FiChevronDown,
  FiFilter,
  FiRefreshCw,
  FiSearch,
  FiX,
} from "react-icons/fi";
import { useLocation } from "react-router-dom";

const FILTER_EVENT_NAME = "xo-os:schedule-filters-changed";

const DEFAULT_CATEGORIES = [
  { key: "REGULAR", label: "Обычные занятия" },
  { key: "ELECTIVE", label: "Элективы" },
  { key: "MILITARY", label: "Военная подготовка" },
];

const ITEM_HEIGHT_PX = 100;
const VISIBLE_ITEMS_BEFORE_SCROLL = 6;

export default function ScheduleList({ mode = "today" }) {
  const instanceIdRef = useRef(
    `schedule-${Math.random().toString(36).slice(2)}`
  );

  const [schedule, setSchedule] = useState([]);
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  const [subjects, setSubjects] = useState([]);

  const [excludedSubjects, setExcludedSubjects] = useState(new Set());

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [savingFilters, setSavingFilters] = useState(false);

  const [error, setError] = useState(null);
  const [filtersError, setFiltersError] = useState(null);

  const [showFilterMenu, setShowFilterMenu] = useState(false);
  const [subjectSearch, setSubjectSearch] = useState("");

  const location = useLocation();
  const [highlightId, setHighlightId] = useState(null);

  const loadSchedule = useCallback(
    async (showLoader = false) => {
      if (showLoader) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      try {
        const response = await fetch(`/api/schedule?mode=${mode}`, {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        setSchedule(Array.isArray(data) ? data : []);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch schedule:", err);
        setError(err.message || "Не удалось загрузить расписание");
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [mode]
  );

  const loadFilters = useCallback(async () => {
    try {
      const response = await fetch("/api/schedule/filters", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const nextCategories =
        Array.isArray(data.categories) && data.categories.length > 0
          ? data.categories
          : DEFAULT_CATEGORIES;

      const nextSubjects = Array.isArray(data.subjects) ? data.subjects : [];

      setCategories(nextCategories);
      setSubjects(nextSubjects);

      setExcludedSubjects(
        new Set(
          Array.isArray(data.excluded_subjects) ? data.excluded_subjects : []
        )
      );

      setFiltersError(null);
    } catch (err) {
      console.error("Failed to fetch schedule filters:", err);
      setFiltersError(err.message || "Не удалось загрузить фильтры");
    }
  }, []);

  useEffect(() => {
    Promise.all([loadSchedule(true), loadFilters()]);
  }, [loadSchedule, loadFilters]);

  useEffect(() => {
    const handleFiltersChanged = (event) => {
      const detail = event?.detail || {};

      if (detail.sourceId === instanceIdRef.current) {
        return;
      }

      if (Array.isArray(detail.excluded_subjects)) {
        setExcludedSubjects(new Set(detail.excluded_subjects));
      }

      loadSchedule(false);
    };

    window.addEventListener(FILTER_EVENT_NAME, handleFiltersChanged);

    return () => {
      window.removeEventListener(FILTER_EVENT_NAME, handleFiltersChanged);
    };
  }, [loadSchedule]);

  // Закрытие попапа фильтров по клику вне и по Escape
  useEffect(() => {
    if (!showFilterMenu) return;

    const handleClickOutside = (event) => {
      const target = event.target;

      if (
        target.closest("[data-filter-trigger]") ||
        target.closest("[data-filter-popover]")
      ) {
        return;
      }

      setShowFilterMenu(false);
    };

    const handleKeyDown = (event) => {
      if (event.key === "Escape") setShowFilterMenu(false);
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [showFilterMenu]);

  const saveFilters = useCallback(
    async (nextSubjects) => {
      setSavingFilters(true);
      setFiltersError(null);

      try {
        const response = await fetch("/api/schedule/filters", {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            excluded_categories: [],
            excluded_subjects: Array.from(nextSubjects),
          }),
        });

        if (!response.ok) {
          let message = `HTTP ${response.status}`;

          try {
            const data = await response.json();

            if (typeof data.detail === "string") {
              message = data.detail;
            }
          } catch {
            // ignore
          }

          throw new Error(message);
        }

        const data = await response.json();

        const savedSubjects = new Set(
          Array.isArray(data.excluded_subjects)
            ? data.excluded_subjects
            : Array.from(nextSubjects)
        );

        setExcludedSubjects(savedSubjects);

        window.dispatchEvent(
          new CustomEvent(FILTER_EVENT_NAME, {
            detail: {
              sourceId: instanceIdRef.current,
              excluded_subjects: Array.from(savedSubjects),
            },
          })
        );

        await loadSchedule(false);
      } catch (err) {
        console.error("Failed to save schedule filters:", err);
        setFiltersError(
          err.message || "Не удалось сохранить фильтры расписания"
        );
      } finally {
        setSavingFilters(false);
      }
    },
    [loadSchedule]
  );

  const toggleSubject = (subjectKey) => {
    if (savingFilters) return;

    const nextSubjects = new Set(excludedSubjects);

    if (nextSubjects.has(subjectKey)) {
      nextSubjects.delete(subjectKey);
    } else {
      nextSubjects.add(subjectKey);
    }

    saveFilters(nextSubjects);
  };

  const resetFilters = () => {
    if (savingFilters) return;
    saveFilters(new Set());
  };

  const normalizedSearch = subjectSearch.trim().toLowerCase();

  const filteredSubjects = useMemo(() => {
    let result = subjects;

    if (normalizedSearch) {
      result = subjects.filter((subject) =>
        String(subject.label || subject.key || "")
          .toLowerCase()
          .includes(normalizedSearch)
      );
    }

    return [...result].sort((a, b) => {
      const aExcluded = excludedSubjects.has(a.key);
      const bExcluded = excludedSubjects.has(b.key);

      if (aExcluded !== bExcluded) {
        return aExcluded ? -1 : 1;
      }

      return String(a.label || a.key || "").localeCompare(
        String(b.label || b.key || ""),
        "ru"
      );
    });
  }, [subjects, normalizedSearch, excludedSubjects]);

  // ============================================================
  // UPCOMING — фильтруем прошедшие занятия (только для mode="all")
  // ============================================================

    const upcomingSchedule = useMemo(() => {
    if (mode !== "all") return schedule;

    const now = new Date();

    const todayStr = [
      now.getFullYear(),
      String(now.getMonth() + 1).padStart(2, "0"),
      String(now.getDate()).padStart(2, "0"),
    ].join("-");

    const nowTime = [
      String(now.getHours()).padStart(2, "0"),
      String(now.getMinutes()).padStart(2, "0"),
    ].join(":");

    return schedule.filter((item) => {
      if (!item.date) return false;
      if (item.date < todayStr) return false;
      if (item.date > todayStr) return true;

      // Сегодня: пара актуальна, если она ещё НЕ ЗАКОНЧИЛАСЬ.
      // Если есть end_time — сравниваем по нему, иначе по времени начала.
      const end = item.end_time || item.time;
      if (!end) return false;

      return String(end) > nowTime;
    });
  }, [schedule, mode]);

  // ============================================================
  // GROUPING (только для mode="all")
  // ============================================================

  const groupedSchedule = useMemo(() => {
    if (mode !== "all") return null;

    const map = new Map();

    for (const item of upcomingSchedule) {
      const key = item.date;
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(item);
    }

    const groups = [...map.entries()].sort(([a], [b]) =>
      a.localeCompare(b)
    );

    for (const [, items] of groups) {
      items.sort((a, b) =>
        String(a.time || "").localeCompare(String(b.time || ""))
      );
    }

    return groups;
  }, [upcomingSchedule, mode]);

  const highlightEventId = location.state?.highlightEventId;

  useEffect(() => {
    if (!highlightEventId) return;
    if (loading) return;

    // Сначала — плавный скролл
    const scrollTimer = setTimeout(() => {
      const el = document.querySelector(
        `[data-event-id="${highlightEventId}"]`
      );

      if (el) {
        el.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }
    }, 80);

    // Подсветку включаем чуть позже, чтобы пользователь
    // успел увидеть, куда его прискроллило
    const highlightTimer = setTimeout(() => {
      setHighlightId(String(highlightEventId));
    }, 700);

    // Держим подсветку ~4 секунды, потом плавно снимаем
    const clearTimer = setTimeout(() => {
      setHighlightId(null);
    }, 5200);

    return () => {
      clearTimeout(scrollTimer);
      clearTimeout(highlightTimer);
      clearTimeout(clearTimer);
    };
  }, [highlightEventId, location.key, loading]);

  const excludedCount = excludedSubjects.size;

  const getTypeDetails = (type) => {
    const normalizedType = type?.trim().toUpperCase() || "";

    switch (normalizedType) {
      case "LECTURE":
        return {
          label: "Лекция",
          badge: "border-accent-blue/30 bg-accent-blue/10 text-accent-blue",
          dot: "bg-accent-blue",
        };

      case "PRACTICE":
        return {
          label: "Практика",
          badge:
            "border-accent-green/30 bg-accent-green/10 text-accent-green",
          dot: "bg-accent-green",
        };

      case "LAB":
        return {
          label: "Лабораторная",
          badge:
            "border-accent-yellow/30 bg-accent-yellow/10 text-accent-yellow",
          dot: "bg-accent-yellow",
        };

      case "EXAM":
        return {
          label: "Экзамен",
          badge: "border-accent-red/30 bg-accent-red/10 text-accent-red",
          dot: "bg-accent-red",
        };

      default:
        return {
          label: "Занятие",
          badge: "border-border bg-background text-text-secondary",
          dot: "bg-text-secondary",
        };
    }
  };

  const getCategoryLabel = (categoryKey) => {
    const category = categories.find((item) => item.key === categoryKey);

    if (category) return category.label;

    switch (categoryKey) {
      case "ELECTIVE":
        return "Электив";
      case "MILITARY":
        return "Военная подготовка";
      case "REGULAR":
        return "Обычные занятия";
      default:
        return categoryKey || "Занятия";
    }
  };

  const headerTitle =
    mode === "all" ? "Расписание" : "Ближайшие занятия";

  const headerSubtitle =
    mode === "all"
      ? "Все занятия из расписания"
      : "Предстоящие события из расписания";

  if (loading) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <ScheduleHeader
          showFilter={false}
          refreshing={false}
          excludedCount={0}
          onFilterClick={() => { }}
          title={headerTitle}
          subtitle={headerSubtitle}
        />

        <div className="flex min-h-[180px] items-center justify-center">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-accent-blue border-t-transparent" />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <ScheduleHeader
          showFilter={false}
          refreshing={refreshing}
          excludedCount={excludedCount}
          onFilterClick={() => setShowFilterMenu((value) => !value)}
          title={headerTitle}
          subtitle={headerSubtitle}
        />

        <div className="flex min-h-[180px] flex-col items-center justify-center text-center">
          <p className="text-sm text-text-secondary">
            Не удалось загрузить расписание
          </p>

          <p className="mt-1 text-xs text-text-muted">{error}</p>

          <button
            type="button"
            onClick={() => loadSchedule(false)}
            className="mt-4 inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-xs font-medium text-text-secondary transition-colors hover:border-accent-blue/40 hover:text-accent-blue"
          >
            <FiRefreshCw className="h-3.5 w-3.5" />
            Повторить
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="relative rounded-xl border border-border bg-panel p-5">
      <div className="mb-4 flex items-start justify-between gap-4">
        <ScheduleHeader
          showFilter={true}
          refreshing={refreshing}
          excludedCount={excludedCount}
          isOpen={showFilterMenu}
          onFilterClick={() => setShowFilterMenu((value) => !value)}
          title={headerTitle}
          subtitle={headerSubtitle}
        />

        <div
          role="dialog"
          data-filter-popover
          aria-hidden={!showFilterMenu}
          className={`
            absolute right-5 top-16 z-50
            w-[min(360px,calc(100vw-2rem))]
            origin-top-right
            overflow-hidden
            rounded-xl
            border border-border
            bg-panel
            shadow-2xl shadow-black/30
            transition-[opacity,transform] duration-200 ease-out
            ${showFilterMenu
              ? "opacity-100 scale-100 translate-y-0 pointer-events-auto"
              : "opacity-0 scale-95 -translate-y-2 pointer-events-none"
            }
          `}
        >
          <div className="flex items-center justify-between border-b border-border/60 px-4 py-3">
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Фильтры расписания
              </h3>

              <p className="mt-0.5 text-[11px] text-text-muted">
                Исключения сохраняются для твоего аккаунта
              </p>
            </div>

            <button
              type="button"
              onClick={() => setShowFilterMenu(false)}
              className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-card hover:text-text-primary"
              aria-label="Закрыть"
            >
              <FiX className="h-4 w-4" />
            </button>
          </div>

          <div className="max-h-[70vh] overflow-y-auto p-4 fcc-scrollbar">
            {filtersError && (
              <div className="mb-4 rounded-lg border border-accent-red/20 bg-accent-red/5 px-3 py-2 text-xs text-accent-red">
                {filtersError}
              </div>
            )}

            <div className="space-y-4">
              {/* Subjects */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-text-primary">
                  Предметы
                </p>

                <p className="mt-0.5 text-[11px] text-text-muted">
                  Например, исключи предмет, который уже закрыл
                </p>
              </div>

              {subjects.length > 0 ? (
                <>
                  <div className="relative">
                    <FiSearch className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />

                    <input
                      type="text"
                      value={subjectSearch}
                      onChange={(event) =>
                        setSubjectSearch(event.target.value)
                      }
                      placeholder="Поиск предмета..."
                      className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-3 text-xs text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-accent-blue/50"
                    />
                  </div>

                  <div className="max-h-64 overflow-y-auto rounded-lg border border-border/60 bg-background/50 p-1 fcc-scrollbar">
                    {filteredSubjects.length > 0 ? (
                      filteredSubjects.map((subject) => {
                        const checked = excludedSubjects.has(subject.key);

                        return (
                          <FilterCheckbox
                            key={subject.key}
                            checked={checked}
                            disabled={savingFilters}
                            label={subject.label || subject.key}
                            onChange={() => toggleSubject(subject.key)}
                            compact
                          />
                        );
                      })
                    ) : (
                      <div className="px-3 py-6 text-center text-xs text-text-muted">
                        Ничего не найдено
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="rounded-lg border border-dashed border-border bg-background/30 px-3 py-4 text-center text-xs text-text-muted">
                  Список предметов пока пуст
                </div>
              )}

              {/* Summary / reset */}
              <div className="border-t border-border/60 pt-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-text-primary">
                      Активные исключения
                    </p>

                    <p className="mt-0.5 truncate text-[11px] text-text-muted">
                      {excludedCount === 0
                        ? "Ничего не скрыто"
                        : `${excludedCount} ${getPluralForm(
                          excludedCount,
                          "фильтр",
                          "фильтра",
                          "фильтров"
                        )}`}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={resetFilters}
                    disabled={savingFilters || excludedCount === 0}
                    className="shrink-0 rounded-lg border border-border px-3 py-2 text-[11px] font-medium text-text-secondary transition-colors hover:border-accent-red/30 hover:bg-accent-red/5 hover:text-accent-red disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Сбросить
                  </button>
                </div>

                {savingFilters && (
                  <div className="mt-3 flex items-center gap-2 text-[11px] text-text-muted">
                    <div className="h-3 w-3 animate-spin rounded-full border border-accent-blue border-t-transparent" />
                    Сохраняем фильтры...
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {upcomingSchedule.length === 0 ? (
        <div className="flex min-h-[180px] items-center justify-center text-center">
          <div>
            {excludedCount > 0 ? (
              <>
                <p className="text-sm text-text-secondary">
                  Все ближайшие занятия скрыты фильтрами
                </p>

                <p className="mt-1 text-xs text-text-muted">
                  Открой «Фильтр» и включи нужные предметы
                </p>
              </>
            ) : (
              <>
                <p className="text-sm text-text-secondary">
                  Предстоящих занятий нет
                </p>

                <p className="mt-1 text-xs text-text-muted">
                  Новые занятия появятся после синхронизации
                </p>
              </>
            )}
          </div>
        </div>
      ) : mode === "all" && groupedSchedule ? (
        <div
          className="overflow-y-auto overscroll-contain pr-1 fcc-scrollbar"
          style={{ maxHeight: "min(70vh, 800px)" }}
        >
          {groupedSchedule.map(([date, items]) => (
            <div key={date} className="pb-3 last:pb-0">
              <ScheduleDayHeader date={date} count={items.length} />

              <div className="divide-y divide-border/60">
                {items.map((item, index) => (
                  <ScheduleRow
                    key={
                      item.id ||
                      item.stable_id ||
                      `${date}-${item.time}-${index}`
                    }
                    highlighted={highlightId === String(item.stable_id || item.id)}
                    item={item}
                    getTypeDetails={getTypeDetails}
                    getCategoryLabel={getCategoryLabel}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div
          className="overflow-y-auto overscroll-contain pr-1 fcc-scrollbar"
          style={{
            maxHeight: `${Math.min(
              upcomingSchedule.length,
              VISIBLE_ITEMS_BEFORE_SCROLL
            ) * ITEM_HEIGHT_PX
              }px`,
          }}
        >
          <div className="divide-y divide-border/60">
            {upcomingSchedule.map((item, index) => (
              <ScheduleRow
                key={
                  item.id ||
                  item.stable_id ||
                  `${item.time}-${item.subject}-${index}`
                }
                item={item}
                highlighted={highlightId === String(item.stable_id || item.id)}
                getTypeDetails={getTypeDetails}
                getCategoryLabel={getCategoryLabel}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function ScheduleHeader({
  showFilter,
  refreshing,
  excludedCount,
  isOpen = false,
  onFilterClick,
  title = "Ближайшие занятия",
  subtitle = "Предстоящие события из расписания",
}) {
  return (
    <div className="flex min-w-0 flex-1 items-start justify-between gap-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent-blue/10 text-accent-blue">
          <FiCalendar className="h-4 w-4" />
        </div>

        <div className="min-w-0">
          <h2 className="truncate text-lg font-bold text-text-primary">
            {title}
          </h2>

          <p className="mt-0.5 text-xs text-text-muted">{subtitle}</p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        {refreshing && (
          <FiRefreshCw className="h-3.5 w-3.5 animate-spin text-text-muted" />
        )}

        {showFilter && (
          <button
            type="button"
            data-filter-trigger
            onClick={onFilterClick}
            aria-expanded={isOpen}
            className={`
              inline-flex items-center gap-2
              rounded-lg border px-3 py-2
              text-sm font-medium
              transition-all duration-200
              focus:outline-none
              focus:ring-2 focus:ring-accent-blue/20
              ${isOpen
                ? "border-accent-blue/40 bg-accent-blue/10 text-accent-blue"
                : "border-border bg-background text-text-primary hover:border-accent-blue/40 hover:bg-accent-blue/10 hover:text-accent-blue"
              }
            `}
          >
            <FiFilter className="h-4 w-4" />

            <span className="hidden sm:inline">Фильтр</span>

            {excludedCount > 0 && (
              <span className="inline-flex min-w-5 items-center justify-center rounded-full border border-accent-blue/20 bg-accent-blue/5 px-1.5 py-0.5 text-[10px] font-semibold text-accent-blue">
                {excludedCount}
              </span>
            )}

            <FiChevronDown
              className={`
                hidden h-3.5 w-3.5 sm:block
                transition-transform duration-200
                ${isOpen ? "rotate-180" : "rotate-0"}
              `}
            />
          </button>
        )}
      </div>
    </div>
  );
}

function ScheduleDayHeader({ date, count }) {
  return (
    <div className="sticky top-0 z-10 -mx-1 flex items-center justify-between gap-3 border-b border-border/60 bg-panel/95 px-1 py-2 backdrop-blur-sm">
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-text-primary">
          {formatDayLabel(date)}
        </p>

        <p className="mt-0.5 text-[11px] text-text-muted">
          {formatDaySubLabel(date, count)}
        </p>
      </div>

      <span className="shrink-0 rounded-full border border-border bg-background px-2 py-0.5 font-mono text-[10px] font-medium text-text-muted">
        {count}
      </span>
    </div>
  );
}

function ScheduleRow({ item, highlighted = false, getTypeDetails, getCategoryLabel }) {
  const type = getTypeDetails(item.type);
  const isSync = item.status === "sync";
  const category = item.category || "REGULAR";

  return (
    <div
      data-event-id={item.stable_id || item.id}
      className={`
        group h-[100px] shrink-0 py-3
        scroll-mt-20
        transition-[background-color] duration-700 ease-out
        ${highlighted
          ? "bg-accent-blue/15"
          : "hover:bg-card/40"
        }
      `}
    >
      <div className="grid h-full grid-cols-[72px_minmax(0,1fr)_100px] items-center gap-3">
        {/* TIME */}
        <div className="flex items-center gap-2">
          <FiCalendar className="h-4 w-4 shrink-0 text-text-muted" />

          <span className="font-mono text-sm font-semibold text-text-primary">
            {item.time || "--:--"}
          </span>
        </div>

        {/* CONTENT */}
        <div className="min-w-0">
          <div className="flex min-w-0 items-center gap-2">
            <span
              className={`
                inline-flex shrink-0 items-center gap-1.5
                rounded-full border px-2 py-1
                text-[9px] font-semibold uppercase tracking-wide
                ${type.badge}
              `}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${type.dot}`} />

              {type.label}
            </span>

            {category !== "REGULAR" && (
              <span className="hidden shrink-0 rounded-full border border-accent-blue/20 bg-accent-blue/5 px-2 py-1 text-[9px] font-medium text-accent-blue sm:inline-flex">
                {getCategoryLabel(category)}
              </span>
            )}
          </div>

          <p
            className="mt-1.5 truncate text-sm font-semibold text-text-primary"
            title={item.subject || "Без названия"}
          >
            {item.subject || "Без названия"}
          </p>

          <div className="mt-1 flex min-w-0 items-center gap-3 text-[10px] text-text-muted">
            <span className="truncate">
              {item.room || "Аудитория не указана"}
            </span>

            <span className="hidden truncate sm:inline">
              {item.teacher || "Преподаватель не указан"}
            </span>
          </div>
        </div>

        {/* SYNC */}
        <div className="flex justify-end">
          {isSync ? (
            <div className="flex items-center gap-1.5 text-[10px] font-medium text-accent-green">
              <FiCheckCircle className="h-3.5 w-3.5" />

              <span className="hidden sm:inline">В календаре</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-[10px] font-medium text-accent-red">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-red" />

              <span className="hidden sm:inline">Не синхр.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FilterCheckbox({
  checked,
  disabled,
  label,
  onChange,
  compact = false,
}) {
  return (
    <label
      className={`
        flex cursor-pointer items-center gap-3 rounded-lg border transition-colors
        ${compact ? "px-2.5 py-2" : "px-3 py-2.5"}
        ${checked
          ? "border-accent-blue/20 bg-accent-blue/5"
          : "border-transparent hover:bg-card"
        }
        ${disabled ? "cursor-not-allowed opacity-50" : ""}
      `}
    >
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={onChange}
        className="sr-only"
      />

      <span
        className={`
          flex h-4 w-4 shrink-0 items-center justify-center rounded border transition-all
          ${checked
            ? "border-accent-blue bg-accent-blue text-background"
            : "border-border bg-background"
          }
        `}
      >
        {checked && <FiCheck className="h-3 w-3" />}
      </span>

      <span
        className={`
          min-w-0 truncate
          ${checked ? "text-text-primary" : "text-text-secondary"}
          ${compact ? "text-xs" : "text-sm"}
        `}
        title={label}
      >
        {label}
      </span>

      {checked && (
        <span className="ml-auto shrink-0 text-[9px] font-semibold uppercase tracking-wide text-accent-blue">
          скрыто
        </span>
      )}
    </label>
  );
}

function getPluralForm(number, one, few, many) {
  const abs = Math.abs(number);
  const mod10 = abs % 10;
  const mod100 = abs % 100;

  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few;

  return many;
}

function formatDayLabel(dateStr) {
  if (!dateStr) return "Без даты";

  const date = new Date(`${dateStr}T00:00:00`);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  const sameDay = (a, b) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  const formatted = new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    weekday: "long",
  }).format(date);

  if (sameDay(date, today)) return `Сегодня, ${formatted}`;
  if (sameDay(date, tomorrow)) return `Завтра, ${formatted}`;
  return formatted;
}

function formatDaySubLabel(dateStr, count) {
  const date = new Date(`${dateStr}T00:00:00`);
  const short = new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);

  const plural = (() => {
    const n = count % 100;
    if (n >= 11 && n <= 14) return "занятий";
    const m = count % 10;
    if (m === 1) return "занятие";
    if (m >= 2 && m <= 4) return "занятия";
    return "занятий";
  })();

  return `${short} · ${count} ${plural}`;
}