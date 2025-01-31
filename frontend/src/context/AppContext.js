// src/context/AppContext.js

import React, { createContext, useState, useContext } from "react";

const AppContext = createContext();

export const AppContextProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    setIsDarkMode((prev) => !prev);
    document.body.classList.toggle("dark-theme");
  };

  return (
    <AppContext.Provider value={{ isDarkMode, toggleTheme }}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the context easily
export const useAppContext = () => {
  return useContext(AppContext);
};
