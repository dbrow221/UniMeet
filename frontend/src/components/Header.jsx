// src/components/Header.jsx
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";
import "../styles/Header.css";

function Header() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem(ACCESS_TOKEN);

  const handleLogout = () => {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  return (
    <header className="header">
      <nav className="nav">
        <Link className="nav-logo" to="/">UniMeet</Link>
        <ul className="nav-links">
  <li><Link to="/">Home</Link></li>
  <li><Link to="/map">Campus Map</Link></li>
  <li><Link to="/events">Events</Link></li>
  <li><Link to="/users/search/">Find Friends</Link></li>

  {isLoggedIn ? (
    <>
      <li><Link to="/messages">Messages</Link></li>
      <li><Link to="/profile">Profile</Link></li>
      <li>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </li>
    </>
  ) : (
    <>
      <li><Link to="/login">Login</Link></li>
      <li><Link to="/register">Register</Link></li>
    </>
  )}
</ul>

      </nav>
    </header>
  );
}

export default Header;
