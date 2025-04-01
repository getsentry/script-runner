import React, {useState, useRef} from 'react';
import {ConfigFunction, ConfigGroup, Route} from './types.tsx'

type Props = {
  route: Route,
  navigate: (to: Route) => void,
  groups: ConfigGroup[],
}

function Home(props: Props) {
  const [searchResults, setSearchResults] = useState<{function: ConfigFunction, group: string}[] | null>(null);
  const [showResults, setShowResults] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);


  function search(query: string) {
    if (query === "") {
      setSearchResults(null);
      setShowResults(false);
      return;
    }

    const results = [];

    const substrings = query.split(" ");

    for (const group of props.groups) {
      for (const f of group.functions) {
        let found = true;
        for (const substr of substrings) {
          if (!f.name.includes(substr) && !group.group.includes(substr)) {
            found = false;
            break;
          }
        }
        // All substrings found
        if (found) {
          results.push({function: f, group: group.group});
        }

      }
    }

    setSearchResults(results.slice(0, 10));
    setShowResults(true);
  }

  function handleBlur(e: React.FocusEvent<HTMLInputElement>) {
    if (dropdownRef.current && !dropdownRef.current.contains(e.relatedTarget)) {
      setShowResults(false);
    }
  }

  function handleFocus() {
    setShowResults(true);
  }

  return (
    <div className="home">
      <div className="home-search">
        <div className="home-search-text">What do you want to do today?</div>
        <div className="home-search-input">
          <input
            type="text"
            placeholder="Search"
            onChange={e => search(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
          />
        </div>
        <div className="home-search-results" ref={dropdownRef} tabIndex={0}>
          {searchResults !== null && showResults && (
            <ul>
              {searchResults.map((f, index) => (
                <li key={index} className="home-search-result">
                  <a onClick={() => props.navigate({...props.route, group: f.group, function: f.function.name})}>
                    <span className="function-group">{f.group} / </span>
                    <span>{f.function.name}</span>
                  </a>
                </li>
              ))}
              {
                searchResults !== null && searchResults.length === 0 && <li className="home-no-result"><em>no results</em></li>
              }
            </ul>
          )}
        </div>


      </div>
    </div>
  )
}

export default Home
