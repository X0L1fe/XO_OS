import { eventBus } from './events';

const API_BASE = '';

export const focusAPI = {
  startSession: async (lessonId = null, goalText = null) => {
    const response = await fetch(`${API_BASE}/api/focus/start`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lesson_id: lessonId, goal_text: goalText }),
    });
    if (!response.ok) {
      throw new Error(`Failed to start focus session: ${response.status}`);
    }
    const data = await response.json();
    // Emit an event that the focus session started
    eventBus.emit('focus-started', data);
    return data;
  },

  pauseSession: async (sessionId) => {
    const response = await fetch(`${API_BASE}/api/focus/${sessionId}/pause`, {
      method: 'POST',
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error(`Failed to pause focus session: ${response.status}`);
    }
    const data = await response.json();
    eventBus.emit('focus-paused', data);
    return data;
  },

  resumeSession: async (sessionId) => {
    const response = await fetch(`${API_BASE}/api/focus/${sessionId}/resume`, {
      method: 'POST',
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error(`Failed to resume focus session: ${response.status}`);
    }
    const data = await response.json();
    eventBus.emit('focus-resumed', data);
    return data;
  },

  completeSession: async (sessionId, completionMode = 'manual', evidence = []) => {
    const response = await fetch(`${API_BASE}/api/focus/${sessionId}/complete`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        completion_mode: completionMode,
        evidence: evidence,
      }),
    });
    if (!response.ok) {
      throw new Error(`Failed to complete focus session: ${response.status}`);
    }
    const data = await response.json();
    eventBus.emit('focus-completed', data);
    return data;
  },

  getActiveSession: async () => {
    const response = await fetch(`${API_BASE}/api/focus/active`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error(`Failed to get active focus session: ${response.status}`);
    }
    return await response.json();
  },

  getSession: async (sessionId) => {
    const response = await fetch(`${API_BASE}/api/focus/${sessionId}`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error(`Failed to get focus session: ${response.status}`);
    }
    return await response.json();
  },

  addEvidence: async (sessionId, evidence) => {
    const response = await fetch(`${API_BASE}/api/focus/${sessionId}/evidence`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(evidence),
    });
    if (!response.ok) {
      throw new Error(`Failed to add evidence: ${response.status}`);
    }
    return await response.json();
  },
};