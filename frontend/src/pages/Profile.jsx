<<<<<<< HEAD
import React, { useEffect, useState, useMemo } from "react";
import { ACCESS_TOKEN } from "../constants";
import "../styles/Profile.css";

function Profile() {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    user: { username: "", password: "" },
    bio: "",
    location: "",
    pronouns: "",
    notifications_enabled: true,
  });

  const token = localStorage.getItem(ACCESS_TOKEN);

  // Fetch profile info from backend assuming token exists
  useEffect(() => {
    if (!token) return;

    fetch("http://127.0.0.1:8000/api/profile/", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch profile");
        return res.json();
      })
      .then((data) => {
        setProfile(data);
        setFormData({
          user: { username: data.username || "", password: "" },
          bio: data.bio || "",
          location: data.location || "",
          pronouns: data.pronouns || "",
          notifications_enabled: !!data.notifications_enabled,
        });
      })
      .catch((err) => console.error("ERROR LOADING PROFILE:", err));
  }, [token]);

  // Handle form field changes when editing
  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    if (name.startsWith("user.")) {
      const field = name.split(".")[1];
      setFormData((prev) => ({
        ...prev,
        user: { ...prev.user, [field]: value },
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
    }
  };

  // If any field is changed, mark as "dirty" to enable save
  const isDirty = useMemo(() => {
    if (!profile) return false;

    // Check nested user fields for changes
    if (
      formData.user.username !== profile.username ||
      formData.user.password.trim() !== "" ||
      formData.bio !== (profile.bio || "") ||
      formData.location !== (profile.location || "") ||
      formData.pronouns !== (profile.pronouns || "") ||
      formData.notifications_enabled !== !!profile.notifications_enabled
    ) {
      return true;
    }
    return false;
  }, [formData, profile]);

  // Handle saving changes to backend
  const handleSave = () => {
    const payload = {};

    // Check nested user fields for changes
    const usernameChanged = formData.user.username !== profile.username;
    const passwordChanged = formData.user.password.trim() !== "";

    // Only include changed fields in payload
    if (usernameChanged || passwordChanged) {
      payload.user = {};
      if (usernameChanged) payload.user.username = formData.user.username;
      if (passwordChanged) payload.user.password = formData.user.password;
    }

    // Check other profile fields for changes
    ["bio", "location", "pronouns", "notifications_enabled"].forEach(
      (field) => {
        if (formData[field] !== profile[field]) {
          payload[field] = formData[field];
        }
      }
    );

    // If nothing changed, just exit
    if (Object.keys(payload).length === 0) {
      alert("No changes detected.");
      setEditing(false);
      return;
    }

    // Send update request to backend
    fetch("http://127.0.0.1:8000/api/profile/", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to update profile");
        return res.json();
      })
      .then((updated) => {
        // If username or password changed, log out with alert
        if (usernameChanged || passwordChanged) {
          alert("Your username or password has been changed. Please log in again.");
          localStorage.removeItem(ACCESS_TOKEN);
          window.location.href = "/login";
          return;
        }

        // Update local profile state and exit edit mode
        setProfile(updated);
        setFormData((prev) => ({ ...prev, user: { ...prev.user, password: "" } }));
        setEditing(false);
      })
      .catch((err) => console.error("Error updating profile:", err));
  };

  /* Render loading state if profile not yet fetched 
  SHOULD NOT LAST LONG, INDICATIVE OF POSSIBLE ERROR */
  if (!profile) return <p>Loading profile...</p>;

  return (
    <div className="profile-wrapper">
      <h1>Profile Settings</h1>

      {editing ? (
        <div className="profile-edit">
          <h2>Account Info</h2>
          <div className="profile-field">
            <label>Username:</label>
            <input
              name="user.username"
              value={formData.user?.username || ""}
              onChange={handleChange}
            />
          </div>

          <div className="profile-field">
            <label>Password:</label>
            <input
              type="password"
              name="user.password"
              value={formData.user?.password || ""}
              onChange={handleChange}
              placeholder="Enter new password"
            />
          </div>

          <h2>Profile Info</h2>
          <div className="profile-field">
            <label>Bio:</label>
            <textarea name="bio" value={formData.bio} onChange={handleChange} />
          </div>

          <div className="profile-field">
            <label>Location:</label>
            <input
              name="location"
              value={formData.location}
              onChange={handleChange}
            />
          </div>

          <div className="profile-field">
            <label>Pronouns:</label>
            <input
              name="pronouns"
              value={formData.pronouns}
              onChange={handleChange}
            />
          </div>

          <div className="profile-field">
            <label>
              Notifications Enabled:
              <input
                type="checkbox"
                name="notifications_enabled"
                checked={formData.notifications_enabled}
                onChange={handleChange}
              />
            </label>
          </div>

          <div className="profile-actions">
            <button onClick={handleSave}>Save</button>
            <button onClick={() => setEditing(false)}>Cancel</button>
          </div>
        </div>
      ) : (
        <div className="profile-view">
          <p><strong>Username:</strong> {profile.username}</p>
          <p><strong>Bio:</strong> {profile.bio || "No bio set"}</p>
          <p><strong>Location:</strong> {profile.location || "No location set"}</p>
          <p><strong>Pronouns:</strong> {profile.pronouns || "Not specified"}</p>
          <p><strong>Notifications:</strong> {profile.notifications_enabled ? "Enabled" : "Disabled"}</p>

          <button onClick={() => setEditing(true)}>Edit Profile</button>
        </div>
      )}
    </div>
  );
}
=======
import React, { useEffect, useState } from "react";
import { ACCESS_TOKEN } from "../constants";
import { jwtDecode } from "jwt-decode";
import "../styles/Profile.css";

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch current user info from token
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const decoded = jwtDecode(token);
      // decoded typically has user_id, username, etc.
      setUser({
        id: decoded.user_id,
        username: decoded.username
      });
    } catch (err) {
      console.error("Failed to decode token:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) return <p>Loading profile...</p>;
  if (!user) return <p>No user logged in.</p>;

  return (
    <div className="profile-wrapper">
      <h1>Profile</h1>
      <div className="profile-card">
        <p>
          <strong>Username:</strong> {user.username}
        </p>

        {/* Example future button for editing profile */}
        <button className="edit-profile-btn">Edit Profile</button>
      </div>
    </div>
  );
};
>>>>>>> 6466b375c94b4c0bc258cf50ed19f1a9398ac15e

export default Profile;
