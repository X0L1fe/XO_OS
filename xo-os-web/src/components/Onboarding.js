import React, { useEffect, useMemo, useState } from "react";
import {
  FiAlertCircle,
  FiArrowRight,
  FiBookOpen,
  FiCheck,
  FiChevronRight,
  FiLoader,
  FiSearch,
  FiUsers,
} from "react-icons/fi";

const Onboarding = ({
  user,
  handleAuthenticated,
  onboardingCompleted,
}) => {
  const [groups, setGroups] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");

  const [loading, setLoading] = useState(false);
  const [groupsLoading, setGroupsLoading] = useState(true);

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchGroups = async () => {
      setGroupsLoading(true);
      setError(null);

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
        setError("Не удалось загрузить список групп.");
      } finally {
        setGroupsLoading(false);
      }
    };

    fetchGroups();
  }, []);

  const filteredGroups = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();

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
  }, [groups, searchTerm]);

  const handleGroupSelect = (groupName) => {
    setSelectedGroup(groupName);
    setError(null);
  };

  const getErrorMessage = async (response, fallback) => {
    try {
      const data = await response.json();

      return (
        data?.detail ||
        data?.message ||
        fallback
      );
    } catch {
      return fallback;
    }
  };

  const refreshAuthState = async () => {
    const response = await fetch("/api/auth/status", {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    handleAuthenticated({
      ...data,
      onboarding_completed: true,
    });

    onboardingCompleted();
  };

  const handleSkipGroup = async () => {
    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await refreshAuthState();
      setSuccess(true);
    } catch (err) {
      console.error("Failed to skip group selection:", err);
      setError(
        "Не удалось пропустить настройку. Пожалуйста, попробуйте снова."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmGroup = async () => {
    if (!selectedGroup) {
      setError("Выберите группу.");
      return;
    }

    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);

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
        const message = await getErrorMessage(
          groupResponse,
          "Не удалось сохранить выбранную группу."
        );

        throw new Error(message);
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
        const message = await getErrorMessage(
          importResponse,
          "Не удалось импортировать расписание."
        );

        throw new Error(message);
      }

      await refreshAuthState();

      setSuccess(true);
    } catch (err) {
      console.error("Failed to complete onboarding:", err);

      setError(
        err.message ||
          "Не удалось завершить настройку. Пожалуйста, попробуйте снова."
      );
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-background px-4 py-8 text-text-primary sm:px-6">
        <div className="pointer-events-none fixed inset-0 overflow-hidden">
          <div className="absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 rounded-full bg-accent-blue/10 blur-3xl" />
        </div>

        <div className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center">
          <div className="w-full max-w-lg rounded-2xl border border-border bg-panel p-8 text-center shadow-2xl shadow-black/20">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent-green/20 bg-accent-green/10 text-accent-green">
              <FiCheck className="h-8 w-8" />
            </div>

            <h1 className="mt-6 text-2xl font-bold text-text-primary">
              Настройка завершена
            </h1>

            <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-text-secondary">
              Профиль пользователя обновлён. XO_OS готов перейти к следующему
              этапу настройки.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8 text-text-primary sm:px-6 lg:px-8">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-180px] h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-accent-blue/10 blur-3xl" />
        <div className="absolute bottom-[-120px] right-[-100px] h-[300px] w-[300px] rounded-full bg-accent-blue/5 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl items-center justify-center">
        <div className="w-full rounded-2xl border border-border bg-panel/95 shadow-2xl shadow-black/20 backdrop-blur-xl">
          <div className="grid lg:grid-cols-[300px_minmax(0,1fr)]">
            {/* Intro */}
            <div className="border-b border-border p-6 lg:border-b-0 lg:border-r lg:p-8">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-accent-blue/20 bg-accent-blue/10 text-accent-blue">
                <FiUsers className="h-5 w-5" />
              </div>

              <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-blue">
                XO_OS / INITIAL SETUP
              </p>

              <h1 className="mt-3 text-2xl font-bold leading-tight text-text-primary">
                Выберите учебную группу
              </h1>

              <p className="mt-3 text-sm leading-6 text-text-secondary">
                Группа используется для импорта расписания из MAIS и
                первоначальной настройки вашего профиля.
              </p>

              <div className="mt-6 space-y-3">
                <InfoRow
                  icon={<FiBookOpen className="h-4 w-4" />}
                  title="Расписание"
                  description="Импорт занятий вашей группы"
                />

                <InfoRow
                  icon={<FiUsers className="h-4 w-4" />}
                  title="Учебная группа"
                  description="Сохраняется в вашем профиле"
                />
              </div>

              <div className="mt-8 rounded-xl border border-border/70 bg-background/50 p-3">
                <p className="text-xs leading-5 text-text-muted">
                  Группу можно пропустить. В этом случае автоматический импорт
                  расписания выполняться не будет.
                </p>
              </div>
            </div>

            {/* Selection */}
            <div className="p-6 lg:p-8">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-text-primary">
                    Учебная группа
                  </p>

                  <p className="mt-1 text-xs text-text-muted">
                    Найдено: {filteredGroups.length}
                  </p>
                </div>

                {selectedGroup && (
                  <div className="hidden rounded-lg border border-accent-blue/20 bg-accent-blue/5 px-3 py-2 text-right sm:block">
                    <p className="text-[10px] uppercase tracking-wide text-text-muted">
                      Выбрана
                    </p>

                    <p className="mt-0.5 text-xs font-semibold text-accent-blue">
                      {selectedGroup}
                    </p>
                  </div>
                )}
              </div>

              {error && (
                <div className="mt-5 flex items-start gap-3 rounded-xl border border-accent-red/20 bg-accent-red/5 p-3.5">
                  <FiAlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-accent-red" />

                  <p className="text-xs leading-5 text-accent-red">
                    {error}
                  </p>
                </div>
              )}

              <div className="mt-6">
                <label
                  htmlFor="group-search"
                  className="mb-2 block text-xs font-medium text-text-secondary"
                >
                  Поиск
                </label>

                <div className="relative">
                  <FiSearch className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />

                  <input
                    id="group-search"
                    type="text"
                    value={searchTerm}
                    onChange={(event) =>
                      setSearchTerm(event.target.value)
                    }
                    placeholder="Группа, факультет, курс или уровень"
                    className="w-full rounded-xl border border-border bg-background/70 py-3 pl-10 pr-4 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-accent-blue/50 focus:ring-2 focus:ring-accent-blue/10"
                  />
                </div>
              </div>

              <div className="mt-4 overflow-hidden rounded-xl border border-border bg-background/40">
                <div className="max-h-[420px] overflow-y-auto">
                  {groupsLoading ? (
                    <div className="flex min-h-[260px] flex-col items-center justify-center">
                      <FiLoader className="h-5 w-5 animate-spin text-accent-blue" />

                      <p className="mt-3 text-xs text-text-muted">
                        Загружаем список групп...
                      </p>
                    </div>
                  ) : filteredGroups.length === 0 ? (
                    <div className="flex min-h-[260px] flex-col items-center justify-center px-6 text-center">
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
                        const isSelected =
                          selectedGroup === group.name;

                        return (
                          <button
                            key={group.name}
                            type="button"
                            onClick={() =>
                              handleGroupSelect(group.name)
                            }
                            className={`group w-full px-4 py-3.5 text-left transition-colors ${
                              isSelected
                                ? "bg-accent-blue/10"
                                : "hover:bg-card/70"
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div
                                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border ${
                                  isSelected
                                    ? "border-accent-blue/30 bg-accent-blue/10 text-accent-blue"
                                    : "border-border bg-background text-text-muted"
                                }`}
                              >
                                {isSelected ? (
                                  <FiCheck className="h-4 w-4" />
                                ) : (
                                  <FiUsers className="h-4 w-4" />
                                )}
                              </div>

                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2">
                                  <p className="truncate text-sm font-semibold text-text-primary">
                                    {group.name}
                                  </p>

                                  {isSelected && (
                                    <span className="hidden rounded-full border border-accent-blue/20 bg-accent-blue/5 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-accent-blue sm:inline-flex">
                                      выбрано
                                    </span>
                                  )}
                                </div>

                                <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-text-muted">
                                  {group.fac && (
                                    <span>
                                      {group.fac}
                                    </span>
                                  )}

                                  {group.level && (
                                    <span>
                                      {group.level}
                                    </span>
                                  )}

                                  {group.course && (
                                    <span>
                                      {group.course} курс
                                    </span>
                                  )}
                                </div>
                              </div>

                              <FiChevronRight
                                className={`h-4 w-4 shrink-0 transition-transform ${
                                  isSelected
                                    ? "translate-x-0.5 text-accent-blue"
                                    : "text-text-muted group-hover:translate-x-0.5"
                                }`}
                              />
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
                <button
                  type="button"
                  onClick={handleSkipGroup}
                  disabled={loading}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-background px-4 py-3 text-sm font-medium text-text-secondary transition-colors hover:border-accent-blue/30 hover:bg-card hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <FiLoader className="h-4 w-4 animate-spin" />
                      Обработка...
                    </>
                  ) : (
                    "Пропустить"
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleConfirmGroup}
                  disabled={loading || !selectedGroup}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-accent-blue px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-accent-blue/10 transition-all hover:bg-accent-blue/90 hover:shadow-accent-blue/20 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {loading ? (
                    <>
                      <FiLoader className="h-4 w-4 animate-spin" />
                      Настраиваем...
                    </>
                  ) : (
                    <>
                      Продолжить
                      <FiArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>

              {selectedGroup && (
                <div className="mt-4 flex items-center justify-between rounded-xl border border-accent-blue/15 bg-accent-blue/5 px-3.5 py-3 sm:hidden">
                  <span className="text-xs text-text-muted">
                    Выбрана группа
                  </span>

                  <span className="max-w-[60%] truncate text-xs font-semibold text-accent-blue">
                    {selectedGroup}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function InfoRow({ icon, title, description }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-background text-accent-blue">
        {icon}
      </div>

      <div className="min-w-0">
        <p className="text-xs font-medium text-text-primary">
          {title}
        </p>

        <p className="mt-0.5 text-[11px] leading-5 text-text-muted">
          {description}
        </p>
      </div>
    </div>
  );
}

export default Onboarding;