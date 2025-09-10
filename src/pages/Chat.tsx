import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, ArrowLeft, FileText, CheckCircle, Clock, User, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
  type?: "text" | "status" | "summary";
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AGSA assistant. I'm here to help you navigate government services and find schemes you're eligible for. What would you like assistance with today?",
      sender: "assistant",
      timestamp: new Date(),
      type: "text"
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentFlow, setCurrentFlow] = useState<"idle" | "eligibility" | "documents" | "summary">("idle");
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (content: string, sender: "user" | "assistant", type: "text" | "status" | "summary" = "text") => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      sender,
      timestamp: new Date(),
      type
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const simulateAssistantResponse = async (userMessage: string) => {
    setIsTyping(true);
    await new Promise(resolve => setTimeout(resolve, 1500));

    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes("scheme") || lowerMessage.includes("benefit") || lowerMessage.includes("subsidy")) {
      setCurrentFlow("eligibility");
      addMessage(
        "I'll help you find relevant government schemes. Let me check your eligibility based on your profile...",
        "assistant",
        "status"
      );
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      addMessage(
        "✅ Found 3 schemes you're eligible for:\n\n1. **Pradhan Mantri Awas Yojana** - Housing subsidy\n2. **Kisan Credit Card** - Agricultural credit\n3. **Mudra Loan Scheme** - Business loan\n\nShall I proceed to verify your documents for these schemes?",
        "assistant"
      );
    } else if (lowerMessage.includes("document") || lowerMessage.includes("verify") || lowerMessage.includes("yes")) {
      setCurrentFlow("documents");
      addMessage(
        "Let me verify your documents from DigiLocker...",
        "assistant",
        "status"
      );
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      addMessage(
        "📄 Document verification complete:\n\n✅ Aadhaar Card - Verified\n✅ PAN Card - Verified\n✅ Income Certificate - Verified\n⚠️ Bank Statement - Need recent copy\n\nWould you like me to prepare the application forms?",
        "assistant"
      );
    } else if (lowerMessage.includes("form") || lowerMessage.includes("application") || lowerMessage.includes("prepare")) {
      setCurrentFlow("summary");
      addMessage(
        "Preparing your application summary...",
        "assistant",
        "status"
      );
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      addMessage(
        "🎯 **Application Summary**\n\n**Scheme:** Pradhan Mantri Awas Yojana\n**Subsidy Amount:** ₹2,50,000\n**Processing Time:** 15-30 days\n\n**Next Steps:**\n1. Upload recent bank statement\n2. Review pre-filled application\n3. Digital signature & submit\n\nShall I proceed with the application?",
        "assistant",
        "summary"
      );
    } else {
      addMessage(
        "I understand you're looking for help with government services. I can assist you with:\n\n• Finding eligible schemes and benefits\n• Document verification\n• Application form assistance\n• Status tracking\n\nWhat specific service do you need help with?",
        "assistant"
      );
    }
    
    setIsTyping(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    addMessage(inputValue, "user");
    const userMessage = inputValue;
    setInputValue("");
    
    simulateAssistantResponse(userMessage);
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const MessageBubble = ({ message }: { message: Message }) => {
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
                if (line.startsWith('✅') || line.startsWith('⚠️') || line.startsWith('📄') || line.startsWith('🎯')) {
                  return (
                    <div key={index} className="flex items-start mb-1">
                      <span className="mr-2">{line.slice(0, 2)}</span>
                      <span>{line.slice(2).trim()}</span>
                    </div>
                  );
                }
                return <div key={index} className={index > 0 ? "mt-1" : ""}>{line}</div>;
              })}
            </div>
            
            <div className={`text-xs mt-2 ${
              isUser ? "text-white/70" : "text-gray-500"
            }`}>
              {formatTimestamp(message.timestamp)}
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

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
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                <span className="text-xs text-gray-500">Online</span>
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
          <AnimatePresence>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          <AnimatePresence>
            {isTyping && (
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
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message or ask about government schemes..."
                className="pr-12 h-12 rounded-full border-gray-300 focus:border-primary"
                disabled={isTyping}
              />
              <Button
                type="submit"
                size="sm"
                className="absolute right-1 top-1 h-10 w-10 rounded-full p-0"
                disabled={!inputValue.trim() || isTyping}
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