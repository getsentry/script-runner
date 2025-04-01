import { Route } from './types.tsx'
import { useEffect, useState, useRef, useCallback } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/solid'


interface Props {
  regions: string[],
  route: Route,
  navigate: (to: Route) => void,
}

function Header(props: Props) {
  const [selected, setSelected] = useState<string[]>(props.route.regions);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const linkRef = useRef<HTMLAnchorElement | null>(null);

  const { navigate, route } = props;

  const handleClick = useCallback((event: MouseEvent) => {
    function orderRegions(selectedCustomers: string[]) {
      return selectedCustomers.sort((a, b) => props.regions.indexOf(a) - props.regions.indexOf(b))
    }

    if (linkRef.current && linkRef.current.contains(event.target as HTMLElement)) {
      setIsOpen(prev => !prev);
    } else if (dropdownRef.current && !dropdownRef.current.contains(event.target as HTMLElement)) {
      if (isOpen) {
        setIsOpen(false);
        const newRoute = { ...route };
        newRoute.regions = orderRegions(selected);
        navigate(newRoute);
      }
    }
  }, [isOpen, props.regions, selected, route, navigate]);

  useEffect(() => {
    document.addEventListener('click', handleClick);

    // Clean up on unmount
    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, [props.regions, props.route, isOpen, selected, handleClick]);

  useEffect(() => {
    setSelected(props.route.regions)
  }, [props.route.regions])


  function toggleProject(region: string) {
    setSelected((prev) => {
      return prev.includes(region) ? prev.filter(c => c !== region) || [] : [...prev, region]
    });
  }

  return (
    <div className="header">
      <div>
        <a className="header-title" onClick={() => props.navigate({ regions: props.route.regions })}>
          ⚡️ ops script runner ⚡ ️
        </a>
      </div>
      <div className="header-right">
        <a ref={linkRef} className='header-region-dropdown'>
          {props.route.regions.length > 0 && <span>{props.route.regions.join(', ')}</span>}
          {props.route.regions.length === 0 && <span><em>Select a region</em></span>}

          <span className="dropdown-chevron"><ChevronDownIcon className="size-3" /></span>
        </a>
        <div ref={dropdownRef} className={isOpen ? 'dropdown' : 'dropdown hidden'}>
          <ul>
            {props.regions.map(c => (
              <li>
                <label key={c}>
                  {c}
                </label>
                <input
                  type="checkbox"
                  value={c}
                  checked={selected.includes(c)}
                  onChange={() => toggleProject(c)}
                />
              </li>
            ))}
          </ul>
        </div>

      </div>
    </div>
  )
}


export default Header;
