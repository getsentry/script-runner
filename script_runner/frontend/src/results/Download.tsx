type Props = {
  group: string;
  function: string;
  filteredResults: unknown;
  // ignore other unused props, these should be aligned across all components later
  [key: string]: any;  // eslint-disable-line @typescript-eslint/no-explicit-any
}

function Download(props: Props) {

  function download() {
    const blob = new Blob([JSON.stringify(props.filteredResults)], { type: 'application/json' });
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
    const dataToCopy = props.filteredResults ? JSON.stringify(props.filteredResults, null, 2) : "No data";
    navigator.clipboard.writeText(dataToCopy)
      .then(() => console.log("Copied to clipboard!"))
      .catch(err => console.error("Failed to copy to clipboard:", err));
  }

  return (
    <div className="function-result-download">
      <div><button onClick={download}>download all data (results & errors)</button></div>
      <div><button onClick={copy}>copy all data to clipboard</button></div>
    </div>
  );
}

export default Download;

