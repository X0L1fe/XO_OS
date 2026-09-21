import React, { useEffect, useState } from 'react';

export default function NowBlock() {
  const [now, setNow] = useState({
    taskTitle: '',
    taskDesc: '',
    timeEstimate: '',
    priority: '',
    xpReward: 0,
    time: '--:--',
    category: '', // category of task (lecture, practice, etc.)
  });

  useEffect(() => {
    fetch('/api/now', { credentials: 'include' })
      .then(r => r.json())
      .then(setNow)
      .catch(console.error);
  }, []);

  return (
    <section className="bg-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between pb-2">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 bg-accentBlue/20 rounded">
            <span className="w-1.5 h-1.5 bg-accentBlue rounded mx-auto mt-0.5" />
          </div>
          <h2 className="text-lg font-semibold text-primary tracking-tight">СЕЙЧАС</h2>
        </div>
        <span className="text-xs font-mono text-secondary">{now.time}</span>
      </div>

      <div className="space-y-3">
        <div className="space-y-1">
          <p className="text-2xl font-bold text-primary tracking-tight">{now.taskTitle}</p>
          {now.category && (
            <p className="text-xs text-secondary uppercase tracking-wider">{now.category}</p>
          )}
          {now.taskDesc && (
            <p className="text-sm text-secondary">{now.taskDesc}</p>
          )}
        </div>

        <div className="mt-4 flex items-center space-x-4 text-sm">
          <span className="flex-1 text-primary">{now.timeEstimate}</span>
          <span className="w-0.5 h-0.5 bg-gray-600 mx-2" />
          <span className="flex-1 text-secondary text-right">{now.priority}</span>
        </div>

        <div className="mt-4 flex items-center space-x-3">
          <div className="w-2.5 h-2.5 bg-accentGreen/20 rounded">
            <span className="w-1.5 h-1.5 bg-accentGreen rounded mx-auto mt-0.5" />
          </div>
          <span className="text-sm font-medium text-accentGreen">+{now.xpReward} XP</span>
        </div>
      </div>

      <button
        className="w-full mt-5 py-2 px-4 bg-accentBlue hover:bg-accentBlue/80 text-primary font-medium rounded transition-all duration-200"
      >
        НАЧАТЬ
      </button>
    </section>
  );
}