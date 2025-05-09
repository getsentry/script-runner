import { useState, useEffect } from "react";
import { ParamType } from "./types";


type Props = {
  id: string;
  disabled: boolean;
  value: string;
  onChange: (value: string) => void;
  type: ParamType;
  // applies to autocomplete and dynamic_autocomplete
  initialOptions: string[] | null;
  loadOptions?: (input: string) => Promise<string[]>;
}

// A custom input with optional autocomplete functionality
function Input(props: Props) {
  const [options, setOptions] = useState<string[]>(props.initialOptions || []);
  const [dropdownVisible, setDropdownVisible] = useState(false);

  function filterOptions(): string[] {
    // return first 5 options
    return options.filter(option => option.toLowerCase().includes(props.value.toLowerCase())).slice(0, 5);
  }

  useEffect(() => {
    if (props.loadOptions) {
      props.loadOptions(props.value).then((newOptions) => {
        setOptions(newOptions);
      });
    }
  }, [])

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
      setTimeout(() => {
        setDropdownVisible(false);
      }, 100);
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
    />

    {dropdownVisible && filteredOptions.length > 0 && (
      <div className="autocomplete-list">
        <ul>
          {filteredOptions.map((option, index) => (
            <li key={index}><a onClick={() => fillOption(option)}>{option}</a></li>
          ))
          }
        </ul>
      </div>
    )}
  </div>

}

export default Input;
