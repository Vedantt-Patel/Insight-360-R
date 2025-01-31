import React from "react";
import { Routes, Route } from "react-router-dom";
import { AppContextProvider } from "./context/AppContext"; 
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import About from "./components/About";
// import DownloadImg from './components/DownloadImg'; 
// import DownloadButton from "./components/DownloadButton"; 

const App = () => {
  return (
    <AppContextProvider>
      <Navbar />
      {/* <DownloadImg></DownloadImg> */}
      {/* <DownloadButton></DownloadButton> */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/about" element={<About />} />
        {/* <Route path="/download" element={<DownloadImg />} />  */}
      </Routes>
      {/* <MermaidChart /> */}
    </AppContextProvider>
  );
};

export default App;
