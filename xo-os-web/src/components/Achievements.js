import React, { useEffect, useState } from 'react';

export default function Achievements() {
  const [achievements, setAchievements] = useState([]);
  const [streak, setStreak] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch('/api/achievements', { credentials: 'include' })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        // Transform data to include active/locked status if not present
        const transformedAchievements = (data.achievements || []).map(ach => {
          if (typeof ach === 'string') {
            return {
              text: ach,
              icon: '🏆',
              active: false, // Default to locked if not specified
            };
          }
          return {
            ...ach,
            active: ach.active !== undefined ? ach.active : false, // Default to locked if not specified
          };
        });
        setAchievements(transformedAchievements);
        setStreak(data.streak || 0);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch achievements:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <section className="bg-panel rounded-2xl p-6">
        <h2 className="text-xl font-bold text-accentYellow mb-4">ДОСТИЖЕНИЯ</h2>
        <div className="flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-accentBlue border-t-transparent rounded-full animate-spin" />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="bg-panel rounded-2xl p-6">
        <h2 className="text-xl font-bold text-accentYellow mb-4">ДОСТИЖЕНИЯ</h2>
        <p className="text-center text-secondary">Ошибка загрузки данных</p>
        <p className="text-center text-sm text-secondary mt-1">{error}</p>
      </section>
    );
  }

  return (
    <section className="bg-panel rounded-2xl p-6">
      <div className="space-y-6">
        {/* Streak badge */}
        <div className="flex items-center space-x-4">
          <div className="relative w-10 h-10">
            {/* Yellow/orange highlighted background for streak */}
            <div className="w-full h-full bg-accentYellow/20 rounded-xl flex items-center justify-center">
              <span className="text-accentYellow font-bold text-2xl">🔥</span>
            </div>
            {/* Subtle glow effect */}
            <div className="absolute inset-0 rounded-xl ring-2 ring-accentYellow/30" />
          </div>
          <div className="space-y-1 text-left">
            <p className="text-xs font-medium text-secondary uppercase tracking-wider">STREAK</p>
            <p className="text-base font-mono text-accentYellow">{streak} дней</p>
          </div>
        </div>

        {/* Achievements - compact horizontal strip as per reference */}
        <div className="flex-1">
          <div className="flex flex-wrap gap-2">
            {/* Show first 4 achievements as compact strip */}
            {achievements.slice(0, 4).map((ach, index) => {
              const isActive = ach.active !== undefined ? ach.active : false;

              return (
                <div key={ach.icon || index} className={`relative w-10 h-10 flex-shrink-0 ${isActive ? 'ring-2 ring-accentBlue/50' : ''}`}>
                  {/* Achievement badge - outlined hexagonal/badge-like */}
                  <div className="w-full h-full flex items-center justify-center">
                    {/* Background based on active/locked state */}
                    <div className={`w-full h-full flex items-center justify-center rounded-lg
                      ${isActive
                        ? 'bg-accentBlue/20 border border-accentBlue/50'
                        : 'bg-background/20 border border-border/30'}`}>
                      {/* Icon */}
                      <span className={`
                        text-${isActive ? 'accentBlue' : 'secondary'}
                        text-xl
                        ${isActive ? 'drop-shadow-[0_0_2px_rgba(22,131,255,0.3)]' : ''}
                      `}>
                        {ach.icon || '🏆'}
                      </span>
                    </div>
                    {/* Subtle glow for active achievements */}
                    {isActive && (
                      <div className="absolute inset-0 rounded-lg pointer-events-none ring-2 ring-accentBlue/30" />
                    )}
                  </div>
                </div>
              );
            })}

            {/* Link to show all achievements */}
            <div className="relative w-10 h-10 flex-shrink-0">
              <div className="w-full h-full flex items-center justify-center bg-background/20 border border-border/30 rounded-lg hover:bg-background/30 transition-all duration-200">
                <span className="text-xs text-secondary font-medium">→</span>
              </div>
            </div>
          </div>

          {/* Show all achievements link text */}
          <div className="mt-2 text-center">
            <p className="text-xs text-secondary uppercase tracking-wider">Показать все →</p>
          </div>
        </div>
      </div>
    </section>
  );
}