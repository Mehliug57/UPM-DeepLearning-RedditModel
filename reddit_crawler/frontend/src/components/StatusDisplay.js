import React, {useEffect, useState} from 'react';
import axios from 'axios';

const StatusDisplay = () => {
    const [status, setStatus] = useState('');
    const [currentSubreddit, setCurrentSubreddit] = useState('');
    const [currentlyCollecting, setCurrentlyCollecting] = useState(false);
    const [postLimit, setPostLimit] = useState(5000);

    useEffect(() => {
        const fetchStatus = () => {
            axios.get('/api/status', { withCredentials: true })
                .then(response => {
                    setStatus(response.data.status);
                    setCurrentSubreddit(response.data.current_subreddit);
                    setCurrentlyCollecting(response.data.currently_collecting);
                    setPostLimit(response.data.current_post_limit);
                })
                .catch(error => console.error(error));
        };

        fetchStatus();
        const intervalId = setInterval(fetchStatus, 5000);
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="bg-secondary p-3 rounded mb-4">
            <h2>Status</h2>
            <p>Status: {status}</p>
            <p>Current Subreddit: {currentSubreddit}</p>
            <p>Currently Collecting: {currentlyCollecting ? "Yes" : "No"}</p>
            <p>Post Limit: {postLimit}</p>
        </div>
    );
};

export default StatusDisplay;
