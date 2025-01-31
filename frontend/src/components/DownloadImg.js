import React from 'react';

function DownloadImg() {
  const handleDownload = () => {
    const pdfUrl = '/sample.pdf';
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = 'sample.pdf'; 
    link.click();
  };

  return (
    <button onClick={handleDownload}>Download PDF</button>
  );
}

export default DownloadImg;
