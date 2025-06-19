import React from 'react';
import BooksList from '../Features/BooksList';
import { useNavigate } from 'react-router-dom';

export default function BooksPage() {
    const navigate = useNavigate();

    const handleAdd = () => {
        navigate('/add-book');
    };

    const handleLogout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        navigate('/');
    };

    return (
        <div style={styles.container}>
            <div style={styles.headerRow}>
                <h1>Список книг</h1>
                <button onClick={handleAdd} style={styles.add}>Добавить книгу</button>
                <button onClick={handleLogout} style={styles.logout}>Выйти</button>
            </div>
            <BooksList />
        </div>
    );
}

const styles = {
    container: {
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '20px',
        fontFamily: 'Arial, sans-serif',
    },
    headerRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
    },
    logout: {
        padding: '8px 12px',
        backgroundColor: '#f44336',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
    },
        add: {
        padding: '8px 12px',
        backgroundColor: '#378922',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
    },
};