import React, { useEffect } from "react";
import Mermaid from "react-mermaid2";

const MermaidDiagram = () => {
  const mermaidCode = `
    graph TD
    subgraph Research Study
        startStart --> problem[Identify Problem: Traditional chatbots fail to provide accurate responses]
        problem --> solution[Propose Solution: RAG-based chatbot]
        solution --> rag[Understand RAG: RetrievalAugmented Generation]
    end

    subgraph RAG-based Chatbot
        rag --> retrieve[Retrieve Relevant Information: From product catalogs, FAQs, customer reviews]
        retrieve --> generate[Generate Tailored Responses]
        generate --> answer[Provide Accurate, Contextually Relevant Answers]
    end

    subgraph E-commerce Platforms
        answer --> queries[Handle Diverse Customer Queries: Product inquiries, order tracking, troubleshooting]
        queries --> satisfaction[Improve Customer Satisfaction]
        satisfaction --> process[Streamline Service Processes]
        process --> errors[Reduce Errors]
    end

    subgraph Enhanced Customer Support
        errors --> engagement[Enhance Engagement]
        engagement --> experience[Optimize E-commerce Experience]
    end
  `;
  useEffect(() => {
    console.log("Mermaid component mounted!");
  }, []);

  return (
    <div>
      <h2>Mermaid Diagram Example</h2>
      <Mermaid chart={mermaidCode} />
    </div>
  );
};

export default MermaidDiagram;
