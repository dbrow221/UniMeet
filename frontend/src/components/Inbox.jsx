import React, { useState, useEffect } from "react";
import api from "../api";
import "../styles/Inbox.css";

export default function Inbox() {
  const [isOpen, setIsOpen] = useState(false);
  const [joinRequests, setJoinRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch join requests when the inbox is opened
  useEffect(() => {
    if (isOpen) {
      fetchJoinRequests();
    }
  }, [isOpen]);

  const fetchJoinRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get("/api/join-requests/");
      setJoinRequests(response.data);
    } catch (err) {
      console.error("Error fetching join requests:", err);
      setError("Failed to load join requests");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    try {
      await api.post(`/api/join-requests/${requestId}/approve/`);
      // Refresh the list after approval
      fetchJoinRequests();
    } catch (err) {
      console.error("Error approving request:", err);
      alert(err.response?.data?.detail || "Failed to approve request");
    }
  };

  const handleDeny = async (requestId) => {
    try {
      await api.post(`/api/join-requests/${requestId}/deny/`);
      // Refresh the list after denial
      fetchJoinRequests();
    } catch (err) {
      console.error("Error denying request:", err);
      alert(err.response?.data?.detail || "Failed to deny request");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Toggle button */}
      <button className="inbox-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? "Close Inbox" : "Inbox"}
        {!isOpen && joinRequests.length > 0 && (
          <span className="inbox-badge">{joinRequests.length}</span>
        )}
      </button>

      {/* Drawer */}
      <div className={`inbox ${isOpen ? "open" : "closed"}`}>
        <h3>Notifications</h3>
        
        {loading && <p className="inbox-status">Loading...</p>}
        
        {error && <p className="inbox-error">{error}</p>}
        
        {!loading && !error && joinRequests.length === 0 && (
          <p className="inbox-empty">No new notifications</p>
        )}
        
        {!loading && !error && joinRequests.length > 0 && (
          <ul className="inbox-list">
            {joinRequests.map((request) => (
              <li key={request.id} className="inbox-item">
                <div className="inbox-item-header">
                  <strong>{request.user_details.username}</strong>
                  <span className="inbox-item-time">
                    {formatDate(request.created_at)}
                  </span>
                </div>
                <div className="inbox-item-event">
                  wants to join: <strong>{request.event_details.name}</strong>
                </div>
                <div className="inbox-item-actions">
                  <button 
                    className="inbox-btn inbox-btn-approve"
                    onClick={() => handleApprove(request.id)}
                  >
                    Approve
                  </button>
                  <button 
                    className="inbox-btn inbox-btn-deny"
                    onClick={() => handleDeny(request.id)}
                  >
                    Deny
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
