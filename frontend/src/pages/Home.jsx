import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import api from "../api"; // your Axios instance
import { ACCESS_TOKEN } from "../constants";
import "../styles/Home.css";

function Home() {
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsername = async () => {
      const token = localStorage.getItem(ACCESS_TOKEN);
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const decoded = jwtDecode(token);
        const userId = decoded.user_id;

        // Make API call with Authorization header and trailing slash
        const res = await api.get(`/user/${userId}/`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        setUsername(res.data.username);
      } catch (err) {
        console.error("Failed to fetch username:", err);
        setUsername(""); // fallback
      } finally {
        setLoading(false);
      }
    };

    fetchUsername();
  }, []);

  if (loading) {
    return <div className="home-loading">Loading...</div>;
  }

  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="home-title">
          Welcome {username ? `${username} 👋` : "to UniMeet 🎓"}
        </h1>
        <p className="home-tagline">
          Connect with classmates, discover campus events, and build your community.  
          UniMeet is your hub for meet-ups, events, and everything happening on campus.
        </p>

        <div className="home-buttons">
          <Link to="/events" className="btn btn-light">
            View Events
          </Link>
          <Link to="/create-event" className="btn btn-primary">
            Create Event
          </Link>
        </div>
      </div>

      <footer className="home-footer">
        © {new Date().getFullYear()} UniMeet. All rights reserved.
      </footer>
    </div>
  );
}

export default Home;
