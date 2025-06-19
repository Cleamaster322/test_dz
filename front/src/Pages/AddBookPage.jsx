import React from 'react';
import AddBookForm from '../Features/AddBookForm';

export default function AddBookPage() {
    return (
        <div style={{ padding: '30px' }}>
            <h1 style={{ textAlign: 'center' }}>Добавить книгу</h1>
            <AddBookForm />
        </div>
    );
}