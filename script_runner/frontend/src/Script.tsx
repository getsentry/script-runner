import { useState, useEffect } from "react";
import ScriptResult from "./ScriptResult.tsx";
import { RunResult, ConfigFunction } from "./types.tsx";
import Tag from "./components/Tag/Tag";
import Button from "./components/Button/Button";
import Input from "./components/Input/Input";
import CodeViewer from "./components/CodeViewer/CodeViewer";

interface Props {
  regions: string[];
  group: string;
  function: ConfigFunction;
  execute: (
    regions: string[],
    group: string,
    func: string,
    args: string[]
  ) => Promise<RunResult>;
}

function Script(props: Props) {
  const { name: functionName, parameters, source, type } = props.function;
  const [params, setParams] = useState<(string | null)[]>(
    parameters.map((a) => a.default)
  );
  const [result, setResult] = useState<RunResult | null>(null);
  const [hasResult, setHasResult] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  // If the selected function changes, reset all state
  useEffect(() => {
    setParams(parameters.map((a) => a.default));
    setResult(null);
    setHasResult(false);
    setError(null);
  }, [parameters, props.group, props.function, props.execute]);

  function handleInputChange(idx: number, value: string) {
    setParams((prev) => {
      const next = [...prev];
      next[idx] = value;
      return next;
    });
  }

  function executeFunction() {
    if (hasResult) {
      return;
    }

    setError(null);

    if (params.some((p) => p === null)) {
      return;
    }

    setIsRunning(true);

    props
      .execute(props.regions, props.group, functionName, params as string[])
      .then((result: RunResult) => {
        setResult(result);
        setHasResult(true);
        setIsRunning(false);
      })
      .catch((err) => {
        setError(err.error);
        setIsRunning(false);
      });
  }

  const disabled = isRunning || hasResult || props.regions.length === 0;
  const inputDisabled = isRunning || hasResult;

  return (
    <div className="function-main">
      <div className="function-left">
        <div className="function-header">
          <Tag variant={type} />
          <span>{functionName}</span>
        </div>
        <div className="function-execute">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              executeFunction();
            }}
          >
            {parameters.length > 0 && (
              <div>
                <div>
                  To execute this function, provide the following parameters:
                </div>
                {parameters.map((arg, idx) => (
                  <Input
                    key={arg.name}
                    parameter={arg}
                    value={params[idx]}
                    isDisabled={inputDisabled}
                    onChange={(value) => handleInputChange(idx, value)}
                  />
                ))}
              </div>
            )}
            <div className="function-hint">
              {props.regions.length > 0 ? (
                <>This will run on: {props.regions.join(", ")}</>
              ) : (
                <em>Select a region to run this function</em>
              )}
            </div>
            <Button type="submit" disabled={disabled}>
              execute function
            </Button>
          </form>
        </div>
        {error && (
          <div className="function-error">
            <strong>Error: </strong>
            {error}
          </div>
        )}
        {hasResult && (
          <ScriptResult
            data={result}
            group={props.group}
            function={functionName}
            regions={props.regions}
          />
        )}
      </div>
      <CodeViewer functionName={functionName} source={source} type={type} />
    </div>
  );
}

export default Script;
