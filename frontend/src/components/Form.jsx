import React, { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/FormStyles.css";
import LoadingIndicator from "../components/LoadingIndicator";

function Form({ route, method }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrorMessage(""); // clear old errors
        try {
            const res = await api.post(route, { username, password });
            if (method === "login") {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
                navigate("/");
            } else {
                navigate("/login");
            }
        } catch (error) {
            if (error.response) {
                // Server responded with status code outside 2xx
                if (error.response.status === 400) {
                    setErrorMessage("Invalid input. Please check your username and password.");
                } else if (error.response.status === 401) {
                    setErrorMessage("Incorrect username or password.");
                } else if (error.response.status === 409) {
                    setErrorMessage("That username is already taken.");
                } else {
                    setErrorMessage("Something went wrong. Please try again later.");
                }
            } else if (error.request) {
                // Request made but no response
                setErrorMessage("No response from server. Please check your connection.");
            } else {
                // Something else happened
                setErrorMessage("An unexpected error occurred.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>{method === "login" ? "Login" : "Register"}</h1>
            <input
                className="form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            {loading && <LoadingIndicator />}
            {errorMessage && <p className="error-text">{errorMessage}</p>}
            <button className="form-button" type="submit" disabled={loading}>
                {method === "login" ? "Login" : "Register"}
            </button>
        </form>
    );
}

export default Form;
