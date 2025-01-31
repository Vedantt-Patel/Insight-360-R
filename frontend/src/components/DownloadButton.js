import React from 'react';
import  '../style/DownloadButton.css';

const DownloadButton = () => {
    const handleDownload = () => {
        fetch('http://localhost:5000/download_pptx', {
            method: 'GET',
        })
        .then(response => response.blob())  // Convert response to Blob
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'output_presentation_final.pptx';  // Set download file name
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(err => console.error('Error downloading PPTX:', err));
    };

    return <button className="download-button" onClick={handleDownload}>📥 Download PPT</button>;
};

export default DownloadButton;
