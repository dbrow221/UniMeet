import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/EventView.css";
import L from "leaflet";
import {jwtDecode} from "jwt-decode"; // ✅ correct import
import { ACCESS_TOKEN } from "../constants";

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
  const [currentID, setCurrentID] = useState(null); // ✅ store logged-in username

  const fetchEvents = async () => {
    try {
      const token = localStorage.getItem(ACCESS_TOKEN);
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const response = await fetch("http://127.0.0.1:8000/api/events/", { headers });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      const publicEvents = data.filter((event) => event.is_public);
      setEvents(publicEvents);
    } catch (err) {
      console.error("Error fetching events:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Decode JWT to get current username
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      try {
        const decoded = jwtDecode(token);
        console.log(decoded);
        setCurrentID(Number(decoded.user_id)); // store username
      } catch (err) {
        console.error("Failed to decode token:", err);
      }
    }

    fetchEvents();
  }, []);

  const handleDelete = async (eventId) => {
    if (!window.confirm("Are you sure you want to delete this event?")) return;

    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      alert("You must be logged in to delete events.");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/events/delete/${eventId}/`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        
      });

      if (res.ok) {
        await fetchEvents(); // refresh list
        alert("Event deleted successfully!");
      } else {
        const errorData = await res.json();
        console.error("Delete failed:", errorData);
        alert("Failed to delete event. Check console for details.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("An error occurred while deleting the event.");
    }
  };

  if (loading) return <p>Loading events...</p>;
  if (events.length === 0) return <p>No public events available.</p>;
    
  return (
    <div className="events-wrapper">
      <h1>Public Events</h1>
      <ul className="events-list">
        {events.map((event) => (
          
          <li key={event.id} className="event-item">
            <h2>{event.name}</h2>
            <p>📍 Location: <b>{event.location_details?.name || "Unknown"}</b></p>
            <p>🗓 Posted: {new Date(event.posted_date).toLocaleDateString()}</p>
            <p>👤 Host: {event.host_details?.username || "Unknown"}</p>
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

            
            {/* ✅ Show delete button only if current user is the host */}

           {currentID && event.host_details?.id === currentID && (
              <button
                onClick={() => handleDelete(event.id)}
                className="delete-event-btn"
              >
                
                Delete Event  
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EventView; 
