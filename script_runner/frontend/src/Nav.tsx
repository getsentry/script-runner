import { useState } from 'react';
import './App.css'
import {ConfigGroup, Route} from './types.tsx'
import { FolderPlusIcon, FolderMinusIcon } from '@heroicons/react/24/outline'

interface Props {
  route: Route,
  navigate: (to: Route) => void,
  groups: ConfigGroup[],
}


function Nav(props: Props) {
  const activeGroup = "group" in props.route ? props.route.group : null;
  const activeFunction = "function" in props.route ? props.route.function : null;

  const [expanded, setExpanded] = useState<boolean[]>(
    props.groups.map(g => g.group === activeGroup)
  );

  function toggle(idx: number) {
    setExpanded((prev) => {
      const next = [...prev];
      next[idx] = !next[idx];
      return next;
    });
  }

  function expand(idx: number) {
    setExpanded((prev) => {
      const next = [...prev];
      next[idx] = true;
      return next;
    });
  }

  return (
    <div className="nav">
      <div className="sections">
        {
          props.groups.map((group, groupIdx) => {
            const isExpanded = expanded[groupIdx];
            return (
              <div className="nav-section">
                <div className="nav-group">
                  <a className="nav-group-icon" onClick={() => toggle(groupIdx)}>
                    {isExpanded ? <FolderMinusIcon /> : <FolderPlusIcon />}
                  </a>
                  <a className="group-text" onClick={() => {
                    expand(groupIdx);
                    props.navigate({regions: props.route.regions, group: group.group});
                  }}>{group.group}</a>
                </div>
                {isExpanded && <div>
                  {group.functions.map((f) => (
                    <a
                      title={f.name}
                      className={`nav-function ${(f.name === activeFunction && group.group === activeGroup) ? 'active' : ''}`}
                      onClick={() => props.navigate({regions: props.route.regions, group: group.group, function: f.name})}>
                      {f.name}
                    </a>
                  ))}
                </div>}
              </div>
            )
          })
        }
      </div>
    </div>
  )

}

export default Nav
