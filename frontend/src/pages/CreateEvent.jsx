// frontend/src/components/CreateEvent.jsx
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import "../styles/CreateEvent.css";
import { ACCESS_TOKEN } from "../constants";

const CreateEvent = () => {
  const { state } = useLocation();
  const location = state?.location; // location object from CampusMap
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [details, setDetails] = useState("");
  const [isPublic, setIsPublic] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!location) {
      alert("Please select a location first.");
      return;
    }

    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      alert("You must be logged in to create an event.");
      return;
    }

    // Decode JWT to get user ID
    let hostId;
    try {
      const decoded = jwtDecode(token);
      hostId = decoded.user_id; // ensure backend token has user_id
    } catch (err) {
      console.error("Failed to decode token:", err);
      alert("Cannot determine current user. Please log in again.");
      return;
    }

    try {
      let locationId = location.id;

      // If location has no ID, create it first
      if (!locationId) {
        const locRes = await fetch(
          "http://127.0.0.1:8000/api/locations/create/",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              name: location.name,
              latitude: location.latitude,
              longitude: location.longitude,
            }),
          }
        );

        // Safely parse response
        let locData;
        try {
          locData = await locRes.json();
        } catch {
          const text = await locRes.text();
          console.error("Location API returned invalid JSON:", text);
          alert("Failed to create location. See console for details.");
          return;
        }

        if (!locRes.ok) {
          console.error("Location creation failed:", locData);
          alert("Failed to create location. See console for details.");
          return;
        }

        locationId = locData.id;
      }

      // Create the event using location ID
      const eventPayload = {
  name,
  details,
  is_public: isPublic,
  host_id: hostId,       // 👈 changed from host → host_id
  location_id: locationId, // 👈 changed from location → location_id
};

      const eventRes = await fetch("http://127.0.0.1:8000/api/events/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(eventPayload),
      });

      // Safely parse event response
      let eventData;
      try {
        eventData = await eventRes.json();
      } catch {
        const text = await eventRes.text();
        console.error("Event API returned invalid JSON:", text);
        alert("Failed to create event. See console for details.");
        return;
      }

      if (eventRes.ok) {
        alert("Event created successfully!");
        navigate("/"); // redirect to home or event list
      } else {
        console.error("Event creation failed:", eventData);
        alert("Failed to create event. See console for details.");
      }
    } catch (err) {
      console.error("Network or server error:", err);
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <div className="create-event">
      <h1>Create Event</h1>

      {location ? (
        <p>
          📍 Location: <b>{location.name}</b> (
          {location.latitude?.toFixed(5)}, {location.longitude?.toFixed(5)})
        </p>
      ) : (
        <p style={{ color: "red" }}>No location selected!</p>
      )}

      <form onSubmit={handleSubmit} className="event-form">
        <div>
          <label>Event Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Details:</label>
          <textarea
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            required
          />
        </div>

        <div>
          <label>
            Public Event:
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
            />
          </label>
        </div>

        <button type="submit" disabled={!location}>
          Create Event
        </button>
      </form>
    </div>
  );
};

export default CreateEvent;
