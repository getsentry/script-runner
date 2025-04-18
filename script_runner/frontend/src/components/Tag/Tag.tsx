import React from "react";
import "./Tag.css";

// Define the possible variants for the tag
type TagVariant = "read" | "write";

// Define the props for the Tag component
interface TagProps {
  variant: TagVariant;
  children?: React.ReactNode; // Allow optional children if needed
}

// The Tag component
function Tag({ variant, children }: TagProps) {
  // Determine the text content based on the variant if no children are provided
  const textContent = children || variant;

  return <span className={`tag tag-${variant}`}>{textContent}</span>;
}

export default Tag;
