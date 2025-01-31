// src/components/Navbar.js

import React from "react";
import { Link } from "react-router-dom";
import { useAppContext } from "../context/AppContext";  
import "../style/Navbar.css";  
import HomeIcon from "@mui/icons-material/Home";
import LoginIcon from "@mui/icons-material/ExitToApp";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import InfoIcon from "@mui/icons-material/Info";
import WbSunnyIcon from "@mui/icons-material/WbSunny";
import DarkModeIcon from "@mui/icons-material/DarkMode";

const Navbar = () => {
  const { isDarkMode, toggleTheme } = useAppContext();

  return (
    <nav className={`navbar ${isDarkMode ? "dark" : "light"}`}>
      <ul className="navbar__menu">
        <li className="navbar__item navbar__title">
          <Link to="/">
            <h1>JustLearn</h1>
          </Link>
        </li>
        <li className="navbar__item">
          <Link to="/" className="navbar__link">
            <HomeIcon />
            <span>Home</span>
          </Link>
        </li>
        <li className="navbar__item">
          <Link to="/login" className="navbar__link">
            <LoginIcon />
            <span>Login</span>
          </Link>
        </li>
        <li className="navbar__item">
          <Link to="/signup" className="navbar__link">
            <PersonAddIcon />
            <span>SignUp</span>
          </Link>
        </li>
        <li className="navbar__item">
          <Link to="/about" className="navbar__link">
            <InfoIcon />
            <span>About</span>
          </Link>
        </li>
        <li className="navbar__item navbar__theme-toggle" onClick={toggleTheme}>
          {isDarkMode ? <DarkModeIcon /> : <WbSunnyIcon />}
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
