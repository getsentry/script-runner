import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { coy } from 'react-syntax-highlighter/dist/esm/styles/prism';


type Props = {
  filteredResults: unknown;
  // ignore other unused props, these should be aligned across all components later
  [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}


function Json(props: Props) {
  return <div className="json-viewer">
    <SyntaxHighlighter language="json" style={coy} customStyle={{ fontSize: 12, width: "100%" }} wrapLines={true} lineProps={{ style: { whiteSpace: 'pre-wrap' } }}>
      {JSON.stringify(props.filteredResults, null, 2)}
    </SyntaxHighlighter>
  </div>
}

export default Json;
