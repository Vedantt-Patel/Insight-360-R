import React, { useState } from "react";
import { useAppContext } from "../context/AppContext";
import "../style/SignUp.css";

const SignUp = () => {
  const { isDarkMode } = useAppContext();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form submitted:", { fullName, email, password });
  };

  return (
    <div className={`signup-container ${isDarkMode ? "dark-mode" : ""}`}>
      <form onSubmit={handleSubmit} className="signup-form">
        <h2 className="signup-heading">Register</h2>

        <div className="input-group">
          <label className="signup-label">Full Name</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="signup-input"
          />
        </div>

        <div className="input-group">
          <label className="signup-label">E-mail</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="signup-input"
          />
        </div>

        <div className="input-group">
          <label className="signup-label">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="signup-input"
          />
        </div>

        <button type="submit" className="signup-button">
          Sign Up
        </button>
      </form>
    </div>
  );
};

export default SignUp;
