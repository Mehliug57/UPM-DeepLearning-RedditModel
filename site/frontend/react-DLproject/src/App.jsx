import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import 'bootstrap/dist/css/bootstrap.min.css';
import {React, useState,useEffect} from 'react';
import axios from "axios";
import "./App.css"



function Footer() {
  return (
    <footer className="footer">
      <p>© 2025 Reddit Helper. All Rights Reserved.</p>
    </footer>
  );
}
const getCardStyle = (confidence) => {
  if (confidence >= 0.5) {
    return { backgroundColor: "#d4edda", color: "#155724" }; // Verde chiaro
  } else if (confidence >= 0.3) {
    return { backgroundColor: "#fff3cd", color: "#856404" }; // Giallo
  } else {
    return { backgroundColor: "#f8d7da", color: "#721c24" }; // Rosso chiaro
  }
};
const navbar = {backgroundColor: '#F16E10'};
const brandStyle = {
  color: 'white', // Colore del testo (bianco)
  marginLeft: '10px',
};
function App() {
  const [title,setTitle]= useState(true);
  const [subreddits, setSubreddits] = useState("");
  const [request,setRequest] =useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log("prima");
      const res = await axios.post('http://127.0.0.1:5000/predict', { title:request, });
      console.log("dopo");
      setSubreddits(res.data.predicted_subreddits);
      console.log(res.data.predicted_subreddits);
    } catch (error) {
      console.error("Error communicating with the backend:", error);
    }
  };
  return (
    <div>
    <Navbar style={navbar} >
        <Navbar.Brand className="custom-brand" style={brandStyle}>Reddit helper🔎</Navbar.Brand>
    </Navbar>
    {title && <Container><h1 className="title">Welcome! Insert the title of your post to continue...</h1></Container>}
    {!title && <Container><h1 className="title">These are the best subreddits to publish your post! </h1></Container>}
    <Container
        className="d-flex justify-content-center align-items-center"
        style={{ height: "50vh" }}>
        <Form className="d-flex" style={{ width: "50%" }} onSubmit={handleSubmit}>
          <Form.Control
            type="text"
            placeholder="Insert your title here..."
            className="me-2"
            aria-label="Search"
            onChange={(e) => setRequest(e.target.value)}
          />
          <Button  variant="primary" type="submit" onClick={()=>{setTitle(false)}}>🔎</Button>
        </Form>
      </Container>
      <Container>
        {subreddits !== "" && subreddits.length > 0 && (
          subreddits.slice(0, 3).map((sub, index) => (
            <Card key={index} className="mb-3" style={getCardStyle(sub.confidence)}>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <Card.Title className="mb-0">r/{sub.subreddit}</Card.Title>
                  <span className="confidence-text">
                    {(sub.confidence * 100).toFixed(2)}%
                  </span>
                </div>
              </Card.Body>
            </Card>
          ))
        )}
      </Container>
      <Footer/>
    </div>
  )
}

export default App
