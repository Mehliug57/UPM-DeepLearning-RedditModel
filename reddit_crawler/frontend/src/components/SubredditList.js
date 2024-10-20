import React, {useEffect, useState} from 'react';
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
        <div className="bg-secondary p-3 rounded mb-4">
            <h2>Subreddits</h2>
            <ul className="list-unstyled">
                {subreddits.map(subreddit => (
                    <li key={subreddit.name} className="py-2">
                        <span className="font-weight-bold">{subreddit.name}</span> - Collected
                        Posts: {subreddit.collected_posts}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default SubredditList;
