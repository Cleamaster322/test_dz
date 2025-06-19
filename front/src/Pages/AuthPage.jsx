import React from 'react';
import AuthForm from '../Features/Auth.jsx';

export default function AuthPage() {
    return (
        <div style={styles.container}>
            <h1 style={styles.header}>Авторизация</h1>
            <AuthForm />
        </div>
    );
}

const styles = {
    container: {
        maxWidth: '500px',
        margin: '50px auto',
        padding: '20px',
        border: '1px solid #ccc',
        borderRadius: '10px',
        backgroundColor: '#f9f9f9',
        textAlign: 'center',
    },
    header: {
        marginBottom: '20px',
    },
};