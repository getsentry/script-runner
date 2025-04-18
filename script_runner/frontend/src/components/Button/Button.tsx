import React from "react";
import "./Button.css";

// Define button variants
type ButtonVariant = "primary" | "secondary";

// Define the props for the Button component, extending standard button attributes
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: ButtonVariant; // Add optional variant prop, default to primary
}

// The Button component
function Button({
  children,
  className,
  variant = "primary",
  ...props
}: ButtonProps) {
  // Combine base class, variant class, and any additional classes
  const combinedClassName = `button button-${variant} ${
    className || ""
  }`.trim();

  return (
    <button className={combinedClassName} {...props}>
      {children}
    </button>
  );
}

export default Button;
