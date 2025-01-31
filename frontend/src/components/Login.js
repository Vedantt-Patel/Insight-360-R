import React, { useState } from "react";
import { useAppContext } from "../context/AppContext";
import "../style/Login.css";

const Login = () => {
  const { isDarkMode } = useAppContext();  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form submitted:", { username, password });
  };

  return (
    <div className={`login-container ${isDarkMode ? "dark-mode" : ""}`}>
      <form onSubmit={handleSubmit} className="login-form">
        <h2 className="login-heading">Login</h2>

        <div className="input-group">
          <label className="login-label">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="login-input"
          />
        </div>

        <div className="input-group">
          <label className="login-label">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login-input"
          />
        </div>

        <button type="submit" className="login-button">
          Sign In
        </button>
      </form>
    </div>
  );
};

export default Login;
