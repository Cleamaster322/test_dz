import React, { useState } from 'react';
import api from '../shared/api';
import { useNavigate } from 'react-router-dom';

const AddBookForm = () => {
    const [title, setTitle] = useState('');
    const [author, setAuthor] = useState('');
    const [description, setDescription] = useState('');
    const [genre, setGenre] = useState([]);
    const [message, setMessage] = useState('');
    const navigate = useNavigate();


    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('lb/add_book/', {
                title,
                author,
                description,
                genre
            });
            navigate('/books');
        } catch (err) {
            console.error('Ошибка при добавлении книги:', err);
            setMessage('Ошибка при добавлении книги.');
        }
    };

    return (
        <form onSubmit={handleSubmit} style={styles.form}>
            <input
                type="text"
                placeholder="Название"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                style={styles.input}
            />
            <input
                type="text"
                placeholder="Автор"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                required
                style={styles.input}
            />
            <textarea
                placeholder="Описание"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                style={styles.textarea}
            />
            <input
                type="text"
                placeholder="Жанры (например: 1,2,3)"
                value={genre}
                onChange={(e) => {
                    const raw = e.target.value;
                    const numbers = raw
                        .split(',')
                        .map(s => parseInt(s.trim()))
                        .filter(n => !isNaN(n));
                    setGenre(numbers);
                }}
                style={styles.input}
            />
            <button type="submit" style={styles.button}>Добавить книгу</button>
            {message && <p>{message}</p>}
        </form>
    );
};

const styles = {
    form: {
        display: 'flex',
        flexDirection: 'column',
        maxWidth: '400px',
        margin: '0 auto',
        gap: '10px',
    },
    input: {
        padding: '8px',
        fontSize: '14px',
    },
    textarea: {
        padding: '8px',
        fontSize: '14px',
        minHeight: '60px',
    },
    button: {
        padding: '10px',
        backgroundColor: '#4CAF50',
        color: '#fff',
        border: 'none',
        cursor: 'pointer',
    },
};

export default AddBookForm;