import { useEffect, useRef } from "react";

const MessageHistoryDisplay = ({ messageHistory, formatMessage }) => {
  const historyContainerRef = useRef();

  // Automatically scroll to the latest chat messages.
  useEffect(() => {
    const { offsetHeight, scrollHeight, scrollTop } =
      historyContainerRef.current;

    if (scrollHeight <= scrollTop + offsetHeight + 240) {
      historyContainerRef.current.scrollTo({
        top: scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messageHistory.length]);

  return (
    <div className="h-full overflow-y-auto max-h-60" ref={historyContainerRef}>
      {messageHistory.map((message, index) => (
        <p className="mb-2 text-white" key={index}>
          {formatMessage(message)}
        </p>
      ))}
    </div>
  );
};

export default MessageHistoryDisplay;
