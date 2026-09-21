import React, { useEffect, useState } from 'react';

const API = process.env.REACT_APP_API_BASE_URL;

export default function CalendarObsidianBlock() {
  const [calendar, setCalendar] = useState({
    status: '',
    lastSync: '',
    created: 0,
    updated: 0,
    moved: 0,
    deleted: 0,
  });
  const [obsidian, setObsidian] = useState({
    status: '',
    vault: '',
    lastSync: '',
  });

  useEffect(() => {
    // Google Calendar
    fetch(`${API}/api/calendar/status`)
      .then(r => r.json())
      .then(setCalendar)
      .catch(console.error);

    // Obsidian
    fetch(`${API}/api/obsidian/status`)
      .then(r => r.json())
      .then(setObsidian)
      .catch(console.error);
  }, []);

  return (
    <section className="bg-panel rounded-2xl p-6 space-y-4">
      <div className="border-t border-border pt-4">
        <h3 className="text-lg font-bold text-accentBlue mb-2">Google Calendar</h3>
        <div className="flex items-center space-x-3">
          <div className={`w-2 h-2 ${calendar.status === 'Синхронизирован' ? 'bg-accentGreen' : 'bg-accentRed'} rounded-full`} />
          <span className="text-sm">{calendar.status || 'Не активен'}</span>
        </div>
        <div className="mt-2 text-xs text-secondary">
          MAISync → Google Calendar
        </div>
        <div className="mt-2 text-xs text-secondary">
          Последняя синхронизация: {calendar.lastSync || 'Отсутствует'}
        </div>
      </div>

      <div className="border-t border-border pt-4">
        <h3 className="text-lg font-bold text-accentBlue mb-2">Obsidian</h3>
        <div className="flex items-center space-x-3">
          <div className={`w-2 h-2 ${obsidian.status === 'Синхронизирован' || obsidian.status === 'Подключён' ? 'bg-accentGreen' : 'bg-accentRed'} rounded-full`} />
          <span className="text-sm">{obsidian.status || 'Отключён'}</span>
        </div>
        <div className="mt-2 text-xs text-secondary">
          Vault: {obsidian.vault || 'Не указан'}
        </div>
        <div className="mt-2 text-xs text-secondary">
          Последняя синхронизация: {obsidian.lastSync || 'Отсутствует'}
        </div>
      </div>
    </section>
  );
}