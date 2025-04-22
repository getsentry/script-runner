import React from "react";
import "./Button.css";

// Define button variants
type ButtonVariant = "primary" | "secondary";
// Define button sizes
type ButtonSize = "sm" | "md"; // Add more sizes if needed (e.g., "lg")

// Define the props for the Button component, extending standard button attributes
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: ButtonVariant; // Add optional variant prop, default to primary
  size?: ButtonSize; // Add optional size prop
}

// The Button component
function Button({
  children,
  className,
  variant = "primary",
  size = "md", // Default size to medium
  ...props
}: ButtonProps) {
  // Combine base class, variant class, size class, and any additional classes
  const combinedClassName = `button button-${variant} button-${size} ${
    className || ""
  }`.trim();

  return (
    <button className={combinedClassName} {...props}>
      {children}
    </button>
  );
}

export default Button;
