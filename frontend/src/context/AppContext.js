// src/context/AppContext.js

import React, { createContext, useState, useContext } from "react";

const AppContext = createContext();

export const AppContextProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [abstractionText, setAbstractionText] = useState("");  // Add this line

  const toggleTheme = () => {
    setIsDarkMode((prev) => !prev);
    document.body.classList.toggle("dark-theme");
  };

  return (
    <AppContext.Provider value={{ isDarkMode, toggleTheme, abstractionText, setAbstractionText }}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the context easily
export const useAppContext = () => {
  return useContext(AppContext);
};
