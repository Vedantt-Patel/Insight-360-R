import React, { useEffect } from "react";
import Mermaid from "react-mermaid2";
import { useAppContext } from "../context/AppContext";

const MermaidDiagram = () => {
  const { abstractionText } = useAppContext();

  useEffect(() => {
    // Log when component is mounted (optional debugging)
    console.log("Mermaid component mounted!");
  }, []);

  if (!abstractionText) {
    return <div>Loading...</div>; // Handle case when abstractionText is empty
  }

  return (
    <div>
      <h2>Mermaid Diagram Example</h2>
      {/* Only render Mermaid chart if abstractionText is provided */}
      <Mermaid chart={abstractionText} />
    </div>
  );
};

export default MermaidDiagram;
