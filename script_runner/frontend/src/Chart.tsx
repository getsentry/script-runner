import { useEffect, useState } from 'react';

import { AgCharts } from 'ag-charts-react';
import { MergedRowData } from './types';

type ChartData = {
  data: unknown[],
  series: { xKey: string, yKey: string, yName: string }[]
}


// returns chart formatted data if data can be rendered as line chart
// otherwise return null
function getChartData(mergedData: unknown, regions: string[], xAxisKey: string) {
  try {
    if (mergedData && Array.isArray(mergedData)) {
      const numericFields = getNumericFields(mergedData);

      const series = regions.map(region => {
        return numericFields.map(f => [region, f])
      }).flat(1);

      const mergedByDate: object = mergedData.reduce((acc: { [date: string | number]: { [key: string]: unknown } }, curr: { date: string, [key: string]: unknown }) => {
        const xValue = curr[xAxisKey] as string | number;

        if (!(xValue in acc)) {
          acc[xValue] = {};
        }

        numericFields.forEach(field => {
          acc[xValue][`${curr["region"]}-${field}`] = curr[field];
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
  } catch {
    return null;
  }

  return null;
}

function getXAxisOptions(data: MergedRowData[]): string[] {
  if (!data.length) {
    return [];
  }
  return Object.keys(data[0]).filter((key) => key !== "region");
}

function getNumericFields(data: MergedRowData[]): string[] {
  if (!data.length) {
    return [];
  }
  return Object.entries(data[0]).filter(([, value]) => typeof value === 'number').map(([key,]) => key);
}


type Props = {
  data: MergedRowData[] | null;
  regions: string[];
}

function Chart(props: Props) {
  const [xAxisOptions, setXAxisOptions] = useState<string[]>([]);
  const [xAxis, setXAxis] = useState<string | null>(null);

  // Object to pass to ag-charts
  const [chartOptions, setChartOptions] = useState<ChartData | null>(null);

  useEffect(() => {
    setXAxisOptions(getXAxisOptions(props.data || []));
  }, [props.data, props.regions]);

  // update chart data when the selected x axis changes
  useEffect(() => {
    if (xAxis) {
      const chartData = getChartData(props.data, props.regions, xAxis);
      setChartOptions(chartData);
    } else {
      setChartOptions(null);
    }
  }, [props.data, props.regions, xAxis]);


  const canRenderChart = props.data && Array.isArray(props.data) && getNumericFields(props.data).length > 0;

  if (canRenderChart) {
    return <div className="function-result-chart">
      <div className="function-result-chart-controls">
        <div>
          <label>x axis:</label>
          <select onChange={(e) => setXAxis(e.target.value)} value={xAxis || ""}>
            <option value="">Select x axis</option>
            {xAxisOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>
      {chartOptions && <AgCharts options={chartOptions} />}
    </div >
  } else {
    return <div className="function-result-chart">
      <p className="no-data">data can't be displayed as a chart</p>
    </div>
  }




}

export default Chart;
