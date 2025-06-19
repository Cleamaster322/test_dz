import React from 'react';
import api from './api';

export default function LogoutButton({ onLogout }) {
    const handleLogout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        api.setTokenAuth(); // очистить Authorization
        onLogout?.();
    };

    return <button onClick={handleLogout}>Выйти</button>;
}