import React from 'react';
import axios from 'axios';

const StartCollection = () => {
    const handleStartCollection = () => {
        axios.get('http://127.0.0.1:5000/start_collection')
            .then(response => {
                alert(response.data);
            })
            .catch(error => console.error(error));
    };

    return (
        <div>
            <h2>Start Collection</h2>
            <button onClick={handleStartCollection}>Start Collection</button>
        </div>
    );
};

export default StartCollection;
