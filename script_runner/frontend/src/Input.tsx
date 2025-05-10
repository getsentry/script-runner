import { useState } from "react";
import { ParamType } from "./types";

const MAX_OPTIONS = 5;


type Props = {
  id: string;
  disabled: boolean;
  value: string;
  onChange: (value: string) => void;
  type: ParamType;
  // applies to autocomplete and dynamic_autocomplete
  options: string[] | null;
}

// A custom input with optional autocomplete functionality
function Input(props: Props) {
  const [dropdownVisible, setDropdownVisible] = useState(false);

  const [activeIndex, setActiveIndex] = useState(-1);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'ArrowDown') {
      const nextIndex = (activeIndex + 1) % 5;
      setActiveIndex(nextIndex);
    } else if (e.key === 'ArrowUp') {
      const nextIndex = (activeIndex - 1 + 5) % 5;
      setActiveIndex(nextIndex);
    }
    else if (e.key === 'Enter') {
      if (activeIndex >= 0 && activeIndex < filteredOptions.length) {
        fillOption(filteredOptions[activeIndex]);
      }
      // Don't immediately submit the form
      e.preventDefault();
    }
  }

  function filterOptions(): string[] {
    // return first 5 options
    return (props.options || []).filter(option => option.toLowerCase().includes(props.value.toLowerCase())).slice(0, MAX_OPTIONS);
  }

  const filteredOptions = filterOptions();

  function fillOption(value: string) {
    props.onChange(value);
    setDropdownVisible(false);
  }

  function handleFocus() {
    if (props.type === "autocomplete" || props.type === "dynamic_autocomplete") {
      setDropdownVisible(true);
    }
  }

  function handleBlur() {
    if (props.type === "autocomplete" || props.type === "dynamic_autocomplete") {
      setDropdownVisible(false);
    }
  }

  if (props.type === "number" || props.type === "integer") {
    return (
      <input
        type="number"
        id={props.id}
        value={Number(props.value) || 0}
        onChange={(e) => {
          props.onChange(String(e.target.value))
        }}
        required
        disabled={props.disabled}
      />
    )
  }

  if (props.type === "textarea") {
    return (
      <div className="input-container">
        <textarea
          required
          onChange={e => props.onChange(e.target.value)}
          value={props.value}
          disabled={props.disabled}
        /></div >)
  }

  return <div className="input-container">
    <input
      type="text"
      required
      onChange={e => props.onChange(e.target.value)}
      value={props.value}
      disabled={props.disabled}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
    />

    {dropdownVisible && filteredOptions.length > 0 && (
      <div className="autocomplete-list">
        <ul>
          {filteredOptions.map((option, index) => (
            <li key={index}>
              <a
                className={index === activeIndex ? "active" : ""}
                onMouseEnter={() => setActiveIndex(index)} onMouseDown={() => fillOption(option)}
                onMouseLeave={() => setActiveIndex(-1)}
              >
                {option}
              </a>
            </li>
          ))
          }
        </ul>
      </div>
    )}
  </div>

}

export default Input;
