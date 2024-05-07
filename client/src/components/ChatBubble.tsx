import React, { useState } from "react";
import "./ChatBubble.css";
import Sources from "./Sources";
import PersonIcon from "@mui/icons-material/Person";
import ContentPasteIcon from "@mui/icons-material/ContentPaste";
import DoneIcon from "@mui/icons-material/Done";
import ReactMarkdown from "react-markdown";

interface TextBox {
  text: string;
  type: number; // 0 for user, 1 for server response
  sources?: string[];
	isStreaming: boolean;
}

interface ChatBubbleProps {
  bubble: TextBox;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ bubble }) => {
  const isUser = bubble.type === 0;
  const bubbleClass = isUser ? "user-bubble" : "ai-bubble";
  const textClass = isUser ? "user-message" : "ai-message";
  const [isCopy, setIsCopy] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(bubble.text);
    setIsCopy(true);
    setTimeout(() => {
      setIsCopy(false);
    }, 3000);
  };

	//const { blockMatches } = useLLMOutput({
		//llmOutput: bubble.text,
		//fallbackBlock: {
			//component: MarkdownComponent,
			//lookBack: markdownLookBack(),
		//},
		//blocks: [],
		//isStreamFinished: bubble.isStreaming,

	//})

  return (
    <div>
      <div
        className={`${bubbleClass} chat-bubble`}
        style={{ display: "flex", alignItems: "center" }}
      >
        <div>
          {!isUser && <Sources refs={bubble.sources} />}
          <div
            className={`${textClass} chat-text`}
            style={{
              display: "flex",
              alignItems: "center",
              padding: "8px 12px",
              boxShadow: "rgba(0, 0, 0, 0.024) 0px 2px 16px",
            }}
          >
            {isUser && (
              <PersonIcon
                sx={{
                  color: "var(--white)",
                  borderRadius: "50%",
                  fontSize: "12px",
                  p: "4px",
                  background: "var(--text-200)",
                  marginRight: "6px",
                }}
              />
            )}
						<div className="markdown-container">
							<ReactMarkdown>{bubble.text}</ReactMarkdown>
						</div>
            <div className="bubble-opts" onClick={copyToClipboard}>
              <div className={`bubble-opt copy-opt ${isCopy ? "copied" : ""}`}>
                {isCopy ? (
                  <>
                    <DoneIcon
                      sx={{ fontSize: "12px", color: "var(--gray-900)" }}
                    />
                    <p>Copied</p>
                  </>
                ) : (
                  <>
                    <ContentPasteIcon
                      sx={{ fontSize: "12px", color: "var(--gray-900)" }}
                    />
                    <p>Copy</p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBubble;
