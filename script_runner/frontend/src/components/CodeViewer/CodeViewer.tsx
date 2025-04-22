import React, { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import Button from "../Button/Button"; // Adjust path as needed
import Tag from "../Tag/Tag"; // Import Tag component
import "./CodeViewer.css";

interface CodeViewerProps {
  functionName: string;
  source: string;
  type: "read" | "write"; // Add type prop
}

function CodeViewer({ functionName, source, type }: CodeViewerProps) {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  if (isCollapsed) {
    return (
      <div className="code-viewer-collapsed">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setIsCollapsed(false)}
          aria-label="Show code"
        >
          Show Code
        </Button>
      </div>
    );
  }

  return (
    <div className="code-viewer-expanded">
      <div className="code-viewer-header">
        <div className="code-viewer-title-group">
          <Tag variant={type} />
          <span>✨ {functionName} source ✨</span>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setIsCollapsed(true)}
          aria-label="Hide code"
        >
          Hide Code
        </Button>
      </div>
      <div className="code-viewer-content">
        <SyntaxHighlighter
          language="python"
          // Add any preferred style from react-syntax-highlighter/dist/esm/styles/prism
          // e.g., import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
          // style={prism}
          customStyle={{
            margin: 0, // Remove default margin from highlighter
            fontSize: "12px",
            maxHeight: "calc(100vh - 150px)", // Example max height, adjust as needed
            overflowY: "auto", // Ensure scrolling if content exceeds max height
          }}
          showLineNumbers // Optional: show line numbers
        >
          {source}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

export default CodeViewer;
