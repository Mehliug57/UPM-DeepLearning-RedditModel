import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SubredditList = () => {
    const [subreddits, setSubreddits] = useState([]);

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/subreddit_list')
            .then(response => {
                setSubreddits(response.data);
            })
            .catch(error => console.error(error));
    }, []);

    return (
        <div>
            <h2>Subreddits</h2>
            <ul>
                {subreddits.map(subreddit => (
                    <li key={subreddit.name}>
                        {subreddit.name} - Collected Posts: {subreddit.collected_posts}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default SubredditList;
