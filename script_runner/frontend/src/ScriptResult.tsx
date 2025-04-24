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
function mergeRegionKeys(data: unknown, regions: string[]): MergedRowData[] | null {
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

  const [filteredData, setFilteredData] = useState(props.data);

  // With regions merged into row objects. For passing to chart and grid components.
  const [mergedData, setMergedData] = useState<MergedRowData[] | null>(null);

  const [displayOptions, setDisplayOptions] = useState<{ [k: string]: boolean }>(
    { 'json': true, 'grid': false, 'chart': false, 'download': true }
  );

  // For grid display
  const [rowData, setRowData] = useState<RowData[] | null>(null);
  const [colDefs, setColumnDefs] = useState<{ field: string }[] | null>(null);


  function download() {
    const blob = new Blob([JSON.stringify(filteredData)], { type: 'application/json' });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '');
    const fileName = `${props.group}_${props.function}_${timestamp}.json`
    const link = document.createElement('a');
    link.download = fileName;
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function copy() {
    const data = JSON.stringify(filteredData);
    navigator.clipboard.writeText(data);
  }

  function applyJqFilter(raw: RunResult | null, filter: string) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    jq.then((jq: any) => jq.json(raw, filter)).catch(() => {
      // If any error occurs, display the raw data
      return raw
    }
    ).then(setFilteredData).catch(() => { })
  }

  useEffect(() => {
    const mergedData = mergeRegionKeys(props.data, props.regions) || null;
    setMergedData(mergedData);
    const gridData = getGridData(mergedData);


    if (gridData) {
      setColumnDefs(gridData.columns.map(f => ({ "field": f })))
      setRowData(gridData.data);
    } else {
      setColumnDefs(null)
      setRowData(null)
    }

    setDisplayOptions(prev => {
      prev["grid"] = gridData !== null;
      prev["chart"] = gridData !== null;
      return prev;
    });

    if (displayOptions[displayType] === false) {
      setDisplayType('json');
    }

  }, [props.data, filteredData, props.regions, displayOptions, displayType]);

  return (
    <div className="function-result">
      <div className="function-result-header">
        {Object.entries(displayOptions).filter(([, active]) => active).map(([opt,]) => (
          <div className={`function-result-header-item${displayType === opt ? ' active' : ''}`} >
            <a onClick={() => setDisplayType(opt)}>{opt}</a>
          </div>
        ))}
      </div>
      <div className="function-result-filter">
        <input type="text" placeholder="Filter results with jq" onChange={(e) => applyJqFilter(props.data, e.target.value)} />
      </div>
      {
        displayType === 'json' && <div className="json-viewer">
          <SyntaxHighlighter language="json" style={coy} customStyle={{ fontSize: 12, width: "100%" }} wrapLines={true} lineProps={{ style: { whiteSpace: 'pre-wrap' } }}>
            {JSON.stringify(filteredData)}
          </SyntaxHighlighter>
        </div>
      }
      {
        displayType === "grid" && <div className="function-result-grid">
          <AgGridReact
            rowData={rowData}
            columnDefs={colDefs}
            defaultColDef={{ sortable: true }}
          />
        </div>
      }
      {
        displayType === "chart" && < div className="function-result-chart">
          <Chart data={mergedData} regions={props.regions} />
        </div>
      }
      {
        displayType === "download" && <div>
          <div className="function-result-download">
            <div><button onClick={download}>download json</button></div>
            <div><button onClick={copy}>copy to clipboard</button></div>
          </div>
        </div>
      }
    </div>
  )

}

export default ScriptResult
