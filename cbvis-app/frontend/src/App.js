import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NavBar from './components/NavBar';
import HomePage from './components/HomePage';
import AccountPage from './components/AccountPage';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
    return (
        <Router>
            <div className="container">
                <NavBar />
                <div className="content">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/account" element={<AccountPage />} />
                        <Route path="/dashboard/*" element={<Dashboard />} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;
