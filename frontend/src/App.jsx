import React from 'react';
import { Toaster } from 'react-hot-toast';
import SearchForm from './components/SearchForm';
import './App.css';

function App() {
  return (
    <div className="App">
      <Toaster />
      
      <header className="app-header">
        <h1>Web Crawler</h1>
        <p>Search for products across multiple sources</p>
      </header>

      <main className="app-main">
        <SearchForm />
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI + React</p>
      </footer>
    </div>
  );
}

export default App;