import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";
import "../styles/Profile.css";

function UserProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const token = localStorage.getItem(ACCESS_TOKEN);

  useEffect(() => {
    if (!token || !userId) return;

    setLoading(true);
    setError(null);

    fetch(`http://127.0.0.1:8000/api/user/${userId}/profile/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch user profile");
        return res.json();
      })
      .then((data) => {
        setProfile(data);
      })
      .catch((err) => {
        console.error("ERROR LOADING USER PROFILE:", err);
        setError("Failed to load profile");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [token, userId]);

  const getInitials = (username) => {
    return username ? username.substring(0, 2).toUpperCase() : "??";
  };

  const handleRemoveFriend = async () => {
    if (!confirm(`Are you sure you want to remove ${profile.username} from your friends?`)) {
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/friends/remove/${userId}/`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error("Failed to remove friend");

      alert("Friend removed successfully.");
      // Refresh profile to update friend status
      window.location.reload();
    } catch (err) {
      console.error("Error removing friend:", err);
      alert("Failed to remove friend.");
    }
  };

  const handleSendFriendRequest = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/friend-requests/send/${userId}/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to send friend request");
      }

      alert("Friend request sent!");
      window.location.reload();
    } catch (err) {
      console.error("Error sending friend request:", err);
      alert(err.message || "Failed to send friend request.");
    }
  };

  if (loading) {
    return (
      <div className="profile-wrapper">
        <div className="loading-container">
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="profile-wrapper">
        <div className="loading-container">
          <p>{error || "Profile not found"}</p>
          <button onClick={() => navigate(-1)}>Go Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-wrapper">
      <div className="profile-header">
        <button onClick={() => navigate(-1)} className="back-button">
          ← Back
        </button>
        <h1>User Profile</h1>
      </div>

      <div className="profile-view">
        <div className="profile-view-header">
          <div className="profile-picture-large">
            {profile.profile_picture ? (
              <img
                src={profile.profile_picture}
                alt="Profile"
                onError={(e) => {
                  e.target.style.display = "none";
                  e.target.nextSibling.style.display = "flex";
                }}
              />
            ) : null}
            <div
              className="profile-picture-placeholder"
              style={{ display: profile.profile_picture ? "none" : "flex" }}
            >
              {getInitials(profile.username)}
            </div>
          </div>
          <div className="profile-view-info">
            <h2>{profile.username}</h2>
            {profile.pronouns && <p className="pronouns-badge">{profile.pronouns}</p>}
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
            <div className="detail-label">Relationship</div>
            <div className="detail-value">
              {profile.is_friend ? (
                <span className="status-badge enabled">Friends</span>
              ) : profile.friend_request_status?.startsWith("sent_pending") ? (
                <span className="status-badge disabled">Request Sent</span>
              ) : profile.friend_request_status?.startsWith("received_pending") ? (
                <span className="status-badge disabled">Request Pending</span>
              ) : (
                <span className="status-badge">Not Friends</span>
              )}
            </div>
          </div>
        </div>

        {/* Action buttons based on friendship status */}
        <div className="profile-actions">
          {profile.is_friend ? (
            <button className="remove-friend-button" onClick={handleRemoveFriend}>
              Remove Friend
            </button>
          ) : profile.friend_request_status?.startsWith("sent_pending") ? (
            <button className="disabled-button" disabled>
              Friend Request Sent
            </button>
          ) : profile.friend_request_status?.startsWith("received_pending") ? (
            <button className="disabled-button" disabled>
              Check Inbox for Request
            </button>
          ) : (
            <button className="add-friend-button" onClick={handleSendFriendRequest}>
              Add Friend
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserProfile;
