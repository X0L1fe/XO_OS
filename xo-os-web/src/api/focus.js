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
    if (!evidence || !evidence.type) {
      throw new Error('Evidence type is required');
    }

    const formData = new FormData();
    formData.append('type', evidence.type);

    if (evidence.type === 'image') {
      if (!(evidence.file instanceof File)) {
        throw new Error('Image evidence requires a File object');
      }
      formData.append('file', evidence.file);
      if (evidence.content) {
        formData.append('content', evidence.content);
      }
    } else if (evidence.type === 'text' || evidence.type === 'url') {
      if (!evidence.content) {
        throw new Error(`${evidence.type} evidence requires content`);
      }
      formData.append('content', evidence.content);
    } else {
      throw new Error(`Unsupported evidence type: ${evidence.type}`);
    }

    const response = await fetch(
      `${API_BASE}/api/focus/${sessionId}/evidence`,
      {
        method: 'POST',
        credentials: 'include',
        // ВАЖНО: Content-Type не выставляем — браузер сам поставит
        // multipart/form-data с корректным boundary.
        body: formData,
      }
    );

    if (!response.ok) {
      let detail = '';
      try {
        const err = await response.json();
        if (err && err.detail) {
          detail = `: ${err.detail}`;
        }
      } catch {
        // тело не JSON — игнорируем
      }
      throw new Error(`Failed to add evidence (${response.status})${detail}`);
    }

    return await response.json();
  },
};