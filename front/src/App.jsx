import {Route, Routes} from "react-router-dom";
import './App.css'
import AuthPage from "./Pages/AuthPage";
import BooksPage from './Pages/BooksPage';
import AddBookPage from './Pages/AddBookPage';

function App() {
  return (
    <>
        <Routes>
            <Route path="/" element={<AuthPage />}/>
            <Route path="/books" element={<BooksPage />} />
            <Route path="/add-book" element={<AddBookPage />} />
        </Routes>
    </>
  )
}

export default App
