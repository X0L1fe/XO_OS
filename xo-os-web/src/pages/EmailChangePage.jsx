import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

/**
 * Страница смены электронной почты.
 * Пользователь приходит сюда по ссылке из письма, подтверждающей намерение изменить email.
 * На этой странице он вводит новый email и текущий пароль, после чего система
 * отправляет подтверждающее письмо на новый адрес.
 */
const EmailChangePage = () => {
  const navigate = useNavigate();
  const location = useLocation(); // чтобы читать query‑параметры
  const [step, setStep] = useState('confirmIntent'); // confirmIntent | enterNew | success
  const [form, setForm] = useState({
    intentToken: '',   // токен из первого письма (подтверждение намерения)
    newEmail: '',
    password: '',
    confirmToken: '',  // токен из второго письма (подтверждение нового email)
  });
  const [errors, setErrors] = useState({});
  const [submiting, setSubmiting] = useState(false);
  const [message, setMessage] = useState('');

  // Извлекаем токен подтверждения намерения из URL
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const token = urlParams.get('token');
    if (token) {
      setForm(prev => ({ ...prev, intentToken: token }));
    } else {
      setErrors({ intentToken: 'Отсутствует токен подтверждения намерения.' });
    }
  }, [location]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setSubmiting(true);
    const newErrors = {};

    if (step === 'confirmIntent') {
      // На этом шаге проверяем только наличие intentToken (он уже есть в форме)
      // Если всё ok – переходим ко вводу нового email
      if (!form.intentToken) {
        newErrors.intentToken = 'Токен намерения отсутствует';
      }
    } else if (step === 'enterNew') {
      // Валидация нового email и пароля
      if (!form.newEmail) newErrors.newEmail = 'Введите новый email';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.newEmail))
        newErrors.newEmail = 'Некорректный формат email';

      if (!form.password) newErrors.password = 'Введите текущий пароль';
    }

    if (Object.keys(newErrors).length) {
      setErrors(newErrors);
      setSubmiting(false);
      return;
    }

    try {
      if (step === 'confirmIntent') {
        // Первый шаг: просто подтверждаем, что пользователь действительно хочет сменить email.
        // Отправляем токен намерения на бекенд, который в ответ выдаёт токен для следующего шага
        // (в реальности бекенд может сразу переводить на страницу ввода нового email).
        await axios.post(`/api/auth/confirm-email-change-intent`, {
          token: form.intentToken,
        });
        setStep('enterNew');
      } else if (step === 'enterNew') {
        // Второй шаг: отправляем новый email и пароль, бекенд шлёт подтверждающее письмо на новый email
        await axios.post(`/api/auth/request-email-change`, {
          intentToken: form.intentToken,
          newEmail: form.newEmail,
          password: form.password,
        });
        setMessage(
          'На новый email отправлено письмо с подтверждением. Пожалуйста, проверьте свою почту.'
        );
        setStep('success');
      }
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        'Произошла ошибка на сервере. Попробуйте позже.';
      setErrors({ submit: msg });
    } finally {
      setSubmiting(false);
    }
  };

  // Рендер в зависимости от текущего шага
  if (step === 'confirmIntent') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="bg-panel rounded-lg p-8 w-full max-w-md text-center">
          <h2 className="text-2xl font-bold text-primary mb-4">
            Подтверждение намерения сменить email
          </h2>
          <p className="text-primary mb-6">
            Мы получили запрос на изменение вашего электронного адреса.
            Пожалуйста, подтвердите, что вы действительно хотите продолжить.
          </p>
          <button
            onClick={() => {
              // Имитируем отправку формы (в реальности тут должен быть запрос,
              // но так как токен уже в query, просто переходим к следующему шагу)
              setStep('enterNew');
            }}
            className="bg-accentBlue hover:bg-accentBlue/90 text-primary font-medium py-2 px-4 rounded transition"
          >
            Подтвердить намерение
          </button>
          <button
            onClick={() => navigate('/')}
            className="mt-4 bg-accentYellow hover:bg-accentYellow/90 text-primary font-medium py-2 px-4 rounded transition"
          >
            Отменить и вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  if (step === 'enterNew') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="bg-panel rounded-lg p-8 w-full max-w-md">
          <h2 className="text-2xl font-bold text-primary mb-6 text-center">
            Ввод нового email
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="newEmail" className="block text-secondary mb-2">
                Новый электронный адрес
              </label>
              <input
                id="newEmail"
                type="email"
                name="newEmail"
                value={form.newEmail}
                onChange={handleChange}
                className="w-full bg-background/50 border border-primary/20 rounded px-3 py-2 text-primary placeholder-secondary focus:outline-none focus:ring-2 focus:ring-accentBlue"
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.newEmail && (
                <p className="text-accentRed text-sm mt-1">{errors.newEmail}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-secondary mb-2">
                Текущий пароль (для подтверждения личности)
              </label>
              <input
                id="password"
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                className="w-full bg-background/50 border border-primary/20 rounded px-3 py-2 text-primary placeholder-secondary focus:outline-none focus:ring-2 focus:ring-accentBlue"
                placeholder="••••••••"
                autoComplete="current-password"
              />
              {errors.password && (
                <p className="text-accentRed text-sm mt-1">{errors.password}</p>
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
              {submiting ? 'Отправка запроса...' : 'Отправить запрос на смену email'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Шаг success – показываем сообщение и предлагаем проверить почту
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-panel rounded-lg p-8 w-full max-w-md text-center">
        <h2 className="text-2xl font-bold text-accentGreen mb-4">
          Ожидание подтверждения
        </h2>
        <p className="text-primary mb-6">{message}</p>
        <p className="text-secondary mb-6">
          После перехода по ссылке из письма ваш email будет изменён,
          и вы будем перенаправлены на страницу входа.
        </p>
        <button
          onClick={() => navigate('/login')}
          className="bg-accentBlue hover:bg-accentBlue/90 text-primary font-medium py-2 px-4 rounded transition"
        >
          Перейти к входу
        </button>
      </div>
    </div>
  );
};

export default EmailChangePage;