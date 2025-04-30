import { marked } from 'marked';

interface Props {
  name: string;
  content: string;
}

function Document(props: Props) {
  return <div>
    <div
      className="document-markdown"
      dangerouslySetInnerHTML={{ __html: marked(props.content) }}
    />

  </div>

}

export default Document;
