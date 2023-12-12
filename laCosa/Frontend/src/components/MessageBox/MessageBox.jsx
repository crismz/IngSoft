import { useEffect, useState } from "react";
import MessageHistoryDisplay from "../MessageHistoryDisplay/MessageHistoryDisplay";
import FormSendMessage from "../FormSendMessage/FormSendMessage";
import ToggleButton from "../ToggleButton/ToggleButton";
import {
  formatChatMessage,
  formatLogMessage,
} from "../../utils/functions/formatMessageHelper";

const MessageBox = ({ eventSource }) => {
  const [isChatActive, setIsChatActive] = useState(true);
  const [chatHistory, setChatHistory] = useState([]);
  const [logsHistory, setLogsHistory] = useState([]);

  useEffect(() => {
    eventSource.addEventListener("Chat", (event) => {
      const messageInfo = JSON.parse(event.data);
      setChatHistory((prevChatHistory) => [...prevChatHistory, messageInfo]);
    });

    eventSource.addEventListener("Log", (event) => {
      const logInfo = JSON.parse(event.data);
      setLogsHistory((prevLogsHistory) => [...prevLogsHistory, logInfo]);
    });
  }, []);

  return (
    <div className="absolute box-content bottom-0 left-0 h-80 w-80 border-2 bg-black/80 p-2">
      <span className="flex justify-between">
        <ToggleButton
          text="Chat"
          active={isChatActive}
          onClick={() => setIsChatActive(true)}
        />
        <ToggleButton
          text="Logs"
          active={!isChatActive}
          onClick={() => setIsChatActive(false)}
        />
      </span>
      <hr className="text-white" />
      <MessageHistoryDisplay
        messageHistory={isChatActive ? chatHistory : logsHistory}
        formatMessage={isChatActive ? formatChatMessage : formatLogMessage}
      />
      <hr className="text-white" />
      <FormSendMessage active={isChatActive} />
    </div>
  );
};

export default MessageBox;
