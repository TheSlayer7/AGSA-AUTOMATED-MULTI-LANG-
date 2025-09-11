import { useState, useRef, useEffect, useCallback, memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, ArrowLeft, FileText, Clock, User, Bot, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { chatService } from "@/services/chat";

interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant" | "system";
  timestamp: Date;
  type?: "text" | "status" | "summary" | "system";
  isAIGenerated?: boolean;
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");
  const [isInitializing, setIsInitializing] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat session on component mount
  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      setIsInitializing(true);
      const session = await chatService.createSession();
      setCurrentSessionId(session.session_id);
      
      // Add welcome message
      if (session.messages && session.messages.length > 0) {
        const formattedMessages = session.messages.map(msg => ({
          id: msg.message_id,
          content: msg.content,
          sender: msg.sender,
          timestamp: new Date(msg.timestamp),
          type: msg.message_type
        }));
        setMessages(formattedMessages);
      } else {
        // Add default welcome message if none exists
        setMessages([{
          id: "welcome",
          content: "Hello! I'm your AGSA assistant. I'm here to help you navigate government services and find schemes you're eligible for. What would you like assistance with today?",
          sender: "assistant",
          timestamp: new Date(),
          type: "text"
        }]);
      }
    } catch (error) {
      console.error("Failed to initialize chat:", error);
      toast({
        title: "Connection Error",
        description: "Failed to connect to AGSA assistant. Please try again.",
        variant: "destructive",
      });
      
      // Set error state instead of fallback message
      setMessages([{
        id: "error",
        content: "I'm currently unable to connect to the government services. Please check your internet connection and try again.",
        sender: "assistant",
        timestamp: new Date(),
        type: "status"
      }]);
    } finally {
      setIsInitializing(false);
    }
  };

  const addMessage = useCallback((content: string, sender: "user" | "assistant" | "system", type: "text" | "status" | "summary" | "system" = "text", isAIGenerated: boolean = false) => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random()}`,
      content,
      sender,
      timestamp: new Date(),
      type,
      isAIGenerated
    };
    setMessages(prev => [...prev, newMessage]);
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isTyping) return;

    const userMessage = inputValue;
    setInputValue("");
    
    // Add user message immediately
    addMessage(userMessage, "user");
    setIsTyping(true);
    
    try {
      // Send message to AI service
      const response = await chatService.sendMessage({
        session_id: currentSessionId,
        message: userMessage,
        message_type: "text"
      });
      
      // Check if response has AI indicators (confidence score, intent category, etc.)
      const isFromAI = response.assistant_message.confidence_score !== null && 
                      response.assistant_message.confidence_score !== undefined &&
                      response.assistant_message.intent_category !== null &&
                      response.assistant_message.intent_category !== "llm_unavailable";
      
      // Check if LLM is unavailable
      const isLLMUnavailable = response.assistant_message.intent_category === "llm_unavailable";
      
      // Add AI response with appropriate type
      addMessage(
        response.assistant_message.content, 
        "assistant", 
        isLLMUnavailable ? "status" : response.assistant_message.message_type,
        isFromAI
      );
      
      // Show toast notification if LLM is unavailable
      if (isLLMUnavailable) {
        toast({
          title: "AI Service Unavailable",
          description: "The intelligent assistant is currently offline.",
          variant: "default",
        });
      }
      
    } catch (error) {
      console.error("Failed to send message:", error);
      
      // Show service unavailable message instead of fake response
      addMessage(
        "I'm currently unable to process your request due to a service interruption. Please try again in a few moments.",
        "assistant",
        "status",
        false
      );
      
      toast({
        title: "Service Unavailable", 
        description: "Unable to connect to government services. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsTyping(false);
    }
  }, [currentSessionId, addMessage, toast]);

  const MessageBubble = memo(({ message }: { message: Message }) => {
    const isUser = message.sender === "user";
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
      >
        <div className={`flex items-start space-x-2 max-w-[80%] ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? "bg-secondary" : "bg-primary"
          }`}>
            {isUser ? (
              <User className="w-4 h-4 text-white" />
            ) : message.isAIGenerated ? (
              <Sparkles className="w-4 h-4 text-white" />
            ) : (
              <Bot className="w-4 h-4 text-white" />
            )}
          </div>

          {/* Message Content */}
          <div className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-secondary text-white"
              : message.type === "status"
              ? "bg-amber-50 border border-amber-200 text-amber-800"
              : message.type === "summary"
              ? "bg-primary/5 border border-primary/20 text-gray-900"
              : "bg-gray-100 text-gray-900"
          }`}>
            {message.type === "status" && (
              <div className="flex items-center mb-2">
                <Clock className="w-4 h-4 mr-2" />
                <span className="text-sm font-medium">Processing...</span>
              </div>
            )}
            
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content.split('\n').map((line, index) => {
                if (line.startsWith('**') && line.endsWith('**')) {
                  return (
                    <div key={index} className="font-semibold text-gray-900 mb-1">
                      {line.slice(2, -2)}
                    </div>
                  );
                }
                if (line.includes('•') || line.includes('-')) {
                  return (
                    <div key={index} className="flex items-start mb-1">
                      <span className="mr-2">•</span>
                      <span>{line.replace(/^[•\-]\s*/, '').trim()}</span>
                    </div>
                  );
                }
                return <div key={index} className={index > 0 ? "mt-1" : ""}>{line}</div>;
              })}
            </div>
            
            <div className={`text-xs mt-2 flex items-center justify-between ${
              isUser ? "text-white/70" : "text-gray-500"
            }`}>
              <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              {!isUser && message.isAIGenerated && (
                <div className="flex items-center ml-2">
                  <Sparkles className="w-3 h-3 mr-1" />
                  <span className="text-xs">AI</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    );
  });

  // Optimized input change handler
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/kyc")}
            className="text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back
          </Button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">AGSA Assistant</h1>
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-1 ${isInitializing ? 'bg-yellow-500' : 'bg-green-500'}`}></div>
                <span className="text-xs text-gray-500">
                  {isInitializing ? 'Connecting...' : 'Online'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <Button variant="outline" size="sm">
          <FileText className="w-4 h-4 mr-1" />
          Export Chat
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {isInitializing ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
                <p className="text-gray-500">Connecting to AGSA Assistant...</p>
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </AnimatePresence>
          )}

          {/* Typing Indicator */}
          <AnimatePresence>
            {isTyping && !isInitializing && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex justify-start mb-4"
              >
                <div className="flex items-start space-x-2">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-center space-x-3">
            <div className="flex-1 relative">
              <Input
                value={inputValue}
                onChange={handleInputChange}
                placeholder="Type your message or ask about government schemes..."
                className="pr-12 h-12 rounded-full border-gray-300 focus:border-primary"
                disabled={isTyping || isInitializing}
              />
              <Button
                type="submit"
                size="sm"
                className="absolute right-1 top-1 h-10 w-10 rounded-full p-0"
                disabled={!inputValue.trim() || isTyping || isInitializing}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>

            {/* Voice Input FAB */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="h-12 w-12 rounded-full border-primary text-primary hover:bg-primary hover:text-white"
                disabled={isInitializing}
                onClick={() => {
                  toast({
                    title: "Voice Input",
                    description: "Voice input feature coming soon!",
                  });
                }}
              >
                <Mic className="w-5 h-5" />
              </Button>
            </motion.div>
          </form>

          <p className="text-xs text-gray-500 text-center mt-2">
            AGSA Assistant can help with government schemes, document verification, and application assistance
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chat;
