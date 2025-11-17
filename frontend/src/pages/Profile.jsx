import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";
import "../styles/Profile.css";

function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [friends, setFriends] = useState([]);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    user: { username: "", password: "" },
    bio: "",
    location: "",
    pronouns: "",
    notifications_enabled: true,
    profile_picture: "",
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
          profile_picture: data.profile_picture || "",
        });
      })
      .catch((err) => console.error("ERROR LOADING PROFILE:", err));
  }, [token]);

  // Fetch friends list
  useEffect(() => {
    if (!token) return;

    fetch("http://127.0.0.1:8000/api/friends/", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch friends");
        return res.json();
      })
      .then((data) => {
        setFriends(data);
      })
      .catch((err) => console.error("ERROR LOADING FRIENDS:", err));
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
      formData.notifications_enabled !== !!profile.notifications_enabled ||
      formData.profile_picture !== (profile.profile_picture || "")
    ) {
      return true;
    }
    return false;
  }, [formData, profile]);

  // Handle removing a friend
  const handleRemoveFriend = (friendId, friendUsername) => {
    if (!confirm(`Are you sure you want to remove ${friendUsername} from your friends?`)) {
      return;
    }

    fetch(`http://127.0.0.1:8000/api/friends/remove/${friendId}/`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to remove friend");
        return res.json();
      })
      .then(() => {
        // Update friends list by removing the friend
        setFriends((prev) => prev.filter((f) => f.id !== friendId));
        alert("Friend removed successfully.");
      })
      .catch((err) => {
        console.error("Error removing friend:", err);
        alert("Failed to remove friend.");
      });
  };

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
    ["bio", "location", "pronouns", "notifications_enabled", "profile_picture"].forEach(
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

  /* Render loading state if profile not yet fetched */
  if (!profile) return (
    <div className="profile-wrapper">
      <div className="loading-container">
        <p>Loading profile...</p>
      </div>
    </div>
  );

  // Generate initials for default avatar
  const getInitials = (username) => {
    return username ? username.substring(0, 2).toUpperCase() : "??";
  };

  return (
    <div className="profile-wrapper">
      <div className="profile-header">
        <h1>Profile Settings</h1>
      </div>

      {editing ? (
        <div className="profile-edit">
          {/* Profile Picture Section */}
          <div className="profile-picture-section">
            <div className="profile-picture-preview">
              {formData.profile_picture ? (
                <img 
                  src={formData.profile_picture} 
                  alt="Profile" 
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div 
                className="profile-picture-placeholder"
                style={{ display: formData.profile_picture ? 'none' : 'flex' }}
              >
                {getInitials(formData.user.username)}
              </div>
            </div>
            <div className="profile-field">
              <label>Profile Picture URL:</label>
              <input
                name="profile_picture"
                value={formData.profile_picture}
                onChange={handleChange}
                placeholder="https://example.com/your-image.jpg"
              />
              <small className="field-hint">Enter a URL to an image (optional)</small>
            </div>
          </div>

          <div className="section-divider"></div>

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
          <div className="profile-view-header">
            <div className="profile-picture-large">
              {profile.profile_picture ? (
                <img 
                  src={profile.profile_picture} 
                  alt="Profile" 
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div 
                className="profile-picture-placeholder"
                style={{ display: profile.profile_picture ? 'none' : 'flex' }}
              >
                {getInitials(profile.username)}
              </div>
            </div>
            <div className="profile-view-info">
              <h2>{profile.username}</h2>
              {profile.pronouns && (
                <p className="pronouns-badge">{profile.pronouns}</p>
              )}
            </div>
          </div>

          <div className="profile-details-grid">
            <div className="profile-detail-card">
              <div className="detail-label">Bio</div>
              <div className="detail-value">{profile.bio || "No bio set"}</div>
            </div>

            <div className="profile-detail-card">
              <div className="detail-label">Location</div>
              <div className="detail-value">{profile.location || "No location set"}</div>
            </div>

            <div className="profile-detail-card">
              <div className="detail-label">Notifications</div>
              <div className="detail-value">
                <span className={`status-badge ${profile.notifications_enabled ? 'enabled' : 'disabled'}`}>
                  {profile.notifications_enabled ? "Enabled" : "Disabled"}
                </span>
              </div>
            </div>

            <div className="profile-detail-card">
              <div className="detail-label">Friends</div>
              <div className="detail-value">
                <span className="friends-count">{friends.length}</span>
              </div>
            </div>
          </div>

          {/* Friends Section */}
          <div className="friends-section">
            <h3 className="friends-section-title">
              Friends ({friends.length})
            </h3>
            {friends.length === 0 ? (
              <p className="no-friends-message">
                No friends yet. Search for users to send friend requests!
              </p>
            ) : (
              <ul className="friends-list">
                {friends.map((friend) => (
                  <li key={friend.id} className="friend-item">
                    <div 
                      className="friend-clickable"
                      onClick={() => navigate(`/user/${friend.id}`)}
                    >
                      <div className="friend-avatar">
                        {getInitials(friend.username)}
                      </div>
                      <div className="friend-info">
                        <span className="friend-username">{friend.username}</span>
                      </div>
                    </div>
                    <button
                      className="remove-friend-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveFriend(friend.id, friend.username);
                      }}
                      title="Remove friend"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <button className="edit-profile-button" onClick={() => setEditing(true)}>
            <span>✏️</span> Edit Profile
          </button>
        </div>
      )}
    </div>
  );
}

export default Profile;
