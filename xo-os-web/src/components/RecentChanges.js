import React, { useEffect, useState } from 'react';

export default function RecentChanges() {
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Placeholder: you can replace with actual API call
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <section className="bg-panel rounded-2xl p-6">
        <div className="flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-accentBlue border-t-transparent rounded-full animate-spin" />
        </div>
      </section>
    );
  }

  if (changes.length === 0) {
    return (
      <section className="bg-panel rounded-2xl p-6">
        <p className="text-center text-sm text-secondary">Нет изменений</p>
      </section>
    );
  }

  return (
    <section className="bg-panel rounded-2xl p-6 space-y-4">
      {changes.map((change, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className="w-2 h-2 bg-accentBlue/20 rounded flex items-center justify-center">
            <span className="w-1 h-1 bg-accentBlue rounded" />
          </div>
          <div className="flex-1 space-y-1">
            <p className="text-sm text-secondary">{change.time}</p>
            <p className="text-base font-medium text-primary">{change.description}</p>
            <p className="text-sm text-secondary">{change.change}</p>
          </div>
        </div>
      ))}
    </section>
  );
}