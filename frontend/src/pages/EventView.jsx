import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/EventView.css";
import L from "leaflet";
import { jwtDecode } from "jwt-decode";
import { ACCESS_TOKEN } from "../constants";
import { useNavigate } from "react-router-dom";
import api from "../api";

// Leaflet marker setup
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const EventView = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentID, setCurrentID] = useState(null);
  const [expandedEventId, setExpandedEventId] = useState(null);
  const [comments, setComments] = useState({});
  const [newComment, setNewComment] = useState({});
  const [loadingComments, setLoadingComments] = useState({});
  const navigate = useNavigate();

  const fetchEvents = async () => {
    try {
      const token = localStorage.getItem(ACCESS_TOKEN);
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const response = await fetch("http://127.0.0.1:8000/api/events/", { headers });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      setEvents(data);
    } catch (err) {
      console.error("Error fetching events:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async (eventId) => {
    if (loadingComments[eventId]) return;
    
    setLoadingComments(prev => ({ ...prev, [eventId]: true }));
    try {
      const response = await api.get(`/api/events/${eventId}/comments/`);
      setComments(prev => ({ ...prev, [eventId]: response.data }));
    } catch (err) {
      console.error("Error fetching comments:", err);
    } finally {
      setLoadingComments(prev => ({ ...prev, [eventId]: false }));
    }
  };

  const handlePostComment = async (eventId) => {
    const commentText = newComment[eventId]?.trim();
    if (!commentText) return;

    try {
      const response = await api.post(`/api/events/${eventId}/comments/`, {
        text: commentText,
        event: eventId
      });
      
      // Add new comment to the list
      setComments(prev => ({
        ...prev,
        [eventId]: [...(prev[eventId] || []), response.data]
      }));
      
      // Clear input
      setNewComment(prev => ({ ...prev, [eventId]: "" }));
    } catch (err) {
      console.error("Error posting comment:", err);
      alert("Failed to post comment");
    }
  };

  const toggleExpand = (eventId, isHost, hasJoined) => {
    // Only allow expansion if user is host or participant
    if (!isHost && !hasJoined) {
      return; // Don't expand for non-participants
    }

    if (expandedEventId === eventId) {
      setExpandedEventId(null);
    } else {
      setExpandedEventId(eventId);
      // Fetch comments when expanding
      if (!comments[eventId]) {
        fetchComments(eventId);
      }
      // Set up polling for real-time updates
      const interval = setInterval(() => {
        if (expandedEventId === eventId) {
          fetchComments(eventId);
        }
      }, 5000); // Poll every 5 seconds
      
      return () => clearInterval(interval);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setCurrentID(Number(decoded.user_id));
      } catch (err) {
        console.error("Failed to decode token:", err);
      }
    }
    fetchEvents();
  }, []);

  // Set up real-time comment polling for expanded event
  useEffect(() => {
    if (expandedEventId) {
      const interval = setInterval(() => {
        fetchComments(expandedEventId);
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [expandedEventId]);

  const handleDelete = async (eventId) => {
    if (!window.confirm("Are you sure you want to delete this event?")) return;
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) return alert("You must be logged in to delete events.");

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/events/delete/${eventId}/`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        await fetchEvents();
        alert("Event deleted successfully!");
      } else {
        const errorData = await res.json();
        console.error("Delete failed:", errorData);
        alert("Failed to delete event.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("An error occurred while deleting the event.");
    }
  };

  const handleJoin = async (event) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) return alert("You must be logged in to join events.");

    try {
      const url = event.is_public
        ? `http://127.0.0.1:8000/api/events/${event.id}/join/`
        : `http://127.0.0.1:8000/api/events/${event.id}/request-join/`;

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        alert(event.is_public ? "Joined event!" : "Request sent!");
        fetchEvents();
      } else {
        console.error("Join failed:", data);
        alert("Failed to join event.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("An error occurred while joining the event.");
    }
  };

  const handleLeave = async (eventId) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) return alert("You must be logged in to leave events.");

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/events/${eventId}/leave/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        alert("Left event successfully!");
        fetchEvents();
      } else {
        console.error("Leave failed:", data);
        alert("Failed to leave event.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("An error occurred while leaving the event.");
    }
  };

  const handleEdit = (eventId) => {
    navigate(`/events/edit/${eventId}`);
  };

  if (loading) return <p>Loading events...</p>;
  if (events.length === 0) return <p>No events available.</p>;

  return (
    <div className="events-wrapper">
      <h1>Events</h1>
      <ul className="events-list">
        {events.map((event) => {
          const isHost = currentID && event.host_details?.id === currentID;
          const hasJoined = event.participant_list?.some(p => p.id === currentID);
          const isExpanded = expandedEventId === event.id;
          const eventComments = comments[event.id] || [];

          return (
            <li key={event.id} className={`event-item ${event.is_public ? "public" : "private"} ${isExpanded ? "expanded" : ""}`}>
              <div className="event-header" onClick={() => toggleExpand(event.id, isHost, hasJoined)}>
                <h2>
                  {event.name}
                  <span className={`event-badge ${event.is_public ? "public" : "private"}`}>
                    {event.is_public ? "Public" : "Private"}
                  </span>
                  {event.is_expired && (
                    <span className="event-badge expired">
                      Expired
                    </span>
                  )}
                </h2>
                <span className="expand-icon">{isExpanded ? "▼" : "▶"}</span>
              </div>

              <div className="event-summary">
                <p>📍 Location: <b>{event.location_details?.name || "Unknown"}</b></p>
                <p>🗓 Posted: {new Date(event.posted_date).toLocaleDateString()}</p>
                <p>🕒 Start: {new Date(event.start_time).toLocaleString()}</p>
                <p>🕒 End: {new Date(event.end_time).toLocaleString()}</p>
                <p>👤 Host: {event.host_details?.username || "Unknown"}</p>
                <p>👥 Participants: {event.participant_list?.length || 0} / {event.max_capacity}</p>
                <p>{event.details}</p>

                {event.location_details?.latitude && event.location_details?.longitude && (
                  <MapContainer
                    center={[event.location_details.latitude, event.location_details.longitude]}
                    zoom={16}
                    scrollWheelZoom={false}
                    className="event-mini-map"
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; OpenStreetMap contributors'
                    />
                    <Marker position={[event.location_details.latitude, event.location_details.longitude]}>
                      <Popup>{event.location_details.name}</Popup>
                    </Marker>
                  </MapContainer>
                )}

                <div className="event-actions">
                  {!isHost && !hasJoined && (
                    <button onClick={() => handleJoin(event)} className="join-event-btn">
                      {event.is_public ? "Join Event" : "Request to Join"}
                    </button>
                  )}

                  {!isHost && hasJoined && (
                    <button onClick={() => handleLeave(event.id)} className="leave-event-btn">
                      Leave Event
                    </button>
                  )}

                  {isHost && (
                    <>
                      <button onClick={() => handleEdit(event.id)} className="edit-event-btn">
                        Edit Event
                      </button>
                      <button onClick={() => handleDelete(event.id)} className="delete-event-btn">
                        Delete Event
                      </button>
                    </>
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="event-expanded">
                  <div className="participants-section">
                    <h3>Participants ({event.participant_list?.length || 0})</h3>
                    {event.participant_list && event.participant_list.length > 0 ? (
                      <ul className="participants-list">
                        {event.participant_list.map(participant => (
                          <li key={participant.id} className="participant-item">
                            <span className="participant-icon">👤</span>
                            <span className="participant-name">{participant.username}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="no-participants">No participants yet</p>
                    )}
                  </div>

                  <div className="comments-section">
                    <h3>Comments</h3>
                    <div className="comments-list">
                      {loadingComments[event.id] && eventComments.length === 0 ? (
                        <p className="loading-comments">Loading comments...</p>
                      ) : eventComments.length > 0 ? (
                        eventComments.map(comment => (
                          <div key={comment.id} className="comment-item">
                            <div className="comment-header">
                              <strong>{comment.user_details.username}</strong>
                              <span className="comment-time">
                                {new Date(comment.created_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="comment-text">{comment.text}</p>
                          </div>
                        ))
                      ) : (
                        <p className="no-comments">No comments yet. Be the first to comment!</p>
                      )}
                    </div>

                    <div className="comment-input-section">
                      <textarea
                        className="comment-input"
                        placeholder="Write a comment..."
                        value={newComment[event.id] || ""}
                        onChange={(e) => setNewComment(prev => ({ ...prev, [event.id]: e.target.value }))}
                        rows={3}
                      />
                      <button 
                        className="comment-submit-btn"
                        onClick={() => handlePostComment(event.id)}
                        disabled={!newComment[event.id]?.trim()}
                      >
                        Post Comment
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default EventView;
