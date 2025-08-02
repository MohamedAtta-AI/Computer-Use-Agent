import { useState, useEffect, useRef } from "react";
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";

import { newSession, chatStream, sendMessage } from "@/lib/api";

/* ------------------------------------------------------------------ */
/* Types */
/* ------------------------------------------------------------------ */

export interface Message {
  id: string;
  type: "user" | "assistant" | "function" | "result";
  content: string;
  timestamp: Date;
}

interface ChatPanelProps {
  /**  Optional – if not provided we’ll create a brand-new backend
       session and emit it via `onSession`                        */
  sessionId?: string;
  onSession?: (id: string) => void;
  className?: string;
}

/* ------------------------------------------------------------------ */
/* Component */
/* ------------------------------------------------------------------ */

export function ChatPanel({
  sessionId: sessionIdProp,
  onSession,
  className = "",
}: ChatPanelProps) {
  /* -------------------------------- state ------------------------- */
  const [sessionId, setSessionId] = useState<string | undefined>(
    sessionIdProp
  );
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "seed",
      type: "assistant",
      content: "Hi! Tell me what task to accomplish.",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  /* --------------------------- create session --------------------- */
  useEffect(() => {
    if (sessionId) return;

    newSession()
      .then((sid) => {
        setSessionId(sid);
        onSession?.(sid);
      })
      .catch((err) => console.error("Unable to create session:", err));
  }, [sessionId, onSession]);

  /* --------------------------- stream messages -------------------- */
  useEffect(() => {
    if (!sessionId) return;

    const es = chatStream(sessionId);

    es.onmessage = (ev) => {
      try {
        const m: Message = JSON.parse(ev.data);
        m.timestamp = new Date(m.timestamp ?? Date.now());
        setMessages((prev) => [...prev, m]);
      } catch (err) {
        console.warn("Bad SSE message:", err);
      }
    };

    es.onerror = (err) => console.error("SSE error", err);
    return () => es.close();
  }, [sessionId]);

  /* ----------------------------- helpers -------------------------- */
  const scrollToBottom = () => {
    const viewport =
      scrollAreaRef.current?.querySelector<HTMLElement>(
        "[data-radix-scroll-area-viewport]"
      );
    if (viewport) viewport.scrollTop = viewport.scrollHeight;
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || !sessionId) return;

    const outbound: Message = {
      id: crypto.randomUUID(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, outbound]);
    setInputValue("");

    try {
      await sendMessage(sessionId, outbound.content);
    } catch (err) {
      console.error("sendMessage failed:", err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (date: Date) =>
    date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  /* ----------------------------- render --------------------------- */
  return (
    <div className={`bg-chat-background flex flex-col min-h-0 ${className}`}>
      {/* header */}
      <div className="p-4 border-b border-panel-border">
        <h3 className="text-sm font-medium text-foreground">Chat Session</h3>
      </div>

      {/* messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 min-h-0 p-4">
        <div className="space-y-4">
          {messages.map((m) => (
            <div key={m.id} className="flex gap-3">
              {/* avatar */}
              <div className="flex-shrink-0">
                {m.type === "user" ? (
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-agent-blue flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>

              {/* bubble */}
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    {m.type === "user" ? "You" : "Agent"}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatTime(m.timestamp)}
                  </span>
                </div>
                <Card className="p-3 bg-card whitespace-pre-wrap">
                  <p className="text-sm text-foreground">{m.content}</p>
                </Card>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* input */}
      <div className="p-4 border-t border-panel-border">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Write a message"
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="bg-agent-blue hover:bg-agent-blue-hover"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
