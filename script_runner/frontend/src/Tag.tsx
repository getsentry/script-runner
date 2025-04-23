import "./Tag.css";

interface TagProps {
  isReadonly: boolean;
}

function Tag({ isReadonly }: TagProps) {
  return (
    <span className={`tag ${isReadonly ? "tag-read" : "tag-write"}`}>
      {isReadonly ? "read" : "write"}
    </span>
  );
}

export default Tag;
