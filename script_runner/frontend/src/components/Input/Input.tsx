import React from "react";
import { ConfigParam } from "../../types"; // Adjust path if needed
import "./Input.css";

interface InputProps {
  parameter: ConfigParam;
  value: string | null;
  isDisabled: boolean;
  onChange: (value: string) => void;
}

function Input({ parameter, value, isDisabled, onChange }: InputProps) {
  const { name, enumValues } = parameter;
  const inputId = `param-${name}`; // Create unique ID for label association

  return (
    <div className="input-group">
      {" "}
      {/* Renamed class */}
      <div className="input-label">
        {" "}
        {/* Renamed class */}
        <label htmlFor={inputId}>{name}</label>
      </div>
      <div className="input-control">
        {" "}
        {/* Renamed class */}
        {enumValues ? (
          <select
            id={inputId}
            required
            disabled={isDisabled}
            value={value || ""} // Handle null value for select
            onChange={(e) => onChange(e.target.value)}
            className="input-select" // Renamed class
          >
            <option value="" disabled>
              Select...
            </option>{" "}
            {/* Add placeholder option */}
            {enumValues.map((enumValue) => (
              <option key={enumValue} value={enumValue}>
                {enumValue}
              </option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            id={inputId}
            required
            disabled={isDisabled}
            value={value || ""} // Handle null value for input
            onChange={(e) => onChange(e.target.value)}
            className="input-text" // Renamed class
          />
        )}
      </div>
    </div>
  );
}

export default Input;
