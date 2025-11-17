import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/FriendSearch.css";

export default function FriendSearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Dynamic search with debounce
  useEffect(() => {
    const delaySearch = setTimeout(() => {
      if (query.trim()) {
        performSearch(query);
      } else {
        setResults([]);
        setMessage("");
      }
    }, 300); // 300ms debounce

    return () => clearTimeout(delaySearch);
  }, [query]);

  const performSearch = async (searchQuery) => {
    setLoading(true);
    setMessage("");
    try {
      const response = await api.get(`/api/users/search/?q=${encodeURIComponent(searchQuery)}`);
      setResults(response.data);
      if (response.data.length === 0) {
        setMessage("No users found.");
      }
    } catch (err) {
      console.error("Error searching users:", err);
      setMessage("Failed to search users.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const sendFriendRequest = async (userId) => {
    try {
      await api.post(`/api/friend-requests/send/${userId}/`);
      setMessage("Friend request sent successfully!");
      // Remove the user from results after sending request
      setResults((prev) => prev.filter((user) => user.id !== userId));
    } catch (err) {
      console.error("Error sending friend request:", err);
      setMessage(err.response?.data?.detail || "Could not send friend request.");
    }
  };

  const getInitials = (username) => {
    return username ? username.substring(0, 2).toUpperCase() : "??";
  };

  return (
    <div className="friend-search-container">
      <div className="friend-search-header">
        <h2>Find Friends</h2>
        <p className="friend-search-subtitle">Search for users by username to send friend requests</p>
      </div>

      <div className="friend-search-input-wrapper">
        <input
          type="text"
          placeholder="Type a username to search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="friend-search-input"
        />
        {loading && <span className="search-loading-spinner">🔍</span>}
      </div>

      {message && (
        <div className={`friend-search-message ${message.includes("sent") ? "success" : "info"}`}>
          {message}
        </div>
      )}

      {results.length > 0 && (
        <div className="friend-search-results-container">
          <p className="results-count">{results.length} user(s) found</p>
          <ul className="friend-search-results">
            {results.map((user) => (
              <li key={user.id} className="friend-search-item">
                <div 
                  className="user-info-clickable"
                  onClick={() => navigate(`/user/${user.id}`)}
                >
                  <div className="user-avatar">
                    {getInitials(user.username)}
                  </div>
                  <div className="user-details">
                    <span className="user-username">{user.username}</span>
                    {user.email && <span className="user-email">{user.email}</span>}
                  </div>
                </div>
                <button
                  className="add-friend-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    sendFriendRequest(user.id);
                  }}
                >
                  + Add Friend
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
