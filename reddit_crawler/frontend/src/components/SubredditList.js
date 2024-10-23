import React, {useEffect, useState} from 'react';
import axios from 'axios';

const SubredditList = () => {
    const [subreddits, setSubreddits] = useState([]);
    const current_post_limit = 100; // Beispiel für das Limit

    useEffect(() => {
        axios.get('/api/subreddit_list', {withCredentials: true})
            .then(response => {
                setSubreddits(response.data);
            })
            .catch(error => console.error(error));
    }, []);

    return (
        <div className="bg-secondary p-3 rounded mb-4" style={{height: '80vh'}}>
            <h2 style={{textAlign: 'center'}}>Subreddits</h2>
            <div style={{maxHeight: '90%', overflowY: 'auto'}}>
                <ul className="list-unstyled" style={{textAlign: 'left', padding: '0 15px'}}>
                    {subreddits.map((subreddit, index) => (
                        <li key={subreddit.name} className="py-2">
                            {index + 1}. <span className="font-weight-bold">{subreddit.name}</span> - ({subreddit.collected_posts}/{subreddit.current_post_limit}) {subreddit.collected_posts >= subreddit.current_post_limit &&
                            <span>✔</span>}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default SubredditList;
