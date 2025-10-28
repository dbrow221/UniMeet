import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";
import "../styles/EditEvent.css";

const EditEvent = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [eventData, setEventData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [locations, setLocations] = useState([]); // For location dropdown

  // Fetch event details
  useEffect(() => {
    const fetchEvent = async () => {
      const token = localStorage.getItem(ACCESS_TOKEN);
      if (!token) {
        alert("You must be logged in.");
        navigate("/login");
        return;
      }

      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      try {
        const [eventRes, locRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/events/${id}/`, { headers }),
          fetch(`http://127.0.0.1:8000/api/locations/`, { headers }),
        ]);

        const eventJson = await eventRes.json();
        const locJson = await locRes.json();

        if (eventRes.ok) setEventData(eventJson);
        else alert("Failed to load event details.");

        if (locRes.ok) setLocations(locJson);
        else console.warn("Failed to load locations");
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvent();
  }, [id, navigate]);

  // Format UTC ISO string for datetime-local input
  const formatDateForInput = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    const offset = date.getTimezoneOffset();
    const localDate = new Date(date.getTime() - offset * 60000);
    return localDate.toISOString().slice(0, 16);
  };

  // Convert local datetime-local value back to UTC
  const convertToUTC = (localDateStr) => {
    if (!localDateStr) return null;
    const date = new Date(localDateStr);
    return date.toISOString();
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setEventData({
      ...eventData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) return alert("You must be logged in.");

    const updatedEvent = {
      ...eventData,
      start_time: convertToUTC(eventData.start_time),
      end_time: convertToUTC(eventData.end_time),
      location_id: eventData.location?.id || eventData.location_id || null,
    };

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/events/edit/${id}/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedEvent),
      });

      if (res.ok) {
        alert("Event updated successfully!");
        navigate("/events");
      } else {
        const data = await res.json();
        console.error("Edit failed:", data);
        alert("Failed to update event.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("An error occurred.");
    }
  };

  if (loading) return <p>Loading event...</p>;
  if (!eventData) return <p>Event not found.</p>;

  return (
    <div className="edit-event-wrapper">
      <h1>Edit Event</h1>
      <form onSubmit={handleSubmit} className="edit-event-form">
        <label>
          Name:
          <input
            type="text"
            name="name"
            value={eventData.name || ""}
            onChange={handleChange}
          />
        </label>

        <label>
          Details:
          <textarea
            name="details"
            value={eventData.details || ""}
            onChange={handleChange}
          />
        </label>

        <label>
          Start Time:
          <input
            type="datetime-local"
            name="start_time"
            value={formatDateForInput(eventData.start_time)}
            onChange={handleChange}
          />
        </label>

        <label>
          End Time:
          <input
            type="datetime-local"
            name="end_time"
            value={formatDateForInput(eventData.end_time)}
            onChange={handleChange}
          />
        </label>

        <label>
          Location:
          <select
            name="location_id"
            value={eventData.location?.id || eventData.location_id || ""}
            onChange={(e) =>
              setEventData({
                ...eventData,
                location: { ...eventData.location, id: Number(e.target.value) },
              })
            }
          >
            <option value="">Select a location</option>
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name}
              </option>
            ))}
          </select>
        </label>

        <label className="checkbox-label">
          Public Event?
          <input
            type="checkbox"
            name="is_public"
            checked={eventData.is_public || false}
            onChange={handleChange}
          />
        </label>

        <button type="submit" className="save-event-btn">
          Save Changes
        </button>
      </form>
    </div>
  );
};

export default EditEvent;
