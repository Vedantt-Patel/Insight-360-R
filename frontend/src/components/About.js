import React from "react";
import { useAppContext } from "../context/AppContext"; 
import "../style/About.css";

const About = () => {
  const { isDarkMode } = useAppContext(); // Get dark mode status from context
  const teamMembers = [
    {
      name: "Vedant Lavri",
      description: "Leader",
      linkedin: "https://www.linkedin.com/in/vedant-patel-machine-learning/",
      image: "https://randomuser.me/api/portraits/men/1.jpg",
    },
    {
      name: "Mihir Mungara",
      description: "Member",
      linkedin: "https://www.linkedin.com/in/mihir-mungara-929b80273/",
      image: "https://randomuser.me/api/portraits/women/2.jpg",
    },
    {
      name: "Ronit Korat",
      description: "Member",
      linkedin: "https://www.linkedin.com/in/ronit-korat-5a2a59286/",
      image: "https://randomuser.me/api/portraits/men/3.jpg",
    },
    {
      name: "Meet Khanpara",
      description: "Member",
      linkedin: "https://www.linkedin.com/in/khanpara-meet-516024289/",
      image: "https://randomuser.me/api/portraits/women/4.jpg",
    },
    {
      name: "Meet Aghara",
      description: "Member",
      linkedin: "https://www.linkedin.com/in/meet-aghara-52a143255/",
      image: "https://randomuser.me/api/portraits/men/5.jpg",
    },
  ];

  return (
    <div className={`about-container ${isDarkMode ? "dark-mode" : ""}`}>
      {/* <h2 className="about-heading">Meet Our Team</h2> */}
      <div className="cards-container">
        {teamMembers.map((member, index) => (
          <div key={index} className="card">
            <img src={member.image} alt={member.name} className="profile-image" />
            <h3 className="card-name">{member.name}</h3>
            <p className="card-description">{member.description}</p>
            <a
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="linkedin-link"
            >
              LinkedIn
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default About;
