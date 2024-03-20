import "./Navbar.css";
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted";
import RefreshIcon from "@mui/icons-material/Refresh";
import { Button } from "@mui/material";
import { useEffect, useRef, useState } from "react";

interface NavbarProps {
  onResetChat: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onResetChat }) => {
  const [dropdown, setDropdown] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const toggleDropdown = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    setDropdown(!dropdown);
  };

  const handleOutsideClick = (event: MouseEvent) => {
    // Check if the click is outside the dropdownRef
    if (
      dropdownRef.current &&
      !dropdownRef.current.contains(event.target as Node)
    ) {
      setDropdown(false);
    }
  };

  useEffect(() => {
    if (dropdown) {
      document.addEventListener("click", handleOutsideClick);
    }
    return () => document.removeEventListener("click", handleOutsideClick);
  }, [dropdown]);

  return (
    <div className="navbar">
      <div className="navbar-left">
        <div className="title">NEXUM</div>
      </div>
      <div className="navbar-right">
        <div>
          <Button
            onClick={toggleDropdown}
            sx={{
              color: "var(--text-300)",
              borderRadius: "50%",
              minWidth: "unset",
              p: "10px",
              "&:hover": {
                background: "var(--bg-400)",
              },
            }}
          >
            <FormatListBulletedIcon
              sx={{ fontSize: "25px", color: "inherit" }}
            />
          </Button>
          <div
            ref={dropdownRef}
            className={`dropdown-menu ${dropdown ? "show" : ""}`}
          >
            <div className="options">
              <div className="option-container">
                <div
                  className="option"
                  onClick={(e) => {
                    onResetChat();
                    toggleDropdown(e);
                  }}
                >
                  <RefreshIcon
                    sx={{ fontSize: "15px", color: "var(--gray-900)" }}
                  />
                  <p>Reset chat</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
