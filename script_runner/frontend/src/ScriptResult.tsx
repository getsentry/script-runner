import { useEffect, useState } from 'react';
import jq from 'jq-web';
import { RunResult, RowData, MergedRowData } from './types';
import Chart from './results/Chart';
import Grid from './results/Grid';
import Download from "./results/Download";
import Json from "./results/Json";


type Props = {
  group: string;
  function: string;
  data: RunResult;
  regions: string[];
}


// Either return merged data or null
function mergeRegionKeys(data: RunResult['results'] | null | undefined, regions: string[]): MergedRowData[] | null {
  try {
    if (typeof data === 'object' && data !== null) {
      const shouldMerge = Object.keys(data).every((r: string) => regions.includes(r));
      if (shouldMerge) {

        const firstRegionData = Object.values(data)[0];
        if (!Array.isArray(firstRegionData)) {
          return null;
        }
        if (firstRegionData.length === 0) {
          return null;
        }

        if (!firstRegionData.every(el => typeof el === 'object' && el !== null)) {
          return null;
        }

        const firstRowKeys = Object.keys(firstRegionData[0])

        // All keys match
        for (let i = 1; i < firstRegionData.length; i++) {
          const rowKeys = Object.keys(firstRegionData[i])
          if (rowKeys.length !== firstRowKeys.length || !rowKeys.every(k => firstRowKeys.includes(k))) {
            return null
          }
        }

        const processed = Object.entries(data).map(([region, regionData]) => {
          if (!Array.isArray(regionData)) {
            return null;
          }

          return regionData.map((row) => {
            const rowData = Object.keys(row).reduce((acc: RowData, key) => {
              const value = row[key];
              acc[key] = typeof value === 'object' && value !== null ? JSON.stringify(value) : value;
              return acc;
            }, {});

            return { region, ...rowData };

          });
        }).flat(1);

        if (processed.some((el) => el === null)) {
          return null;
        }

        return processed as { region: string, [key: string]: unknown }[];
      }
    }
  } catch {
    return null;
  }

  return null;

}

function ScriptResult(props: Props) {
  const [displayType, setDisplayType] = useState<string>('json');
  const [filteredResults, setFilteredResults] = useState<RunResult['results'] | null>(null);

  // With regions merged into row objects. For passing to chart and grid components.
  const [mergedData, setMergedData] = useState<MergedRowData[] | null>(null);

  const components = {
    "json": Json,
    "grid": Grid,
    "chart": Chart,
    "download": Download,
  };

  const ComponentToRender = components[displayType as keyof typeof components];


  useEffect(() => {
    const currentSuccessResults = props.data?.results || null;
    setFilteredResults(currentSuccessResults);

    const merged = mergeRegionKeys(currentSuccessResults, props.regions);
    setMergedData(merged);
  }, [props.data, props.regions, displayType]);

  function applyJqFilter(raw: RunResult['results'] | null | undefined, filter: string) {
    // Apply jq filter only to the 'results' part
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    jq.then((jq: any) => jq.json(raw, filter)).catch(() => {
      // If any error occurs, display the raw data
      return raw
    }
    ).then(setFilteredResults).catch(() => { })
  }

  const hasErrors = props.data?.errors && Object.keys(props.data.errors).length > 0;

  return (
    <div className="function-result">
      {/* Display Errors First, if any */}
      {hasErrors && (
        <div className="errors-section" style={{ marginBottom: '20px' }}>
          <h3>Errors:</h3>
          {Object.entries(props.data!.errors).map(([regionName, errorData]) => (
            <div key={regionName} className="error-message-box" /* Add your red box styling here */
              style={{ border: '1px solid red', padding: '10px', marginBottom: '10px', backgroundColor: '#ffebee' }}>
              <h4>Region: {regionName} (Failed)</h4>
              <p><strong>Error Type:</strong> {errorData.type}</p>
              <p><strong>Message:</strong> {errorData.message}</p>
              {errorData.status_code && <p><strong>Status Received:</strong> {errorData.status_code}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Display Results Section (if any successful results or if no errors at all and no results) */}
      <h3>Successful Results:</h3>
      {(props.data?.results || !hasErrors) ? (
        <div className="results-section">
          <div className="function-result-header">
            {Object.keys(components).map((opt) => (
              <div key={opt} className={`function-result-header-item${displayType === opt ? ' active' : ''}`} >
                <a href="#" onClick={(e) => { e.preventDefault(); setDisplayType(opt); }}>{opt}</a>
              </div>
            ))}
          </div>
          <div className="function-result-filter">
            <input
              type="text"
              placeholder="Filter successful results with jq (e.g., '.region1 | .items[] | select(.id > 0)')"
              onChange={(e) => applyJqFilter(props.data?.results || null, e.target.value)}
              style={{ width: "100%", marginBottom: "10px", padding: "5px" }}
            />
          </div>
          <ComponentToRender
            filteredResults={filteredResults}
            group={props.group}
            function={props.function}
            data={mergedData}
            regions={props.regions}
          />
        </div>
      ) : (
        (!hasErrors && !props.data?.results) && <p>No data was returned from the execution.</p>
      )}
    </div>
  );
}

export default ScriptResult;
