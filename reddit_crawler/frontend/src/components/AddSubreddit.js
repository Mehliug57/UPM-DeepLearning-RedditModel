import React, { useState } from 'react';
import axios from 'axios';

const AddSubreddit = () => {
    const [subredditName, setSubredditName] = useState('');

    const handleAddSubreddit = () => {
        if (subredditName !== '') {
            axios.get(`http://127.0.0.1:5000/add_subreddit/${subredditName}`)
                .then(response => {
                    alert(response.data);
                    setSubredditName('');
                })
                .catch(error => console.error(error));
        } else {
            alert('Please enter a subreddit name.');
        }
    };

    return (
        <div>
            <h2>Add Subreddit</h2>
            <input
                type="text"
                value={subredditName}
                onChange={e => setSubredditName(e.target.value)}
                placeholder="Enter subreddit name"
            />
            <button onClick={handleAddSubreddit}>Add Subreddit</button>
        </div>
    );
};

export default AddSubreddit;
