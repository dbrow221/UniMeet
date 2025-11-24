import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/Inbox.css";

export default function Inbox() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [joinRequests, setJoinRequests] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [unreadMessages, setUnreadMessages] = useState([]);
  const [notifications, setNotifications] = useState([]);
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
      // Fetch join requests, friend requests, unread messages, and notifications
      const [joinResponse, friendResponse, messagesResponse, notificationsResponse] = await Promise.all([
        api.get("/api/join-requests/"),
        api.get("/api/friend-requests/received/"),
        api.get("/api/messages/conversations/"),
        api.get("/api/notifications/")
      ]);
      setJoinRequests(joinResponse.data);
      setFriendRequests(friendResponse.data);
      
      // Filter conversations with unread messages
      const unread = messagesResponse.data.filter(conv => conv.unread_count > 0);
      setUnreadMessages(unread);
      
      // Filter unread notifications
      const unreadNotifications = notificationsResponse.data.filter(notif => !notif.is_read);
      setNotifications(unreadNotifications);
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

  const handleMarkNotificationRead = async (notificationId) => {
    try {
      await api.post(`/api/notifications/${notificationId}/mark-read/`);
      // Refresh the list after marking as read
      fetchRequests();
    } catch (err) {
      console.error("Error marking notification as read:", err);
    }
  };

  const totalNotifications = joinRequests.length + friendRequests.length + unreadMessages.length + notifications.length;

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
        
        {/* Unread Messages Section */}
        {!loading && !error && unreadMessages.length > 0 && (
          <div className="inbox-section">
            <h4 className="inbox-section-title">New Messages</h4>
            <ul className="inbox-list">
              {unreadMessages.map((conversation) => (
                <li key={`message-${conversation.user.id}`} className="inbox-item">
                  <div className="inbox-item-header">
                    <strong>{conversation.user.username}</strong>
                    <span className="inbox-badge-small">{conversation.unread_count}</span>
                  </div>
                  <div className="inbox-item-event">
                    {conversation.last_message?.content.substring(0, 50)}
                    {conversation.last_message?.content.length > 50 ? '...' : ''}
                  </div>
                  <div className="inbox-item-actions">
                    <button 
                      className="inbox-btn inbox-btn-view"
                      onClick={() => {
                        setIsOpen(false);
                        navigate(`/messages?userId=${conversation.user.id}&username=${conversation.user.username}`);
                      }}
                    >
                      View Message
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Event Reminders Section */}
        {!loading && !error && notifications.length > 0 && (
          <div className="inbox-section">
            <h4 className="inbox-section-title">Event Reminders</h4>
            <ul className="inbox-list">
              {notifications.map((notification) => (
                <li key={`notification-${notification.id}`} className="inbox-item">
                  <div className="inbox-item-header">
                    <strong>Event Reminder</strong>
                    <span className="inbox-item-time">
                      {formatDate(notification.created_at)}
                    </span>
                  </div>
                  <div className="inbox-item-event">
                    {notification.message}
                  </div>
                  <div className="inbox-item-actions">
                    {notification.event && (
                      <button 
                        className="inbox-btn inbox-btn-view"
                        onClick={() => {
                          handleMarkNotificationRead(notification.id);
                          setIsOpen(false);
                          navigate(`/events/${notification.event.id}`);
                        }}
                      >
                        View Event
                      </button>
                    )}
                    <button 
                      className="inbox-btn inbox-btn-deny"
                      onClick={() => handleMarkNotificationRead(notification.id)}
                    >
                      Dismiss
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
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
