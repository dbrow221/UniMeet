import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import "../styles/CreateEvent.css";
import { ACCESS_TOKEN } from "../constants";

const CreateEvent = () => {
  const { state } = useLocation();
  const location = state?.location;
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [details, setDetails] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [startTime, setStartTime] = useState(""); // ISO string
  const [endTime, setEndTime] = useState("");     // ISO string
  const [maxCapacity, setMaxCapacity] = useState(10);

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

    let hostId;
    try {
      const decoded = jwtDecode(token);
      hostId = decoded.user_id;
    } catch (err) {
      console.error("Failed to decode token:", err);
      alert("Cannot determine current user. Please log in again.");
      return;
    }

    try {
      let locationId = location.id;

      // Create location if missing
      if (!locationId) {
        const locRes = await fetch("http://127.0.0.1:8000/api/locations/create/", {
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
        });

        const locData = await locRes.json();
        if (!locRes.ok) {
          console.error("Location creation failed:", locData);
          alert("Failed to create location. See console for details.");
          return;
        }

        locationId = locData.id;
      }

      // Build payload with new fields
      const eventPayload = {
        name,
        details,
        is_public: isPublic,
        host_id: hostId,
        location_id: locationId,
        start_time: startTime || new Date().toISOString(), // default to now if empty
        end_time: endTime || new Date(new Date().getTime() + 60 * 60 * 1000).toISOString(), // +1h default
        max_capacity: maxCapacity,
      };

      const eventRes = await fetch("http://127.0.0.1:8000/api/events/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(eventPayload),
      });

      const eventData = await eventRes.json();
      if (eventRes.ok) {
        alert("Event created successfully!");
        navigate("/"); // redirect
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
          📍 Location: <b>{location.name}</b> ({location.latitude?.toFixed(5)}, {location.longitude?.toFixed(5)})
        </p>
      ) : (
        <p style={{ color: "red" }}>No location selected!</p>
      )}

      <form onSubmit={handleSubmit} className="event-form">
        <div>
          <label>Event Name:</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
        </div>

        <div>
          <label>Details:</label>
          <textarea value={details} onChange={(e) => setDetails(e.target.value)} required />
        </div>

        <div>
          <label>Public Event:</label>
          <input type="checkbox" checked={isPublic} onChange={(e) => setIsPublic(e.target.checked)} />
        </div>

        <div>
          <label>Start Time:</label>
          <input type="datetime-local" value={startTime} onChange={(e) => setStartTime(e.target.value)} required />
        </div>

        <div>
          <label>End Time:</label>
          <input type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} required />
        </div>

        <div>
          <label>Max Capacity:</label>
          <input
            type="number"
            min={1}
            value={maxCapacity}
            onChange={(e) => setMaxCapacity(Number(e.target.value))}
            required
          />
        </div>

        <button type="submit" disabled={!location}>
          Create Event
        </button>
      </form>
    </div>
  );
};

export default CreateEvent;
