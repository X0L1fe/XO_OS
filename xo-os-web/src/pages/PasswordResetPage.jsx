import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

/**
 * Страница сброса пароля по токену из письма.
 * Пользователь вводит новый пароль дважды и подтверждает изменение.
 */
const PasswordResetPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('form'); // form | success
  const [form, setForm] = useState({ password: '', confirm: '', token: '' });
  const [errors, setErrors] = useState({});
  const [submiting, setSubmiting] = useState(false);
  const [message, setMessage] = useState('');

  // Извлекаем токен из URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (!token) {
      setErrors({ token: 'Отсутствует токен сброса пароля.' });
    }
    setForm(prev => ({ ...prev, token }));
  }, []);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    // Очищаем ошибку при вводе
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setSubmiting(true);
    const newErrors = {};

    // Простейшая валидация
    if (!form.password) newErrors.password = 'Введите новый пароль';
    if (form.password !== form.confirm) newErrors.confirm = 'Пароли не совпадают';

    if (Object.keys(newErrors).length) {
      setErrors(newErrors);
      setSubmiting(false);
      return;
    }

    try {
      await axios.post(`/api/auth/reset-password`, form);
      setStep('success');
      setMessage('Пароль успешно изменён. Теперь вы можете войти.');
    } catch (err) {
      // Предполагаем, что бекенд вернёт сообщение об ошибке
      setErrors({ submit: err.response?.data?.message || 'Ошибка сервера' });
      setSubmiting(false);
    }
  };

  if (step === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="bg-panel rounded-lg p-8 w-full max-w-md text-center">
          <h2 className="text-2xl font-bold text-accentGreen mb-4">
            Пароль изменён
          </h2>
          <p className="text-primary mb-6">{message}</p>
          <button
            onClick={() => navigate('/login')}
            className="bg-accentBlue hover:bg-accentBlue/90 text-primary font-medium py-2 px-4 rounded transition"
          >
            Перейти к входу
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-panel rounded-lg p-8 w-full max-w-md space-y-6">
        <h2 className="text-2xl font-bold text-primary text-center">
          Сбросить пароль
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="password" className="block text-secondary mb-2">
              Новый пароль
            </label>
            <input
              id="password"
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              className="w-full bg-background/50 border border-primary/20 rounded px-3 py-2 text-primary placeholder-secondary focus:outline-none focus:ring-2 focus:ring-accentBlue"
              placeholder="••••••••"
              autoComplete="new-password"
            />
            {errors.password && (
              <p className="text-accentRed text-sm mt-1">{errors.password}</p>
            )}
          </div>

          <div>
            <label htmlFor="confirm" className="block text-secondary mb-2">
              Подтвердите пароль
            </label>
            <input
              id="confirm"
              type="password"
              name="confirm"
              value={form.confirm}
              onChange={handleChange}
              className="w-full bg-background/50 border border-primary/20 rounded px-3 py-2 text-primary placeholder-secondary focus:outline-none focus:ring-2 focus:ring-accentBlue"
              placeholder="••••••••"
              autoComplete="new-password"
            />
            {errors.confirm && (
              <p className="text-accentRed text-sm mt-1">{errors.confirm}</p>
            )}
          </div>

          {errors.submit && (
            <p className="text-accentRed text-sm">{errors.submit}</p>
          )}

          <button
            type="submit"
            disabled={submiting}
            className={`w-full bg-accentBlue hover:bg-accentBlue/90 text-primary font-medium py-2 px-4 rounded transition
                       ${submiting ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {submiting ? 'Сохранение...' : 'Сохранить пароль'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PasswordResetPage;