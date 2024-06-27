import React from 'react';
import { Link } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
    return (
        <div className="nav-bar">
            <h2>CBVIS</h2>
            <nav>
                <ul>
                    <li><Link to="/">Home</Link></li>
                    <li><Link to="/dashboard/table">Data Dashboard</Link></li>
                    <li><Link to="/account">Account</Link></li>
                </ul>
            </nav>
        </div>
    );
}

export default NavBar;
