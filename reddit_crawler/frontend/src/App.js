import React, {useState, useEffect} from 'react';
import {BrowserRouter as Router, Route, Navigate, Routes} from 'react-router-dom';
import axios from 'axios';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from './components/Login';
import StatusDisplay from './components/StatusDisplay';
import SubredditList from './components/SubredditList';
import AddSubreddit from './components/AddSubreddit';
import StartCollection from './components/StartCollection';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('/api/protected', { withCredentials: true })
            .then(response => {
                setIsLoggedIn(true);
            })
            .catch(() => {
                setIsLoggedIn(false);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <Router>
            <div className="App bg-dark text-white min-vh-100 d-flex flex-column" style={{height: '100vh'}}>
                <Routes>
                    <Route path="/api/login" element={<Login setIsLoggedIn={setIsLoggedIn}/>}/>
                    <Route
                        path="/"
                        element={
                            isLoggedIn ? (
                                <>
                                    <h1 className="text-center mb-4 mt-4">Reddit Data Collector</h1>
                                    <div className="d-flex flex-row" style={{flex: 1}}>
                                        <div className="left-pane d-flex flex-column p-3" style={{flex: 1}}>
                                            <StatusDisplay/>
                                            <AddSubreddit/>
                                            <StartCollection/>
                                        </div>
                                        <div className="right-pane p-3" style={{flex: 1}}>
                                            <SubredditList/>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <Navigate to="/api/login"/>
                            )
                        }
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
