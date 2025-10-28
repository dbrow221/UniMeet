import { Navigate, Outlet } from "react-router-dom";
import { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";

function ProtectedRoute() {
  const [isAuthorized, setIsAuthorized] = useState(null);

  const refreshToken = async () => {
    const refresh = localStorage.getItem(REFRESH_TOKEN);
    if (!refresh) {
      setIsAuthorized(false);
      return;
    }

    try {
      const res = await api.post("/api/token/refresh/", { refresh });
      if (res.status === 200) {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
    } catch (err) {
      console.error("Token refresh failed:", err);
      setIsAuthorized(false);
    }
  };

  const auth = async () => {
    const token = localStorage.getItem(ACCESS_TOKEN);

    // If no token yet, wait for async check
    if (!token) {
      const refresh = localStorage.getItem(REFRESH_TOKEN);
      if (refresh) {
        await refreshToken();
      } else {
        setIsAuthorized(false);
      }
      return;
    }

    try {
      const decoded = jwtDecode(token);
      const now = Date.now() / 1000;
      if (decoded.exp < now) {
        await refreshToken();
      } else {
        setIsAuthorized(true);
      }
    } catch (err) {
      console.error("Token decode failed:", err);
      setIsAuthorized(false);
    }
  };

  useEffect(() => {
    auth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isAuthorized === null) {
    // Show loading state while checking token
    return <div>Checking authorization...</div>;
  }

  return isAuthorized ? <Outlet /> : <Navigate to="/login" replace />;
}

export default ProtectedRoute;
