import {ConfigGroup, Route} from './types.tsx'

interface Props {
  regions: string[],
  group: ConfigGroup,
  navigate: (to: Route) => void,
}

function Scripts(props: Props) {
  return (
    <div className="functions">
      <div className="functions-header">{props.group.group}</div>
      {
        props.group.functions.length > 0 && (
          <div>
            <p>this module contains the following functions</p>
            <ul>
            {
              props.group.functions.map((f) => (
                <li className="functions-function">
                  <a onClick={() => props.navigate({regions: props.regions, group: props.group.group, function: f.name})}>{f.name}</a>
                </li>
              ))
            }
            </ul>
          </div>
        )
      }
      {!props.group.functions.length && <p><em>nothing to see here</em></p>}
    </div>
  )
}

export default Scripts
