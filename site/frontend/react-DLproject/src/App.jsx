import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
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
const navbar = {backgroundColor: '#F16E10'};
const brandStyle = {
  color: 'white', // Colore del testo (bianco)
  marginLeft: '10px',
};
function App() {
  const [title,setTitle]= useState(true);
  const [response, setResponse] = useState("");

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/api/process", { title });
      setResponse(res.data.message);
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
        <Form className="d-flex" style={{ width: "50%" }}>
          <Form.Control
            type="search"
            placeholder="Insert your title here..."
            className="me-2"
            aria-label="Search"
          />
          <Button  variant="primary" onClick={()=>{setTitle(false)}}>🔎</Button>
        </Form>
      </Container>
      <Footer/>
    </div>
  )
}

export default App
