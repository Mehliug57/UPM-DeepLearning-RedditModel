import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = ({ setIsLoggedIn }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:5000/login', {
                username,
                password,
            });
            if (response.data.success) {
                setIsLoggedIn(true);
                navigate('/');
            } else {
                console.log(response.data);
                alert('Login failed');
            }
        } catch (error) {
            console.error('Error during login', error);
        }
    };

    return (
        <div className="container mt-5">
            <form onSubmit={handleLogin} className="border p-4 rounded bg-light">
                <h2 className="text-center mb-4">Login</h2>
                <div className="form-group">
                    <input
                        type="text"
                        className="form-control"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Username"
                        required
                    />
                </div>
                <div className="form-group">
                    <input
                        type="password"
                        className="form-control"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        required
                    />
                </div>
                <button type="submit" className="text-center btn btn-primary btn-block">Login</button>
            </form>
        </div>
    );
};

export default Login;
