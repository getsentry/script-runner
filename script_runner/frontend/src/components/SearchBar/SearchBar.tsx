import React, { useState, useRef, useEffect } from "react";
import { ConfigGroup, ConfigFunction, Route } from "../../types"; // Adjust path
import "./SearchBar.css";

interface SearchResult {
  function: ConfigFunction;
  group: string;
}

interface SearchBarProps {
  groups: ConfigGroup[];
  route: Route; // Needed for navigation context
  navigate: (to: Route) => void;
}

function SearchBar({ groups, route, navigate }: SearchBarProps) {
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(
    null
  );
  const [showResults, setShowResults] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    // Add event listener to close dropdown when clicking outside
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowResults(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef, inputRef]);

  function performSearch(currentQuery: string) {
    if (currentQuery === "") {
      setSearchResults(null);
      setShowResults(false);
      return;
    }

    const results: SearchResult[] = [];
    const substrings = currentQuery
      .toLowerCase()
      .split(" ")
      .filter((s) => s);

    for (const group of groups) {
      for (const f of group.functions) {
        const searchableText = `${group.group.toLowerCase()} ${f.name.toLowerCase()}`;
        let found = true;
        for (const substr of substrings) {
          if (!searchableText.includes(substr)) {
            found = false;
            break;
          }
        }
        if (found) {
          results.push({ function: f, group: group.group });
        }
      }
    }

    setSearchResults(results.slice(0, 10)); // Limit results
    setShowResults(true);
  }

  function handleResultClick(result: SearchResult) {
    navigate({ ...route, group: result.group, function: result.function.name });
    setShowResults(false); // Close dropdown after selection
    if (inputRef.current) {
      inputRef.current.value = ""; // Clear visual input value
    }
  }

  function handleFocus() {
    if (searchResults && searchResults.length > 0) {
      setShowResults(true);
    }
  }

  return (
    <div className="search-bar-container">
      <div className="search-bar-input">
        <input
          ref={inputRef}
          type="text"
          placeholder="Search functions..."
          onChange={(e) => performSearch(e.target.value)}
          onFocus={handleFocus}
          // onBlur handling is done via click outside listener
        />
      </div>
      {showResults && searchResults !== null && (
        <div className="search-bar-results" ref={dropdownRef}>
          <ul>
            {searchResults.length > 0 ? (
              searchResults.map((result, index) => (
                <li
                  key={`${result.group}-${result.function.name}-${index}`}
                  className="search-bar-result"
                >
                  <a onClick={() => handleResultClick(result)}>
                    <span className="result-group">{result.group} / </span>
                    <span className="result-function">
                      {result.function.name}
                    </span>
                  </a>
                </li>
              ))
            ) : (
              <li className="search-bar-no-result">
                <em>no results found</em>
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SearchBar;
