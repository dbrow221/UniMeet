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

export default Profile;
