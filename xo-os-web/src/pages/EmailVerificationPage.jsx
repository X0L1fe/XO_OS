// xo-os-web/src/pages/EmailVerificationPage.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

/**
 * Страница подтверждения электронной почты.
 * Пользователь попадает сюда после перехода по ссылке из письма.
 * После успешной проверки токена показываем сообщение об успехе
 * и предлагаем перейти на страницу входа.
 */
const EmailVerificationPage = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading'); // loading | success | error
  const [message, setMessage] = useState('');

  // Извлекаем токен из query‑строки
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (!token) {
      setStatus('error');
      setMessage('Неверная ссылка подтверждения.');
      return;
    }

    // Отправляем токен на бекенд для верификации
    axios
      .get(`/api/auth/verify-email`, { params: { token } })
      .then(() => {
        setStatus('success');
        setMessage('Ваш email успешно подтверждён!');
      })
      .catch(() => {
        setStatus('error');
        setMessage('Не удалось подтвердить email. Ссылка могла устать или быть неверной.');
      });
  }, []);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-primary mb-4">
            Подтверждение почты
          </h2>
          <div className="animate-spin rounded-full border-4 border-primary border-t-transparent w-12 h-12 mx-auto mb-4"></div>
          <p className="text-secondary">Пожалуйста, подождите...</p>
        </div>
      </div>
    );
  }

  const isSuccess = status === 'success';
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-panel rounded-lg p-8 w-full max-w-md text-center">
        <h2 className={`
          text-2xl font-bold mb-4
          ${isSuccess ? 'text-accentGreen' : 'text-accentRed'}
        `}>
          {isSuccess ? 'Подтверждено' : 'Ошибка'}
        </h2>
        <p className="text-primary mb-6">{message}</p>
        {isSuccess && (
          <button
            onClick={() => navigate('/login')}
            className="bg-accentBlue hover:bg-accentBlue/90 text-primary font-medium py-2 px-4 rounded transition"
          >
            Перейти к входу
          </button>
        )}
        {!isSuccess && (
          <button
            onClick={() => navigate('/')}
            className="bg-accentYellow hover:bg-accentYellow/90 text-primary font-medium py-2 px-4 rounded transition"
          >
            Вернуться на главную
          </button>
        )}
      </div>
    </div>
  );
};

export default EmailVerificationPage;