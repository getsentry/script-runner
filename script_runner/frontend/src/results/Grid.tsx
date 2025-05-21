import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import { MergedRowData, RowData } from '../types';

ModuleRegistry.registerModules([AllCommunityModule]);

type Props = {
  data: MergedRowData[] | null;
  // ignore other unused props, these should be aligned across all components later
  [key: string]: any;
}

function Grid(props: Props) {
  const gridData = getGridData(props.data);

  if (!gridData) {
    return <p>No data suitable for grid view.</p>;
  }


  const colDefs = gridData.columns.map(f => ({ "field": f, headerName: f }));
  const rowData = gridData.data as RowData[];

  return <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
    <AgGridReact
      rowData={rowData}
      columnDefs={colDefs}
      defaultColDef={{ sortable: true, resizable: true, filter: true, flex: 1 }}
    />
  </div>
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


export default Grid;
