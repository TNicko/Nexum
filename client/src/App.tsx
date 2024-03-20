import { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";
import UserInput from "./components/UserInput";
import Navbar from "./components/Navbar";
import ChatBubble from "./components/ChatBubble";
import Grid from "@mui/material/Grid";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import useLocalStorage from "./localStorage";

interface TextBox {
  text: string;
  type: number; // 0 for user, 1 for server response
  sources?: string[];
}

function App() {
  const [bubbles, setBubbles] = useLocalStorage<TextBox[]>("chatBubbles", []);
  const [introduction, setIntroduction] = useLocalStorage("introduction", true);
  const [isSubmitDisabled, setIsSubmitDisabled] = useState(false);
  const [abortController, setAbortController] =
    useState<AbortController | null>(null);
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);
  const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);
  const bubbleEl = useRef<HTMLDivElement>(null);

  const checkIsAtBottom = useCallback(() => {
    const isAtBottom =
      window.innerHeight + window.scrollY >=
      document.documentElement.scrollHeight - 2;
    return isAtBottom;
  }, []);

  useEffect(() => {
    let lastScrollPosition = window.scrollY;
    let ticking = false; // Throttling control for the scroll event

    const handleScroll = () => {
      const scrollY = window.scrollY;
      const isScrollingUp = scrollY < lastScrollPosition;

      if (isScrollingUp) {
        setUserHasScrolledUp(true);
      } else if (checkIsAtBottom()) {
        setUserHasScrolledUp(false);
      }

      lastScrollPosition = scrollY;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(handleScroll);
        ticking = true;
      }
    };

    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [checkIsAtBottom]);

  useEffect(() => {
    if (!userHasScrolledUp && autoScrollEnabled && bubbles.length > 0) {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
      });
    }
  }, [bubbles, autoScrollEnabled, userHasScrolledUp]);

  const resetChat = () => {
    setBubbles([]);
    setIntroduction(true);
    localStorage.removeItem("chatBubbles");
  };

  const cancelRequest = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
    console.log("Request Aborted.");
    setIsSubmitDisabled(false);
  };

  const handleButtonClick = async (value: string) => {
    setIsSubmitDisabled(true);

    const newAbortController = new AbortController();
    setAbortController(newAbortController);

    // Add user's message as a new bubble
    let newUserTextBox: TextBox = { text: value, type: 0 };
    setBubbles((oldBoxes) => [...(oldBoxes ?? []), newUserTextBox]);

    setTimeout(function () {
      window.scrollTo(0, document.documentElement.scrollHeight);
    }, 500);

    fetchEventSource("http://localhost:8000/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: value }),
      signal: newAbortController.signal,
      onopen: async (res) => {
        if (res.ok && res.status === 200) {
          console.log("Connection made ", res);
          // Create bubble for AI response
          setBubbles((oldBoxes) => [
            ...(oldBoxes ?? []),
            { text: "", type: 1 },
          ]);
        } else if (
          res.status >= 400 &&
          res.status < 500 &&
          res.status !== 429
        ) {
          console.log("Client-side error ", res);
        }
      },
      onmessage(event) {
        setBubbles((currentBubbles) => {
          let newBubbles = currentBubbles ? [...currentBubbles] : [];
          if (newBubbles.length > 0) {
            // Assuming the last bubble is always the AI response to update
            let lastIndex = newBubbles.length - 1;
            newBubbles[lastIndex] = {
              ...newBubbles[lastIndex],
              text: newBubbles[lastIndex].text + event.data,
            };
          }
          return newBubbles;
        });
      },
      onclose() {
        console.log("Connection closed by the server");
        setIsSubmitDisabled(false);
      },
      onerror(err) {
        console.log("There was an error from server", err);
        setIsSubmitDisabled(false);
      },
    });

    setIntroduction(false);
  };

  return (
    <>
      <Navbar onResetChat={resetChat} />
      <div className="app">
        <div className="main-container">
          <div className={introduction ? "background" : "background-faded"}>
            {introduction && (
              <>
                <div className="image"></div>
                <p className="intro-text">How can I help you today?</p>
              </>
            )}
          </div>

          <div className="main-conversation">
            <div className="stack-container">
              <Grid
                className="chat-container"
                ref={bubbleEl}
                container
                spacing={2}
              >
                {bubbles?.map((bubble, index) => (
                  <Grid key={index} item xs={100}>
                    <ChatBubble bubble={bubble} />
                  </Grid>
                ))}
              </Grid>
            </div>
          </div>

          <div className="input-container">
            <UserInput
              onButtonClick={handleButtonClick}
              isSubmitDisabled={isSubmitDisabled}
              onCancel={cancelRequest}
            />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;