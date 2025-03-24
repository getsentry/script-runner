import { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import ScriptResult from './ScriptResult.tsx';
import { RunResult, ConfigFunction } from './types.tsx';


interface Props {
  regions: string[],
  group: string,
  function: ConfigFunction,
  canExecute: boolean,
  execute: (regions: string[], group: string, func: string, args: string[]) => Promise<RunResult>,
}


function Script(props: Props) {
  const { name: functionName, parameters, source } = props.function;
  const [params, setParams] = useState<(string | null)[]>(parameters.map(a => a.default));
  const [result, setResult] = useState<(RunResult | null)>(null);
  // we keep another piece of state because the result value might itself be null
  const [hasResult, setHasResult] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [codeCollapsed, setCodeCollapsed] = useState<boolean>(false);

  // If the selected function changes, reset all state
  useEffect(() => {
    setParams(parameters.map(a => a.default));
    setResult(null);
    setHasResult(false);
    setCodeCollapsed(false);
    setError(null);
  }, [parameters, props.group, props.function, props.canExecute, props.execute]);

  function handleInputChange(idx: number, value: string) {
    setParams(prev => {
      const next = [...prev];
      next[idx] = value;
      return next;
    })
  }

  function executeFunction() {
    if (hasResult) {
      return;
    }

    setError(null);

    if (params.some(p => p === null)) {
      return;
    }

    setIsRunning(true);

    props.execute(props.regions, props.group, functionName, params as string[]).then(
      (result: RunResult) => {
        setResult(result);
        setHasResult(true);
        setIsRunning(false);
      }
    )
      .catch((err) => {
        setError(err.error);
        setIsRunning(false);
      })
  }

  const disabled = isRunning || hasResult || props.regions.length === 0 || !props.canExecute;
  const inputDisabled = isRunning || hasResult || !props.canExecute;

  return (
    <div className="function-main">
      <div className="function-left">
        <div className="function-header"><span>{functionName}</span></div>
        <div className="function-execute">
          <form action={executeFunction}>
            {parameters.length > 0 && (
              <div>
                <div>To execute this function, provide the following parameters:</div>
                {
                  parameters.map((arg, idx) => {
                    return <div className="input-group">
                      <div><label htmlFor={arg.name}>{arg.name}</label></div>
                      <div>
                        {arg.enumValues && (
                          <select
                            id={arg.name}
                            required
                            disabled={inputDisabled}
                            value={params[idx] || ''}
                            onChange={e => handleInputChange(idx, e.target.value)}>
                            <option value="">Select...</option>
                            {arg.enumValues.map((v) => <option value={v}>{v}</option>)}
                          </select>
                        )}
                        {!arg.enumValues &&
                          <input
                            type="text"
                            id={arg.name} value={params[idx] || ''}
                            onChange={(e) => handleInputChange(idx, e.target.value)}
                            required
                            disabled={inputDisabled}
                          />
                        }
                      </div>
                    </div>
                  })
                }
              </div>
            )}
            <div className="function-hint">
              {props.canExecute && <>
                {props.regions.length > 0 ?
                  <>This will run on: {props.regions.join(", ")}</> :
                  <em>Select a region to run this function</em>
                }
              </>}
            </div>
            <button disabled={disabled}>execute function</button>
          </form>
        </div>
        {error && <div className="function-error"><strong>Error: </strong>{error}</div>}
        {hasResult && <ScriptResult data={result} group={props.group} function={functionName} regions={props.regions} />}
      </div>
      { }
      {
        codeCollapsed ? (
          <div className="function-right-button"><button onClick={() => setCodeCollapsed(false)} aria-label="open">open</button></div>
        ) : (
          <div className="function-right">
            <div className="function-right-description">✨ This is the <strong>{functionName}</strong> function definition ✨</div>
            <SyntaxHighlighter language="python" customStyle={{ fontSize: 12, width: 500 }}>{source}</SyntaxHighlighter>
            <div className="function-right-button"><button onClick={() => setCodeCollapsed(true)} aria-label="collapse">Collapse</button></div>
          </div>
        )
      }
    </div>
  )


}


export default Script
