import React, { useState } from "react";
import { Paper, IconButton, InputBase } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import StopIcon from '@mui/icons-material/Stop';
import "./UserInput.css";

// Define a TextboxProps interface for the component props
interface TextboxProps {
  onButtonClick: (value: string) => void; // Callback for input change
  isSubmitDisabled: boolean;
	onCancel: () => void;
}

const UserInput: React.FC<TextboxProps> = ({
  onButtonClick,
  isSubmitDisabled,
	onCancel,
}) => {
  const [inputValue, setInputValue] = useState<string>("");
  
	const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    setInputValue(newValue);
  };

  const handleButtonClick = () => {
    onButtonClick(inputValue);
    setInputValue("");
  };

  return (
    <Paper
      component="form"
      sx={{
        borderRadius: "8px 8px 8px 8px",
        background: "var(--bg-100)",
        border: "1px solid var(--text-100)",
        p: "8px 8px",
        height: "2.5rem",
        display: "flex",
        alignItems: "center",
        width: "100%",
      }}
    >
      <InputBase
        sx={{
          ml: 1,
          flex: 1,
          color: "var(--text-400)",
          "& ::placeholder": {
            color: "var(--text-100)",
            opacity: 1,
            fontFamily: "StyreneB",
          },
        }}
        placeholder="Message Nexum..."
        value={inputValue}
        onChange={handleInput}
      />
      <div style={{ alignItems: "center", display: "flex", gap: "5px" }}>
        {isSubmitDisabled && (
          <IconButton
						onClick={onCancel}
						className="cancel-button"
            type="button"
            sx={{
              color: "var(--white)",
              background: "var(--red-500)",
              height: "1.8rem",
              width: "1.8rem",
              borderRadius: "50%",
              "&:hover": {
                backgroundColor: "var(--red-600)",
              },
            }}
          >
						<StopIcon sx={{ fontSize: "20px" }}/>
					</IconButton>
        )}
        <IconButton
          onClick={handleButtonClick}
          disabled={isSubmitDisabled}
          type="button"
          sx={{
            color: "var(--white)",
            background: "var(--brand-600)",
            height: "2.2rem",
            width: "2.2rem",
            borderRadius: "8px",
            "&:hover": {
              backgroundColor: "var(--brand-500)",
            },
            "&[disabled]": {
              opacity: 0.7,
              color: "var(--white)",
              pointerEvents: "none",
              background: "var(--brand-300)",
            },
          }}
          className="send-button"
          aria-label="send"
        >
          {!isSubmitDisabled ? (
            <SendIcon sx={{ fontSize: "15px" }} />
          ) : (
            <div className="custom-spinner"></div>
          )}
        </IconButton>
      </div>
    </Paper>
  );
};

export default UserInput;
