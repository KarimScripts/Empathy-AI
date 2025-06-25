import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  postChatMessage,
  getCurrentUser,
  getHistory,
  getConversation,
} from "./api";
import { Send, Plus, Menu, X, LogOut } from "lucide-react";
import "./ChatPage.css";

const ChatPage = ({ removeToken }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [history, setHistory] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserAndHistory = async () => {
      try {
        const userResponse = await getCurrentUser();
        setUser(userResponse.data);
        const historyResponse = await getHistory();
        setHistory(historyResponse.data);
      } catch (error) {
        console.error("Failed to fetch initial data:", error);
      }
    };
    fetchUserAndHistory();
  }, []);

  useEffect(() => {
    if (currentConversationId) {
      const fetchConversation = async () => {
        setIsLoading(true);
        try {
          const response = await getConversation(currentConversationId);
          setMessages(response.data.messages);
        } catch (error) {
          console.error("Failed to fetch conversation:", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchConversation();
    } else {
      setMessages([]);
    }
  }, [currentConversationId]);

  const getGreeting = () => {
    const hours = new Date().getHours();
    if (hours < 12) return "Good Morning";
    if (hours < 18) return "Good Afternoon";
    return "Good Evening";
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setInput("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const response = await postChatMessage(
        currentInput,
        currentConversationId
      );
      const { ai_response, conversation_id } = response.data;
      const aiMessage = { role: "ai", content: ai_response };

      setMessages((prev) => [...prev, aiMessage]);

      if (!currentConversationId) {
        setCurrentConversationId(conversation_id);
        const newHistoryResponse = await getHistory();
        setHistory(newHistoryResponse.data);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage = {
        role: "ai",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    removeToken();
    navigate("/login");
  };

  return (
    <div className="chat-page-container">
      <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <button className="new-chat-button" onClick={handleNewChat}>
            <Plus size={20} />
            <span>New Chat</span>
          </button>
          <button
            className="sidebar-toggle"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>
        <div className="chat-history-list">
          {history.map((chat) => (
            <div
              key={chat.id}
              className={`history-item ${
                chat.id === currentConversationId ? "active" : ""
              }`}
              onClick={() => setCurrentConversationId(chat.id)}
            >
              {chat.title}
            </div>
          ))}
        </div>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              {user?.name ? user.name[0].toUpperCase() : "U"}
            </div>
            <span>{user?.name || "User"}</span>
          </div>
          <button className="logout-button" onClick={handleLogout}>
            <LogOut size={20} />
          </button>
        </div>
      </aside>
      <div className="chat-area">
        {!isSidebarOpen && (
          <button
            className="sidebar-toggle"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>
        )}
        <main className="chat-history">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.role}`}>
              <p>{msg.content}</p>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </main>

        <div className="interaction-area">
          {messages.length === 0 && !isLoading && (
            <h1 className="greeting">
              <span className="sparkle">✳</span> {getGreeting()},{" "}
              {user?.name || "friend"}.
            </h1>
          )}

          <form className="chat-input-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <textarea
                ref={textareaRef}
                placeholder="How can I help you today?"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                rows={1}
                disabled={isLoading}
              />
              <div className="model-selector">Empathy AI 1.0 ▾</div>
              <button
                type="submit"
                className="send-button"
                disabled={!input.trim() || isLoading}
              >
                <Send size={18} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
