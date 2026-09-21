import React, { useState, useEffect } from 'react';

const Onboarding = ({ user, handleAuthenticated, onboardingCompleted }) => {
  const [groups, setGroups] = useState([]);
  const [filteredGroups, setFilteredGroups] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Fetch groups on mount
  useEffect(() => {
    const fetchGroups = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch("/api/mais/groups", {
          credentials: "include",
        });
        if (!resp.ok) {
          throw new Error(`HTTP error! status: ${resp.status}`);
        }
        const data = await resp.json();
        setGroups(data.groups || []);
        setFilteredGroups(data.groups || []);
      } catch (err) {
        console.error("Failed to fetch groups:", err);
        setError("Не удалось загрузить список групп");
      } finally {
        setLoading(false);
      }
    };
    fetchGroups();
  }, []);

  // Filter groups based on search term
  useEffect(() => {
    if (!searchTerm) {
      setFilteredGroups(groups);
    } else {
      const term = searchTerm.toLowerCase();
      const filtered = groups.filter(group =>
        group.name.toLowerCase().includes(term) ||
        (group.fac && group.fac.toLowerCase().includes(term)) ||
        (group.level && group.level.toString().includes(term)) ||
        (group.course && group.course.toString().includes(term))
      );
      setFilteredGroups(filtered);
    }
  }, [searchTerm, groups]);

  const handleGroupSelect = (groupName) => {
    setSelectedGroup(groupName);
  };

  const handleSkipGroup = async () => {
    setLoading(true);
    setError(null);
    try {
      // Mark onboarding as completed without selecting a group
      const statusResp = await fetch("/api/auth/status", {
        credentials: "include",
      });
      if (!statusResp.ok) {
        throw new Error(`HTTP error! status: ${statusResp.status}`);
      }
      const data = await statusResp.json();
      handleAuthenticated({
        ...data,
        onboarding_completed: true,
      });
      onboardingCompleted();
      setSuccess(true);
    } catch (err) {
      console.error("Failed to skip group selection:", err);
      setError("Не удалось пропустить выбор группы. Пожалуйста, попробуйте снова.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmGroup = async () => {
    if (!selectedGroup) {
      setError("Пожалуйста, выберите группу");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Save the group first
      const resp = await fetch("/api/mais/group", {
        method: "POST",
        credentials: "include",
        body: new URLSearchParams({ group_name: selectedGroup }),
      });
      if (!resp.ok) {
        throw new Error(`HTTP error! status: ${resp.status}`);
      }

      // Import schedule for the selected group
      const importResp = await fetch("/api/mais/import", {
        method: "POST",
        credentials: "include",
        body: new URLSearchParams({ group_name: selectedGroup }),
      });

      if (!importResp.ok) {
        throw new Error(`HTTP error! status: ${importResp.status}`);
      }

      // Update user state to mark onboarding as completed
      const statusResp = await fetch("/api/auth/status", {
        credentials: "include",
      });
      if (!statusResp.ok) {
        throw new Error(`HTTP error! status: ${statusResp.status}`);
      }
      const data = await statusResp.json();
      handleAuthenticated({
        ...data,
        onboarding_completed: true,
      });
      onboardingCompleted();
      setSuccess(true);
    } catch (err) {
      console.error("Failed to complete onboarding:", err);
      setError("Не удалось завершить настройку. Пожалуйста, попробуйте снова.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-primary p-6">
      <div className="max-w-xl mx-auto">
        <h1 className="text-2xl font-bold text-center mb-6">
          Выберите вашу группу
        </h1>
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 mb-4">
            <p>{error}</p>
          </div>
        )}
        {success && (
          <div className="bg-green-50 border-l-4 border-green-500 text-green-700 p-4 mb-4">
            <p>Группа выбрана! Импортируем расписание...</p>
          </div>
        )}
        <div className="mb-4">
          <label className="block text-sm font-medium text-primary mb-2">
            Поиск группы
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Введите номер группы, факультет, курс или уровень"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accentBlue"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-primary mb-2">
            Группы
          </label>
          <div className="border border-gray-300 rounded-md max-h-96 overflow-y-auto">
            {loading && !groups.length ? (
              <div className="py-4 text-center text-gray-500">
                Загрузка...
              </div>
            ) : filteredGroups.length === 0 ? (
              <div className="py-4 text-center text-gray-500">
                Группы не найдены
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {filteredGroups.map((group) => (
                  <li key={group.name} className={`px-4 py-3 hover:bg-gray-50 cursor-pointer ${selectedGroup === group.name ? "bg-accentBlue/20" : ""}`}
                    onClick={() => handleGroupSelect(group.name)}
                  >
                    <div className="flex justify-between text-sm">
                      <div>
                        <p className="font-medium text-primary">{group.name}</p>
                        {group.fac && <p className="text-xs text-gray-500">Факультет: {group.fac}</p>}
                        {group.level && <p className="text-xs text-gray-500">Уровень: {group.level}</p>}
                        {group.course && <p className="text-xs text-gray-500">Курс: {group.course}</p>}
                      </div>
                      {selectedGroup === group.name && (
                        <span className="text-accentGreen">✓ Выбрано</span>
                      )}
                    </div>
                    </li>
                  ))}
                </ul>
                
              )}
            </div>
          </div>
          <div className="flex justify-between">
            <button
              onClick={handleSkipGroup}
              disabled={loading}
              className={`px-6 py-3 bg-accentBlue/20 hover:bg-accentBlue/30 text-primary rounded transition-colors ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Пропуск...' : 'Пропустить выбор группы'}
            </button>
            <button
              onClick={handleConfirmGroup}
              disabled={loading || !selectedGroup}
              className={`px-6 py-3 bg-accentBlue text-white rounded-xl hover:bg-accentBlue/90 transition-colors ${
                loading || !selectedGroup ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Подтверждение...' : 'Подтвердить выбор'}
            </button>
          </div>
        </div>
      </div>
    );
  };

export default Onboarding;