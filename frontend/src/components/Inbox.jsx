import React, { useState, useEffect } from "react";
import api from "../api";
import "../styles/Inbox.css";

export default function Inbox() {
  const [isOpen, setIsOpen] = useState(false);
  const [joinRequests, setJoinRequests] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch requests when the inbox is opened
  useEffect(() => {
    if (isOpen) {
      fetchRequests();
    }
  }, [isOpen]);

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch both join requests and friend requests
      const [joinResponse, friendResponse] = await Promise.all([
        api.get("/api/join-requests/"),
        api.get("/api/friend-requests/received/")
      ]);
      setJoinRequests(joinResponse.data);
      setFriendRequests(friendResponse.data);
    } catch (err) {
      console.error("Error fetching requests:", err);
      setError("Failed to load notifications");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    try {
      await api.post(`/api/join-requests/${requestId}/approve/`);
      // Refresh the list after approval
      fetchRequests();
    } catch (err) {
      console.error("Error approving request:", err);
      alert(err.response?.data?.detail || "Failed to approve request");
    }
  };

  const handleDeny = async (requestId) => {
    try {
      await api.post(`/api/join-requests/${requestId}/deny/`);
      // Refresh the list after denial
      fetchRequests();
    } catch (err) {
      console.error("Error denying request:", err);
      alert(err.response?.data?.detail || "Failed to deny request");
    }
  };

  const handleAcceptFriend = async (requestId) => {
    try {
      await api.patch(`/api/friend-requests/${requestId}/accept/`);
      // Refresh the list after acceptance
      fetchRequests();
    } catch (err) {
      console.error("Error accepting friend request:", err);
      alert(err.response?.data?.detail || "Failed to accept friend request");
    }
  };

  const handleDeclineFriend = async (requestId) => {
    try {
      await api.patch(`/api/friend-requests/${requestId}/decline/`);
      // Refresh the list after declining
      fetchRequests();
    } catch (err) {
      console.error("Error declining friend request:", err);
      alert(err.response?.data?.detail || "Failed to decline friend request");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const totalNotifications = joinRequests.length + friendRequests.length;

  return (
    <>
      {/* Toggle button */}
      <button className="inbox-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? "Close Inbox" : "Inbox"}
        {!isOpen && totalNotifications > 0 && (
          <span className="inbox-badge">{totalNotifications}</span>
        )}
      </button>

      {/* Drawer */}
      <div className={`inbox ${isOpen ? "open" : "closed"}`}>
        <h3>Notifications</h3>
        
        {loading && <p className="inbox-status">Loading...</p>}
        
        {error && <p className="inbox-error">{error}</p>}
        
        {!loading && !error && totalNotifications === 0 && (
          <p className="inbox-empty">No new notifications</p>
        )}
        
        {/* Friend Requests Section */}
        {!loading && !error && friendRequests.length > 0 && (
          <div className="inbox-section">
            <h4 className="inbox-section-title">Friend Requests</h4>
            <ul className="inbox-list">
              {friendRequests.map((request) => (
                <li key={`friend-${request.id}`} className="inbox-item">
                  <div className="inbox-item-header">
                    <strong>{request.from_user_details.username}</strong>
                    <span className="inbox-item-time">
                      {formatDate(request.created_at)}
                    </span>
                  </div>
                  <div className="inbox-item-event">
                    wants to be your friend
                  </div>
                  <div className="inbox-item-actions">
                    <button 
                      className="inbox-btn inbox-btn-approve"
                      onClick={() => handleAcceptFriend(request.id)}
                    >
                      Accept
                    </button>
                    <button 
                      className="inbox-btn inbox-btn-deny"
                      onClick={() => handleDeclineFriend(request.id)}
                    >
                      Decline
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Join Requests Section */}
        {!loading && !error && joinRequests.length > 0 && (
          <div className="inbox-section">
            <h4 className="inbox-section-title">Event Join Requests</h4>
            <ul className="inbox-list">
              {joinRequests.map((request) => (
                <li key={`join-${request.id}`} className="inbox-item">
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
          </div>
        )}
      </div>
    </>
  );
}
