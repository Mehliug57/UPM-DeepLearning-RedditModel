import React, {useState} from 'react';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';

const Login = ({setIsLoggedIn}) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/login', {
                username,
                password,
            }, {withCredentials: true});
            if (response.data.success) {
                setIsLoggedIn(true);
                console.log("Logged in: " + response.data.success);
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
        <div className="container d-flex justify-content-center align-items-center" style={{height: '100vh'}}>
            <form onSubmit={handleLogin} className="border p-4 rounded bg-dark text-white" style={{width: '300px'}}>
                <h2 className="text-center mb-4">Login</h2>
                <div className="form-group mb-3">
                    <input
                        type="text"
                        className="form-control"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Username"
                        required
                    />
                </div>
                <div className="form-group mb-3">
                    <input
                        type="password"
                        className="form-control"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary btn-block">Login</button>
            </form>
        </div>
    );
};

export default Login;
