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
  FiMapPin,
  FiRefreshCw,
  FiSearch,
  FiUser,
  FiX,
} from "react-icons/fi";

const FILTER_EVENT_NAME = "xo-os:schedule-filters-changed";

const DEFAULT_CATEGORIES = [
  {
    key: "REGULAR",
    label: "Обычные занятия",
  },
  {
    key: "ELECTIVE",
    label: "Элективы",
  },
  {
    key: "MILITARY",
    label: "Военная подготовка",
  },
];

export default function ScheduleList() {
  const instanceIdRef = useRef(
    `schedule-${Math.random().toString(36).slice(2)}`
  );

  const [schedule, setSchedule] = useState([]);
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  const [subjects, setSubjects] = useState([]);

  const [excludedCategories, setExcludedCategories] = useState(new Set());
  const [excludedSubjects, setExcludedSubjects] = useState(new Set());

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [savingFilters, setSavingFilters] = useState(false);

  const [error, setError] = useState(null);
  const [filtersError, setFiltersError] = useState(null);

  const [showFilterMenu, setShowFilterMenu] = useState(false);
  const [subjectSearch, setSubjectSearch] = useState("");

  const loadSchedule = useCallback(async (showLoader = false) => {
    if (showLoader) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }

    try {
      const response = await fetch("/api/schedule", {
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
  }, []);

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

      setExcludedCategories(
        new Set(
          Array.isArray(data.excluded_categories)
            ? data.excluded_categories
            : []
        )
      );

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

      // Не обновляем источник события второй раз.
      if (detail.sourceId === instanceIdRef.current) {
        return;
      }

      if (Array.isArray(detail.excluded_categories)) {
        setExcludedCategories(new Set(detail.excluded_categories));
      }

      if (Array.isArray(detail.excluded_subjects)) {
        setExcludedSubjects(new Set(detail.excluded_subjects));
      }

      // Расписание на Dashboard и во вкладке Schedule
      // должно обновиться после изменения фильтров.
      loadSchedule(false);
    };

    window.addEventListener(FILTER_EVENT_NAME, handleFiltersChanged);

    return () => {
      window.removeEventListener(FILTER_EVENT_NAME, handleFiltersChanged);
    };
  }, [loadSchedule]);

  const saveFilters = useCallback(
    async (nextCategories, nextSubjects) => {
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
            excluded_categories: Array.from(nextCategories),
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
            // Ignore invalid error body.
          }

          throw new Error(message);
        }

        const data = await response.json();

        const savedCategories = new Set(
          Array.isArray(data.excluded_categories)
            ? data.excluded_categories
            : Array.from(nextCategories)
        );

        const savedSubjects = new Set(
          Array.isArray(data.excluded_subjects)
            ? data.excluded_subjects
            : Array.from(nextSubjects)
        );

        setExcludedCategories(savedCategories);
        setExcludedSubjects(savedSubjects);

        window.dispatchEvent(
          new CustomEvent(FILTER_EVENT_NAME, {
            detail: {
              sourceId: instanceIdRef.current,
              excluded_categories: Array.from(savedCategories),
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

  const toggleCategory = (categoryKey) => {
    if (savingFilters) {
      return;
    }

    const nextCategories = new Set(excludedCategories);

    if (nextCategories.has(categoryKey)) {
      nextCategories.delete(categoryKey);
    } else {
      nextCategories.add(categoryKey);
    }

    saveFilters(nextCategories, excludedSubjects);
  };

  const toggleSubject = (subjectKey) => {
    if (savingFilters) {
      return;
    }

    const nextSubjects = new Set(excludedSubjects);

    if (nextSubjects.has(subjectKey)) {
      nextSubjects.delete(subjectKey);
    } else {
      nextSubjects.add(subjectKey);
    }

    saveFilters(excludedCategories, nextSubjects);
  };

  const resetFilters = () => {
    if (savingFilters) {
      return;
    }

    saveFilters(new Set(), new Set());
  };

  const allCategoriesExcluded = useMemo(() => {
    if (categories.length === 0) {
      return false;
    }

    return categories.every((category) =>
      excludedCategories.has(category.key)
    );
  }, [categories, excludedCategories]);

  const toggleAllCategories = () => {
    if (savingFilters) {
      return;
    }

    const nextCategories = new Set();

    if (!allCategoriesExcluded) {
      categories.forEach((category) => {
        nextCategories.add(category.key);
      });
    }

    saveFilters(nextCategories, excludedSubjects);
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

  const excludedCount =
    excludedCategories.size + excludedSubjects.size;

  const getTypeDetails = (type) => {
    const normalizedType = type?.trim().toUpperCase() || "";

    switch (normalizedType) {
      case "LECTURE":
        return {
          label: "Лекция",
          badge:
            "border-accent-blue/30 bg-accent-blue/10 text-accent-blue",
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
          badge:
            "border-accent-red/30 bg-accent-red/10 text-accent-red",
          dot: "bg-accent-red",
        };

      default:
        return {
          label: "Занятие",
          badge:
            "border-border bg-background text-text-secondary",
          dot: "bg-text-secondary",
        };
    }
  };

  const getCategoryLabel = (categoryKey) => {
    const category = categories.find(
      (item) => item.key === categoryKey
    );

    if (category) {
      return category.label;
    }

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

  if (loading) {
    return (
      <section className="rounded-xl border border-border bg-panel p-5">
        <ScheduleHeader
          showFilter={false}
          refreshing={false}
          excludedCount={0}
          onFilterClick={() => { }}
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
        />

        <div className="flex min-h-[180px] flex-col items-center justify-center text-center">
          <p className="text-sm text-text-secondary">
            Не удалось загрузить расписание
          </p>

          <p className="mt-1 text-xs text-text-muted">
            {error}
          </p>

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
          onFilterClick={() =>
            setShowFilterMenu((value) => !value)
          }
        />

        {showFilterMenu && (
          <div className="absolute right-4 top-16 z-50 w-[min(390px,calc(100vw-2rem))] overflow-hidden rounded-xl border border-border bg-panel shadow-2xl shadow-black/30">
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

              <div className="space-y-5">
                {/* Categories */}
                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-text-primary">
                        Категории
                      </p>

                      <p className="mt-0.5 text-[11px] text-text-muted">
                        Скрыть целый тип занятий
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={toggleAllCategories}
                      disabled={savingFilters}
                      className="text-[11px] font-medium text-accent-blue transition-colors hover:text-accent-blue/80 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {allCategoriesExcluded
                        ? "Показать все"
                        : "Скрыть все"}
                    </button>
                  </div>

                  <div className="space-y-1">
                    {categories.map((category) => {
                      const checked = excludedCategories.has(
                        category.key
                      );

                      return (
                        <FilterCheckbox
                          key={category.key}
                          checked={checked}
                          disabled={savingFilters}
                          label={category.label}
                          onChange={() =>
                            toggleCategory(category.key)
                          }
                        />
                      );
                    })}
                  </div>
                </div>

                {/* Subjects */}
                <div className="border-t border-border/60 pt-5">
                  <div className="mb-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-text-primary">
                      Предметы
                    </p>

                    <p className="mt-0.5 text-[11px] text-text-muted">
                      Например, исключи предмет, который уже закрыл
                    </p>
                  </div>

                  {subjects.length > 0 ? (
                    <>
                      <div className="relative mb-2">
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
                            const checked = excludedSubjects.has(
                              subject.key
                            );

                            return (
                              <FilterCheckbox
                                key={subject.key}
                                checked={checked}
                                disabled={savingFilters}
                                label={subject.label || subject.key}
                                onChange={() =>
                                  toggleSubject(subject.key)
                                }
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
                </div>

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
                      disabled={
                        savingFilters || excludedCount === 0
                      }
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
        )}
      </div>

      {schedule.length === 0 ? (
        <div className="flex min-h-[180px] items-center justify-center text-center">
          <div>
            {excludedCount > 0 ? (
              <>
                <p className="text-sm text-text-secondary">
                  Все ближайшие занятия скрыты фильтрами
                </p>

                <p className="mt-1 text-xs text-text-muted">
                  Открой «Фильтр» и включи нужные категории или предметы
                </p>
              </>
            ) : (
              <>
                <p className="text-sm text-text-secondary">
                  Запланированных занятий нет
                </p>

                <p className="mt-1 text-xs text-text-muted">
                  Новые занятия появятся после синхронизации
                </p>
              </>
            )}
          </div>
        </div>
      ) : (
        <div
          className="
    h-[300px]
    overflow-y-auto
    overscroll-contain
    pr-1
    fcc-scrollbar
  "
        >
          <div className="divide-y divide-border/60">
            {schedule.map((item, index) => {
              const type = getTypeDetails(item.type);
              const isSync = item.status === "sync";
              const category = item.category || "REGULAR";

              return (
                <div
                  key={
                    item.id ||
                    item.stable_id ||
                    `${item.time}-${item.subject}-${index}`
                  }
                  className="
            group
            h-[100px]
            shrink-0
            py-3
            transition-colors
            duration-180
            hover:bg-card/40
          "
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
                    inline-flex
                    shrink-0
                    items-center
                    gap-1.5
                    rounded-full
                    border
                    px-2
                    py-1
                    text-[9px]
                    font-semibold
                    uppercase
                    tracking-wide
                    ${type.badge}
                  `}
                        >
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${type.dot}`}
                          />

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

                          <span className="hidden sm:inline">
                            В календаре
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-[10px] font-medium text-accent-red">
                          <span className="h-1.5 w-1.5 rounded-full bg-accent-red" />

                          <span className="hidden sm:inline">
                            Не синхр.
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
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
  onFilterClick,
}) {
  return (
    <div className="flex min-w-0 flex-1 items-start justify-between gap-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent-blue/10 text-accent-blue">
          <FiCalendar className="h-4 w-4" />
        </div>

        <div className="min-w-0">
          <h2 className="truncate text-lg font-bold text-text-primary">
            Ближайшие занятия
          </h2>

          <p className="mt-0.5 text-xs text-text-muted">
            Предстоящие события из расписания
          </p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        {refreshing && (
          <FiRefreshCw className="h-3.5 w-3.5 animate-spin text-text-muted" />
        )}

        {showFilter && (
          <button
            type="button"
            onClick={onFilterClick}
            className="
              inline-flex
              items-center
              gap-2
              rounded-lg
              border
              border-border
              bg-background
              px-3
              py-2
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
            "
          >
            <FiFilter className="h-4 w-4" />

            <span className="hidden sm:inline">
              Фильтр
            </span>

            {excludedCount > 0 && (
              <span className="inline-flex min-w-5 items-center justify-center rounded-full border border-accent-blue/20 bg-accent-blue/5 px-1.5 py-0.5 text-[10px] font-semibold text-accent-blue">
                {excludedCount}
              </span>
            )}

            <FiChevronDown className="hidden h-3.5 w-3.5 sm:block" />
          </button>
        )}
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
        flex
        cursor-pointer
        items-center
        gap-3
        rounded-lg
        border
        transition-colors
        ${compact
          ? "px-2.5 py-2"
          : "px-3 py-2.5"
        }
        ${checked
          ? "border-accent-blue/20 bg-accent-blue/5"
          : "border-transparent hover:bg-card"
        }
        ${disabled
          ? "cursor-not-allowed opacity-50"
          : ""
        }
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
          flex
          h-4
          w-4
          shrink-0
          items-center
          justify-center
          rounded
          border
          transition-all
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
          ${checked
            ? "text-text-primary"
            : "text-text-secondary"
          }
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

  if (mod10 === 1 && mod100 !== 11) {
    return one;
  }

  if (
    mod10 >= 2 &&
    mod10 <= 4 &&
    (mod100 < 10 || mod100 >= 20)
  ) {
    return few;
  }

  return many;
}