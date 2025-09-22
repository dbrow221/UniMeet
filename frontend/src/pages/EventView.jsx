import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/EventView.css";
import L from "leaflet";

// Import marker images directly
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { ACCESS_TOKEN } from "../constants";

// Fix default Leaflet marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const EventView = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const token = localStorage.getItem("token"); // optional JWT
        const headers = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = `Bearer ${ACCESS_TOKEN}`;

        const response = await fetch("http://127.0.0.1:8000/api/events/", { headers });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const publicEvents = data.filter((event) => event.is_public);
        setEvents(publicEvents);
      } catch (err) {
        console.error("Error fetching events:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  if (loading) return <p>Loading events...</p>;
  if (events.length === 0) return <p>No public events available.</p>;

  return (
    <div className="events-wrapper">
      <h1>Public Events</h1>
      <ul className="events-list">
        {events.map((event) => (
          <li key={event.id} className="event-item">
            <h2>{event.name}</h2>
            <p>
              📍 Location: <b>{event.location_details?.name || "Unknown"}</b>
            </p>
            <p>🗓 Posted: {new Date(event.posted_date).toLocaleDateString()}</p>
            <p>👤 Host: {event.host?.username || "Unknown"}</p>
            <p>{event.details}</p>

            {/* Mini map */}
            {event.location_details?.latitude && event.location_details?.longitude && (
              <MapContainer
                center={[event.location_details.latitude, event.location_details.longitude]}
                zoom={16}
                scrollWheelZoom={false}
                className="event-mini-map"
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />
                <Marker position={[event.location_details.latitude, event.location_details.longitude]}>
                  <Popup>{event.location_details.name}</Popup>
                </Marker>
              </MapContainer>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EventView;
