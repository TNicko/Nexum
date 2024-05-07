import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { type LLMOutputComponent } from "@llm-ui/react/core";

// Customize this component with your own styling
const MarkdownComponent: LLMOutputComponent = ({ blockMatch }) => {
  const markdown = blockMatch.output;
  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>;
};

export default MarkdownComponent
