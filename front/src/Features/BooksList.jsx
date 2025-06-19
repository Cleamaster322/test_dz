import React, {useEffect, useState} from "react";
import api from "../shared/api";


const BooksList = () => {
    const [books, setBooks] = useState([]);
    const [genreMap, setGenreMap] = useState({});
    const [genre, setGenre] = useState('');
    const [search, setSearch] = useState('');
    const [ordering, setOrdering] = useState('');

const loadBooks = async () => {
    try {
        const params = {};
        if (genre) params.genre = genre;
        if (search) params.search = search;
        if (ordering) params.ordering = ordering;

        const res = await api.get('lb/filter/', { params });
        setBooks(res.data);

        // Загружаем названия жанров по id из книг
        const ids = [...new Set(res.data.map(b => b.genre))];
        const genreNames = {};
        await Promise.all(ids.map(async (id) => {
            try {
                const g = await api.get(`lb/genre/${id}/`);
                genreNames[id] = g.data.name;
            } catch {
                genreNames[id] = 'Неизвестно';
            }
        }));
        setGenreMap(genreNames);

    } catch (err) {
        console.error("Ошибка загрузки книг:", err);
    }
};

    useEffect(() => {
        loadBooks();

        const socket = new WebSocket('ws://localhost:8000/ws/books/');

        socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type === 'book_update' && ['delete', 'add'].includes(data.action)) {
            loadBooks(); // перезагружаем список книг
        }
    };

    return () => socket.close();
    }, []); // при первой загрузке

    const handleFilter = (e) => {
        e.preventDefault();
        loadBooks(); // повторно загрузим с фильтрами
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Удалить эту книгу?")) return;
        try {
            await api.delete(`lb/delete_book/${id}/`)
        } catch (err) {
            console.error("Ошибка при удалении книги:", err);
        }
    };

    return (
        <>
            <form onSubmit={handleFilter} style={styles.filterForm}>
                <input
                    type="number"
                    placeholder="Филтр жанр id"
                    value={genre}
                    onChange={(e) => setGenre(e.target.value)}
                    style={styles.input}
                />
                <input
                    type="text"
                    placeholder="Поиск (название или автор)"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    style={styles.input}
                />
                <select
                    value={ordering}
                    onChange={(e) => setOrdering(e.target.value)}
                    style={styles.input}
                >
                    <option value="">Сортировка</option>
                    <option value="title">По названию (А-Я)</option>
                    <option value="-title">По названию (Я-А)</option>
                    <option value="id">Старые сверху</option>
                    <option value="-id">Новые сверху</option>
                </select>
                <button type="submit" style={styles.button}>Фильтровать</button>
            </form>

            <ul className="book-grid">
                {books.map((p) => (
                    <li key={p.id} className="book-card">
                        <p>{p.id}</p>
                        <p>
                            <strong>{p.title}</strong> - {p.author}
                        </p>
                        <p>{p.description}</p>
                        <p>Жанр: <strong>{genreMap[p.genre] || p.genre}</strong></p>
                        <button onClick={() => handleDelete(p.id)}>🗑 Удалить</button>
                    </li>
                ))}
            </ul>
        </>
    );
};

const styles = {
    filterForm: {
        display: 'flex',
        gap: '10px',
        marginBottom: '20px',
    },
    input: {
        padding: '8px',
        fontSize: '14px',
    },
    button: {
        padding: '8px 12px',
        backgroundColor: '#4CAF50',
        color: 'white',
        border: 'none',
        cursor: 'pointer',
    },
};

export default BooksList;