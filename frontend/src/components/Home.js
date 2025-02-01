import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { useAppContext } from "../context/AppContext";
import DownloadButton from "./DownloadButton"; // Import the new component
import "../style/Home.css";

const Home = () => {
  const { isDarkMode, setAbstractionText } = useAppContext();
  const [pdfFiles, setPdfFiles] = useState([]);
  const [mode, setMode] = useState("");
  const [status, setStatus] = useState("");
  const [downloadLink, setDownloadLink] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [requiresAbstraction, setRequiresAbstraction] = useState(false);
  const [abstractionText, setAbstractionText1] = useState("");
  const [selectedImage, setSelectedImage] = useState(null); // For selecting the image

  const { getRootProps, getInputProps } = useDropzone({
    accept: ".pdf",
    multiple: true,
    onDrop: (acceptedFiles) => setPdfFiles((prevFiles) => [...prevFiles, ...acceptedFiles]),
  });

  const handleRemoveFile = (index) => {
    setPdfFiles(pdfFiles.filter((_, i) => i !== index));
  };

  const handleModeChange = (selectedMode) => {
    setMode(selectedMode);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (pdfFiles.length === 0 || !mode) {
      setStatus("❌ Please select a mode and upload at least one file.");
      return;
    }

    setIsLoading(true);
    setStatus("⏳ Processing... Please wait.");

    const formData = new FormData();
    pdfFiles.forEach((file) => formData.append("pdfFiles", file));
    formData.append("requiresAbstraction", requiresAbstraction);
    formData.append("abstractionText", abstractionText);
    formData.append("mode", mode);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("🔹 Upload Response:", data);

      if (response.ok) {
        setDownloadLink("http://localhost:5000/download_pptx");
        setStatus("✅ Processing Complete! Click below to download.");
      } else {
        setStatus("❌ Error: " + data.message);
      }
    } catch (error) {
      console.error("❌ Error uploading files:", error);
      setStatus("❌ Failed to upload files.");
    }

    setIsLoading(false);
  };

  return (
    <div className={`home-container ${isDarkMode ? "dark-mode" : ""}`}>
      <h2>📄 Welcome To JustLearn !!!!</h2>

      {/* Abstraction Requirement Checkbox */}
      <div className="abstraction-container">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={requiresAbstraction}
            onChange={() => setRequiresAbstraction(!requiresAbstraction)}
          />
          Require Abstraction?
        </label>
      </div>

      {/* Abstraction Text Input */}
      {requiresAbstraction && (
        <textarea
          className="abstraction-input"
          placeholder="Enter abstraction details..."
          value={abstractionText}
          onChange={(e) => {
            setAbstractionText1(e.target.value);
            setAbstractionText(e.target.value);
          }}
        />
      )}

      {/* Mode Selection */}
      <div className="mode-buttons">
        <button
          className={`mode-button ${mode === "fun" ? "active" : ""}`}
          onClick={() => handleModeChange("fun")}
        >
          🎉 Fun Mode
        </button>
        <button
          className={`mode-button ${mode === "formal" ? "active" : ""}`}
          onClick={() => handleModeChange("formal")}
        >
          📑 Formal Mode
        </button>
      </div>

      {/* File Upload Form */}
      <form onSubmit={handleSubmit} className="file-upload-form">
        <div {...getRootProps()} className="file-drop-area">
          <input {...getInputProps()} />
          <p>📂 Drag & drop PDFs or click to select</p>
        </div>

        {/* Display Chosen Files */}
        {pdfFiles.length > 0 && (
          <div className="file-preview">
            <ul>
              {pdfFiles.map((file, index) => (
                <li key={index} className="file-item">
                  {file.name}
                  <button
                    type="button"
                    className="remove-file-button"
                    onClick={() => handleRemoveFile(index)}
                  >
                    ❌
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Submit Button */}
        <button type="submit" className="submit-button" disabled={pdfFiles.length === 0 || !mode}>
          🚀 Generate PPT
        </button>
      </form>

      {/* Show the Image Preview Only if a PDF is Uploaded */}
      {pdfFiles.length > 0 && (
        <div className="image-preview-container">
          <div className="image-scroll-container">
            {[...Array(8).keys()].map((index) => (
              <div
                key={index}
                className={`image-item ${selectedImage === index ? "selected" : ""}`}
                onClick={() => setSelectedImage(index)}
              >
                <img src={`/images/img${index + 1}.png`} alt={`Image ${index + 1}`} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading Animation */}
      {isLoading && (
        <div className="loading-animation">
          <div className="spinner"></div>
        </div>
      )}

      {/* Status Message */}
      {status && <div className="status-message">{status}</div>}

      {/* Show the DownloadButton only after processing */}
      {downloadLink && <DownloadButton downloadLink={downloadLink} />}
    </div>
  );
};

export default Home;
