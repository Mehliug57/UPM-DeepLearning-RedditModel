import React from 'react';
import axios from 'axios';

const StartCollection = () => {
    const handleStartCollection = () => {
        axios.post('http://127.0.0.1:5000/start_collection', {}, { withCredentials: true })
            .then(response => {
                alert(response.data);
            })
            .catch(error => console.error(error));
    };

    return (
        <div className="bg-secondary p-3 rounded mb-4">
            <h2>Start Collection</h2>
            <button onClick={handleStartCollection} className="btn btn-primary">
                Start Collection
            </button>
        </div>
    );
};

export default StartCollection;
