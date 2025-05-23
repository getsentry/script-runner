import { useState, useEffect } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ScriptResult from "./ScriptResult.tsx";
import { RunResult, ConfigFunction } from "./types.tsx";
import Tag from "./Tag";
import Api from "./api.tsx";
import Input from './Input.tsx'
import Collapse from './assets/Collapse.tsx';
import Expand from './assets/Expand.tsx';


interface Props {
  regions: string[];
  group: string;
  function: ConfigFunction;
  api: Api;
}

function Script(props: Props) {
  const { name: functionName, parameters, source, isReadonly } = props.function;
  const [params, setParams] = useState<(string | null)[]>(
    parameters.map((a) => a.default)
  );
  const [result, setResult] = useState<RunResult | null>(null);
  // we keep another piece of state because the result value might itself be null
  const [hasResult, setHasResult] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [codeCollapsed, setCodeCollapsed] = useState<boolean>(false);

  // the user has to confirm a write function
  const [confirmWrite, setConfirmWrite] = useState<boolean>(false);

  // all the dynamic autocomplete options keyed by the parameter name
  const [dynamicOptions, setDynamicOptions] = useState<{ [fieldName: string]: string[] }>({});


  // If the selected function changes, reset all state
  useEffect(() => {
    setParams(parameters.map((a) => a.default));
    setResult(null);
    setHasResult(false);
    setCodeCollapsed(false);
    setError(null);
    setConfirmWrite(false);
    setDynamicOptions({})

    if (parameters.some((p) => p.type === "dynamic_autocomplete")) {
      props.api.getAutocompleteOptions({
        'group': props.group,
        'function': functionName,
        'regions': props.regions
      }).then((optionResult) => {
        const options: { [fieldName: string]: string[] } = {};
        for (const region in optionResult) {
          for (const field in optionResult[region]) {
            if (!(field in options)) {
              options[field] = [];
            }
            options[field] = optionResult[region][field];
          }
        }
        setDynamicOptions(options);
      });
    }
  }, [parameters, props.group, props.function, props.api, props.regions, functionName]);

  function handleInputChange(idx: number, value: string) {
    setParams((prev) => {
      const next = [...prev];
      next[idx] = value;
      return next;
    });
  }

  function executeFunction() {
    setResult(null);
    setHasResult(false);
    setError(null);

    if (params.some((p) => p === null)) {
      return;
    }

    if (!isReadonly && !confirmWrite) {
      setError("Confirm dangerous function");
      return;
    }

    setIsRunning(true);

    props.api.run({
      'group': props.group,
      'function': functionName,
      'parameters': params,
      'regions': props.regions,
    }).then((apiRunResult: RunResult) => {
      setResult(apiRunResult);
      setHasResult(true);
      setIsRunning(false);
    }).catch((err) => {
      setError(err.error);
      setResult(null);
      setHasResult(false);
      setIsRunning(false);
    });
  }

  const disabled = isRunning || props.regions.length === 0;

  const buttonText = hasResult ? "Run Again" : "execute function";

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    executeFunction();
  };

  return (
    <div className="function-main">
      <div className="function-left">
        <div className="function-header">
          <Tag isReadonly={isReadonly} />
          <span>{functionName}</span>
        </div>
        <div className="function-execute">
          <form onSubmit={handleSubmit}>
            {parameters.length > 0 && (
              <div>
                <div>
                  To execute this function, provide the following parameters:
                </div>
                {parameters.map((arg, idx) => {
                  return (
                    <div className="input-group arg" key={`${functionName}-param-${arg.name}-${idx}`}> {/* Improved key */}
                      <div>
                        <label htmlFor={arg.name}>{arg.name}</label>
                      </div>
                      <div>
                        <Input
                          id={arg.name}
                          value={params[idx] || ""}
                          type={arg.type}
                          disabled={disabled}
                          onChange={(value) =>
                            handleInputChange(idx, value)
                          }
                          options={dynamicOptions[arg.name] || arg.enumValues}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            {!isReadonly && (
              <div className="input-group confirm">
                <input
                  type="checkbox"
                  id="confirm-write"
                  checked={confirmWrite}
                  disabled={disabled}
                  onChange={e => setConfirmWrite(e.target.checked)}
                />
                <label htmlFor="confirm-write">I accept this function may be dangerous -- let's do it.</label>
              </div>
            )}
            <button type="submit" className="execute" disabled={disabled}>
              {buttonText}
            </button>
            <div className="function-hint">
              {props.regions.length > 0 ? (
                <>This will run on: {props.regions.join(", ")}</>
              ) : (
                <em>Select a region to run this function</em>
              )}
            </div>
          </form>
        </div>
        {error && (
          <div className="function-error">
            <strong>Error: </strong>
            {error}
          </div>
        )}
        {hasResult && result !== null && (
          <ScriptResult
            data={result}
            group={props.group}
            function={functionName}
            regions={props.regions}
          />
        )}
      </div>
      {codeCollapsed ? (
        <div className="function-right-button">
          <button onClick={() => setCodeCollapsed(false)} aria-label="expand">
            <Expand />
            Expand
          </button>
        </div>
      ) : (
        <div className="function-right">
          <div className="function-right-description">
            <div><strong>View the definition</strong></div>
            <button
              onClick={() => setCodeCollapsed(true)}
              aria-label="collapse"
            >
              <Collapse />
              Collapse
            </button>

          </div>
          <div className="line" />
          <div className="code">
            <SyntaxHighlighter
              language="python"
              style={tomorrow}
              customStyle={{ fontSize: 12, maxWidth: 500 }}
            >
              {source}
            </SyntaxHighlighter>
          </div>
        </div>
      )}
    </div>
  );
}

export default Script;
