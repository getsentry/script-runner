import { useEffect, useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { coy } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AgGridReact } from 'ag-grid-react';
import jq from 'jq-web';
import { AgCharts } from 'ag-charts-react';
import { RunResult } from './types';

import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
ModuleRegistry.registerModules([AllCommunityModule]);

type RowData = {
  [key: string]: unknown;
}

type ChartData = {
  data: unknown[],
  series: { xKey: string, yKey: string, yName: string }[]
}

type Props = {
  group: string,
  function: string,
  data: RunResult | null;
  regions: string[]
}


// Either return merged data or null
function mergeRegionKeys(data: unknown, regions: string[]) {
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

            return {
              region,
              ...rowData,
            }
          });
        }).flat(1);

        return processed;
      }
    }
  } catch {
    return null;
  }

  return null;

}


// returns table formatted data if data is table like
// otherwise return null
function getGridData(data: { [region: string]: unknown[] } | unknown, regions: string[]) {
  const mergedData = mergeRegionKeys(data, regions) || data;

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

const DATE_KEY = "date";

// returns chart formatted data if data can be rendered as line chart
// otherwise return null
function getChartData(data: unknown, regions: string[]) {
  try {
    const merged = mergeRegionKeys(data, regions) || data;

    if (merged && Array.isArray(merged)) {
      if (DATE_KEY in merged[0]) {
        const numericFields = Object.entries(merged[0]).filter(([, value]) => typeof value === 'number').map(([key,]) => key);

        const series = regions.map(region => {
          return numericFields.map(f => [region, f])
        }).flat(1);

        const mergedByDate: object = merged.reduce((acc: { [date: string]: { [key: string]: unknown } }, curr: { date: string, [key: string]: unknown }) => {
          const date = curr[DATE_KEY];
          if (!acc[date]) {
            acc[date] = {};
          }

          numericFields.forEach(field => {
            acc[date][`${curr["region"]}-${field}`] = curr[field];
          });

          return acc;
        }, {});

        const arr = Object.entries(mergedByDate).map(([date, obj]) => {
          return { date, ...obj };
        });

        if (numericFields.length > 0) {
          return {
            data: arr,
            series: series.map(([region, field]) => ({
              xKey: "date",
              yKey: `${region}-${field}`,
              yName: `${field} (${region})`,
            }))
          }
        }
      }
    }
  } catch {
    return null;
  }

  return null;

}


function ScriptResult(props: Props) {
  const [displayType, setDisplayType] = useState<string>('json');

  const [filteredData, setFilteredData] = useState(props.data);
  const [displayOptions, setDisplayOptions] = useState<{ [k: string]: boolean }>(
    { 'json': true, 'grid': false, 'chart': false, 'download': true }
  );
  const [rowData, setRowData] = useState<RowData[] | null>(null);
  const [colDefs, setColumnDefs] = useState<{ field: string }[] | null>(null);
  const [chartOptions, setChartOptions] = useState<ChartData | null>(null);


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
    const gridData = getGridData(filteredData, props.regions);
    const chartData = getChartData(filteredData, props.regions);


    if (gridData) {
      setColumnDefs(gridData.columns.map(f => ({ "field": f })))
      setRowData(gridData.data);
    } else {
      setColumnDefs(null)
      setRowData(null)
    }

    if (chartData) {
      setChartOptions(chartData);
    } else {
      setChartOptions(null);
    }

    setDisplayOptions(prev => {
      prev["grid"] = gridData !== null;
      prev["chart"] = chartData !== null;
      return prev;
    });

    if (displayOptions[displayType] === false) {
      setDisplayType('json');
    }


  }, [filteredData, props.regions, displayOptions, displayType]);

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
        displayType === "chart" && chartOptions && <div className="function-result-chart">
          <AgCharts options={chartOptions} />
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
