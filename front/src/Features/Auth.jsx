import {useState} from 'react'
import api from "../shared/api.jsx"
import {useNavigate} from 'react-router-dom';

export default function AuthForm() {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        // какой эндпоинт вызываем
        const endpoint = isLogin ? 'lb/login/' : 'lb/register/';
        const config = isLogin ? {} : {headers: {Authorization: ''}};

        try {
            // отправляем запрос (api.post умеет принимать 3-й аргумент config)
            const {data} = await api.post(endpoint, {username, password, email}, config);

            if (isLogin) {
                // логин: сохраняем токены и настраиваем заголовок
                const {access, refresh} = data;
                localStorage.setItem('accessToken', access);
                localStorage.setItem('refreshToken', refresh);
                api.setTokenAuth();          // обновили Authorization по месту
                navigate('/books');          // переходим к списку книг
            } else {
                // регистрация прошла успешно
                setMessage('Регистрация успешна. Теперь войдите.');
                setIsLogin(true);            // переключаем форму в режим логина
            }
        } catch (err) {
            // выводим текст ошибки (с безопасным fallback)
            setMessage('Ошибка: ' + (err.response?.data?.detail ?? 'Проверьте данные'));
        }
    };

    return (
        <div>
            <h2>{isLogin ? 'Вход' : 'Регистрация'}</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Имя пользователя"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                /><br/>
                <input
                    type="password"
                    placeholder="Пароль"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                /><br/>
                {!isLogin && (
                    <>
                        <input
                            type="email"
                            placeholder="Почта"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        /><br/>
                    </>
                )}

                <button type="submit">{isLogin ? 'Войти' : 'Зарегистрироваться'}</button>
            </form>
            <button onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти'}
            </button>
            <p>{message}</p>
        </div>
    );
}