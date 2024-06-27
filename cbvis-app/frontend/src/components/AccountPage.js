import React, { useState } from 'react';
import axios from 'axios';

const AccountPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleRegister = () => {
        axios.post('http://localhost:5000/api/register', { username, password })
            .then(response => setMessage(response.data.message))
            .catch(error => setMessage(error.response.data.error));
    };

    return (
        <div>
            <h1>Account Page</h1>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleRegister}>Register</button>
            {message && <p>{message}</p>}
        </div>
    );
}

export default AccountPage;
