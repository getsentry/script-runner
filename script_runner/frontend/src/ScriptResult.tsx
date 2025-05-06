import { useEffect, useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { coy } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AgGridReact } from 'ag-grid-react';
import jq from 'jq-web';
import { RunResult, RowData, MergedRowData } from './types';
import Chart from './Chart';


import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
ModuleRegistry.registerModules([AllCommunityModule]);

type Props = {
  group: string,
  function: string,
  data: RunResult | null;
  regions: string[]
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


// returns table formatted data if data is table like
// otherwise return null
function getGridData(mergedData: MergedRowData[] | null) {

  if (Array.isArray(mergedData) && mergedData.every(row => typeof row === 'object' && row !== null)) {
    if (mergedData.length === 0) {
      return null;
    }

    return {
      columns: Object.keys(mergedData[0]),
      data: mergedData,
    };
  }

  return null;
}

function ScriptResult(props: Props) {
  const [displayType, setDisplayType] = useState<string>('json');
  const [filteredResults, setFilteredResults] = useState<RunResult['results'] | null>(null);

  // With regions merged into row objects. For passing to chart and grid components.
  const [mergedData, setMergedData] = useState<MergedRowData[] | null>(null);

  const [displayOptions, setDisplayOptions] = useState<{ [k: string]: boolean }>(
    { 'json': true, 'grid': false, 'chart': false, 'download': true }
  );

  // For grid display
  const [rowData, setRowData] = useState<RowData[] | null>(null);
  const [colDefs, setColumnDefs] = useState<{ field: string }[] | null>(null);

  useEffect(() => {
    const currentSuccessResults = props.data?.results || null;
    setFilteredResults(currentSuccessResults);

    const merged = mergeRegionKeys(currentSuccessResults, props.regions);
    setMergedData(merged);
    const gridData = getGridData(merged);

    if (gridData) {
      setColumnDefs(gridData.columns.map(f => ({ "field": f, headerName: f })));
      setRowData(gridData.data as RowData[]);
    } else {
      setColumnDefs(null);
      setRowData(null);
    }

    setDisplayOptions(prevOptions => {
        const newOptions = {...prevOptions};
        newOptions["grid"] = gridData !== null;
        newOptions["chart"] = gridData !== null;
        // If current displayType becomes invalid, switch to 'json'
        if (newOptions[displayType] === false && displayType !== 'json' && displayType !== 'download') {
           setDisplayType('json');
        }
        return newOptions;
    });

  }, [props.data, props.regions, displayType]);

  function download() {
    const blob = new Blob([JSON.stringify(filteredResults)], { type: 'application/json' });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '');
    const fileName = `${props.group}_${props.function}_${timestamp}.json`
    const link = document.createElement('a');
    link.download = fileName;
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function copy() {
    // Copy the entire props.data (results and errors)
    const dataToCopy = props.data ? JSON.stringify(props.data, null, 2) : "No data";
    navigator.clipboard.writeText(dataToCopy)
      .then(() => console.log("Copied to clipboard!"))
      .catch(err => console.error("Failed to copy to clipboard:", err));
  }

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
  // Check if filteredResults (derived from props.data.results) has content
  const hasDisplayableResults = filteredResults && Object.keys(filteredResults).length > 0;

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
            {Object.entries(displayOptions).filter(([, active]) => active).map(([opt,]) => (
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
              style={{width: "100%", marginBottom: "10px", padding: "5px"}}
            />
          </div>

          {displayType === 'json' && (
            hasDisplayableResults ? (
              <div className="json-viewer">
                <SyntaxHighlighter language="json" style={coy} customStyle={{ fontSize: 12, width: "100%" }} wrapLines={true} lineProps={{ style: { whiteSpace: 'pre-wrap' } }}>
                  {JSON.stringify(filteredResults, null, 2)}
                </SyntaxHighlighter>
              </div>
            ) : <p>No successful results to display in JSON format (or filter cleared them).</p>
          )}

          {displayType === "grid" && displayOptions.grid && rowData && colDefs && (
            <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
              <AgGridReact
                rowData={rowData}
                columnDefs={colDefs}
                defaultColDef={{ sortable: true, resizable: true, filter: true, flex: 1 }} // Added flex:1
              />
            </div>
          )}
          {displayType === "grid" && (!displayOptions.grid || !rowData || !colDefs) && <p>No data suitable for grid view.</p>}

          {displayType === "chart" && displayOptions.chart && mergedData && (
            <div className="function-result-chart">
              <Chart data={mergedData} regions={props.regions} />
            </div>
          )}
          {displayType === "chart" && (!displayOptions.chart || !mergedData) && <p>No data suitable for chart view.</p>}

          {displayType === "download" && (
            <div>
              <div className="function-result-download">
                <div><button onClick={download}>download all data (results & errors)</button></div>
                <div><button onClick={copy}>copy all data to clipboard</button></div>
              </div>
            </div>
          )}
        </div>
      ) : (
         (!hasErrors && !props.data?.results) && <p>No data was returned from the execution.</p>
      )}
    </div>
  );
}

export default ScriptResult;
