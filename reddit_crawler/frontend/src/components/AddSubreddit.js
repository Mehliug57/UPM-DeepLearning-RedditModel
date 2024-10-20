import React, { useState } from 'react';
import axios from 'axios';

const AddSubreddit = () => {
    const [subredditName, setSubredditName] = useState('');

    const handleAddSubreddit = () => {
        if (subredditName !== '') {
            axios.post('http://127.0.0.1:5000/add_subreddit', { subreddit_name: subredditName }, { withCredentials: true })
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
        <div className="bg-secondary p-3 rounded mb-4">
            <h2>Add Subreddit</h2>
            <div className="form-group mb-3">
                <input
                    type="text"
                    value={subredditName}
                    onChange={e => setSubredditName(e.target.value)}
                    placeholder="Enter subreddit name"
                    className="form-control"
                />
            </div>
            <button onClick={handleAddSubreddit} className="btn btn-primary">Add Subreddit</button>
        </div>
    );
};

export default AddSubreddit;
