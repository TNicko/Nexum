import React, { useState } from "react";
import "./Sources.css";

interface SourcesProps {
  refs?: string[];
}

const Sources: React.FC<SourcesProps> = ({ refs }) => {
  const [hoveredSource, setHoveredSource] = useState<number | null>(null);

  // dummy references for testing
  refs = [
    "https://lsu.co.uk/societies/list",
    "https://www.lboro.ac.uk/services/library",
  ];

  const urlDisplayLength = 20;

  return (
    <div
      className={`sources-container ${hoveredSource !== null ? "blurred" : ""}`}
    >
      {refs?.map((ref, index) => (
        <div
          className={`source-wrapper ${hoveredSource === index ? "focused" : ""}`}
          onMouseEnter={() => setHoveredSource(index)}
          onMouseLeave={() => setHoveredSource(null)}
        >
          <a className="source" key={index} href={ref}>
            <img
              src={`https://s2.googleusercontent.com/s2/favicons?domain=${new URL(ref).hostname}&sz=64`}
              alt="icon"
              className="favicon"
              style={{
                marginRight: "5px",
                width: "15px",
                height: "15px",
                borderRadius: "50%",
              }}
            />
            {/*{new URL(ref).hostname} {/* Display the domain name */}
            {ref.length > urlDisplayLength
              ? ref.substring(0, urlDisplayLength) + "..."
              : ref}
          </a>
          <a  href={ref} className="source-info">
            <img
              src={`https://s2.googleusercontent.com/s2/favicons?domain=${new URL(ref).hostname}&sz=64`}
              alt="icon"
              className="favicon"
              style={{
                marginRight: "5px",
                width: "15px",
                height: "15px",
                borderRadius: "50%",
              }}
            />
            {ref}
          </a>
        </div>
      ))}
    </div>
  );
};

export default Sources;
