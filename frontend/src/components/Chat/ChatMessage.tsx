import React from "react";
import ReactMarkdown from "react-markdown";
import { ChatMessage as ChatMessageType } from "../../types";
import {
  User,
  Bot,
  MousePointer2,
  Terminal,
  FileEdit,
  Camera,
  Monitor,
  MousePointerClick,
  Scroll,
  Move,
  Type,
  Key,
  Clock,
  Hand,
  Command,
} from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const getMessageConfig = (type: ChatMessageType["type"]) => {
    switch (type) {
      case "user":
        return {
          icon: User,
          bgColor: "bg-blue-50",
          textColor: "text-gray-900",
          label: "User",
        };
      case "assistant":
        return {
          icon: Bot,
          bgColor: "bg-gray-50",
          textColor: "text-gray-800",
          label: "Assistant",
        };
      case "function_call":
        return {
          icon: MousePointer2,
          bgColor: "bg-amber-50",
          textColor: "text-amber-900",
          borderColor: "border-amber-300",
          label: "Tool Use",
        };
      case "function_result":
        return {
          icon: MousePointer2,
          bgColor: "bg-amber-50",
          textColor: "text-amber-900",
          borderColor: "border-amber-300",
          label: "Tool Result",
        };
      case "event":
        return {
          icon: MousePointer2,
          bgColor: "bg-amber-50",
          textColor: "text-amber-900",
          borderColor: "border-amber-300",
          label: "Tool Action",
        };
      case "screenshot":
        return {
          icon: Camera,
          bgColor: "bg-indigo-50",
          textColor: "text-indigo-900",
          label: "Screenshot",
        };
    }
  };

  // Helper function to extract text content from message
  const getMessageText = (content: any): string => {
    if (typeof content === "string") {
      return content;
    }
    if (typeof content === "object" && content !== null) {
      if (content.text) {
        return content.text;
      }
      if (content.content) {
        return getMessageText(content.content);
      }
      // If it's an object but no text property, stringify it
      return JSON.stringify(content);
    }
    return String(content);
  };

  // Format tool name for display (e.g., "mouse_click" -> "Mouse Click")
  const formatToolName = (toolName: string): string => {
    if (!toolName) return "Tool";
    return toolName
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  // Get tool-specific icon and color configuration
  const getToolConfig = (toolName: string, action?: string) => {
    const normalizedName = toolName.toLowerCase();
    const normalizedAction = action?.toLowerCase() || "";

    // ===== COMPUTER TOOL ACTIONS =====

    // Screenshot
    if (
      normalizedAction === "screenshot" ||
      normalizedAction.includes("screenshot")
    ) {
      return {
        icon: Camera,
        bgColor: "bg-indigo-50",
        textColor: "text-indigo-900",
        borderColor: "border-indigo-300",
        iconColor: "text-indigo-600",
        label: "Screenshot",
      };
    }

    // Click actions - different icons for different click types
    if (
      normalizedAction === "left_click" ||
      normalizedAction === "double_click" ||
      normalizedAction === "triple_click"
    ) {
      return {
        icon: MousePointerClick,
        bgColor: "bg-blue-50",
        textColor: "text-blue-900",
        borderColor: "border-blue-300",
        iconColor: "text-blue-600",
        label:
          normalizedAction === "double_click"
            ? "Double Click"
            : normalizedAction === "triple_click"
            ? "Triple Click"
            : "Left Click",
      };
    }

    if (normalizedAction === "right_click") {
      return {
        icon: MousePointerClick,
        bgColor: "bg-purple-50",
        textColor: "text-purple-900",
        borderColor: "border-purple-300",
        iconColor: "text-purple-600",
        label: "Right Click",
      };
    }

    if (normalizedAction === "middle_click") {
      return {
        icon: MousePointerClick,
        bgColor: "bg-pink-50",
        textColor: "text-pink-900",
        borderColor: "border-pink-300",
        iconColor: "text-pink-600",
        label: "Middle Click",
      };
    }

    if (
      normalizedAction.includes("click") ||
      normalizedAction.includes("mouse_down") ||
      normalizedAction.includes("mouse_up")
    ) {
      return {
        icon: MousePointerClick,
        bgColor: "bg-cyan-50",
        textColor: "text-cyan-900",
        borderColor: "border-cyan-300",
        iconColor: "text-cyan-600",
        label: "Click",
      };
    }

    // Mouse movement
    if (
      normalizedAction === "mouse_move" ||
      normalizedAction.includes("move")
    ) {
      return {
        icon: Move,
        bgColor: "bg-teal-50",
        textColor: "text-teal-900",
        borderColor: "border-teal-300",
        iconColor: "text-teal-600",
        label: "Move Mouse",
      };
    }

    // Drag
    if (normalizedAction.includes("drag")) {
      return {
        icon: Hand,
        bgColor: "bg-rose-50",
        textColor: "text-rose-900",
        borderColor: "border-rose-300",
        iconColor: "text-rose-600",
        label: "Drag",
      };
    }

    // Scroll
    if (normalizedAction === "scroll" || normalizedAction.includes("scroll")) {
      return {
        icon: Scroll,
        bgColor: "bg-sky-50",
        textColor: "text-sky-900",
        borderColor: "border-sky-300",
        iconColor: "text-sky-600",
        label: "Scroll",
      };
    }

    // Type/Keyboard input
    if (normalizedAction === "type" || normalizedAction.includes("type")) {
      return {
        icon: Type,
        bgColor: "bg-amber-50",
        textColor: "text-amber-900",
        borderColor: "border-amber-300",
        iconColor: "text-amber-600",
        label: "Type",
      };
    }

    // Key press
    if (normalizedAction === "key" || normalizedAction === "hold_key") {
      return {
        icon: Key,
        bgColor: "bg-yellow-50",
        textColor: "text-yellow-900",
        borderColor: "border-yellow-300",
        iconColor: "text-yellow-600",
        label: normalizedAction === "hold_key" ? "Hold Key" : "Key Press",
      };
    }

    // Wait
    if (normalizedAction === "wait") {
      return {
        icon: Clock,
        bgColor: "bg-slate-50",
        textColor: "text-slate-900",
        borderColor: "border-slate-300",
        iconColor: "text-slate-600",
        label: "Wait",
      };
    }

    // Cursor position
    if (
      normalizedAction === "cursor_position" ||
      normalizedAction.includes("cursor")
    ) {
      return {
        icon: MousePointer2,
        bgColor: "bg-lime-50",
        textColor: "text-lime-900",
        borderColor: "border-lime-300",
        iconColor: "text-lime-600",
        label: "Cursor Position",
      };
    }

    // ===== TOOL TYPES =====

    if (normalizedName === "computer") {
      return {
        icon: Monitor,
        bgColor: "bg-slate-50",
        textColor: "text-slate-900",
        borderColor: "border-slate-300",
        iconColor: "text-slate-600",
        label: "Computer Action",
      };
    } else if (normalizedName.includes("bash") || normalizedName === "bash") {
      return {
        icon: Terminal,
        bgColor: "bg-emerald-50",
        textColor: "text-emerald-900",
        borderColor: "border-emerald-300",
        iconColor: "text-emerald-600",
        label: "Bash Command",
      };
    } else if (
      normalizedName.includes("edit") ||
      normalizedName.includes("str_replace")
    ) {
      return {
        icon: FileEdit,
        bgColor: "bg-violet-50",
        textColor: "text-violet-900",
        borderColor: "border-violet-300",
        iconColor: "text-violet-600",
        label: "File Edit",
      };
    } else {
      // Default tool configuration
      return {
        icon: Command,
        bgColor: "bg-gray-50",
        textColor: "text-gray-900",
        borderColor: "border-gray-300",
        iconColor: "text-gray-600",
        label: "Tool Use",
      };
    }
  };

  // Extract clean tool information from message
  const getToolInfo = () => {
    // Check if message content is a tool_use JSON object (from assistant messages)
    let toolUseData = null;

    // First check if content is already an object with tool_use type
    if (
      message.type === "assistant" &&
      typeof message.content === "object" &&
      message.content !== null
    ) {
      if (message.content.type === "tool_use") {
        toolUseData = message.content;
      }
      // Check if content is an array containing tool_use blocks
      else if (Array.isArray(message.content)) {
        const toolUseBlock = message.content.find(
          (block: any) => block && block.type === "tool_use"
        );
        if (toolUseBlock) {
          toolUseData = toolUseBlock;
        }
      }
    }

    // Check if content is a string that's JSON (common after extractTextContent)
    if (
      !toolUseData &&
      message.type === "assistant" &&
      typeof message.content === "string"
    ) {
      try {
        const parsed = JSON.parse(message.content);
        if (parsed && parsed.type === "tool_use") {
          toolUseData = parsed;
        }
        // Also check if it's an array of blocks
        else if (Array.isArray(parsed)) {
          const toolUseBlock = parsed.find(
            (block: any) => block && block.type === "tool_use"
          );
          if (toolUseBlock) {
            toolUseData = toolUseBlock;
          }
        }
      } catch (e) {
        // Not JSON, try to find tool_use pattern in the string
        if (
          message.content.includes('"type":"tool_use"') ||
          message.content.includes("'type':'tool_use'")
        ) {
          try {
            // Try to extract JSON from the string
            const jsonMatch = message.content.match(
              /\{[\s\S]*"type"\s*:\s*"tool_use"[\s\S]*\}/
            );
            if (jsonMatch) {
              const parsed = JSON.parse(jsonMatch[0]);
              if (parsed && parsed.type === "tool_use") {
                toolUseData = parsed;
              }
            }
          } catch (e2) {
            // Still not parseable, ignore
          }
        }
      }
    }

    if (toolUseData) {
      const toolName = toolUseData.name || "tool";
      const formattedToolName = formatToolName(toolName);
      let toolInput = "";
      let actionDescription = "";

      if (toolUseData.input) {
        const input = toolUseData.input;

        // For computer tool actions
        if (toolName === "computer") {
          if (input.action) {
            // Format action descriptions
            if (
              input.action === "left_click" ||
              input.action === "right_click"
            ) {
              actionDescription =
                input.action === "left_click" ? "Left Click" : "Right Click";
              if (input.coordinate && Array.isArray(input.coordinate)) {
                toolInput = `(${input.coordinate[0]}, ${input.coordinate[1]})`;
              }
            } else if (input.action === "type") {
              actionDescription = "Type";
              if (input.text) {
                const preview = input.text.substring(0, 30);
                toolInput = `"${preview}${
                  input.text.length > 30 ? "..." : ""
                }"`;
              }
            } else if (input.action === "key") {
              actionDescription = "Key Press";
              if (input.text) {
                toolInput = input.text;
              }
            } else if (input.action === "screenshot") {
              actionDescription = "Screenshot";
            } else {
              actionDescription = formatToolName(input.action);
            }
          }
        }
        // For bash commands
        else if (toolName.includes("bash") || input.command) {
          actionDescription = "Execute";
          if (input.command) {
            toolInput = input.command;
          }
        }
        // For edit operations
        else if (toolName.includes("edit") || input.path || input.file_path) {
          actionDescription = "Edit File";
          if (input.path || input.file_path) {
            toolInput = input.path || input.file_path;
          } else if (input.file_name) {
            toolInput = input.file_name;
          }
        }
        // Fallback for other tools
        else {
          if (input.coordinate && Array.isArray(input.coordinate)) {
            toolInput = `(${input.coordinate[0]}, ${input.coordinate[1]})`;
          } else if (input.text) {
            const preview = input.text.substring(0, 50);
            toolInput = `"${preview}${input.text.length > 50 ? "..." : ""}"`;
          } else if (input.command) {
            toolInput = input.command;
          } else if (input.path || input.file_path) {
            toolInput = input.path || input.file_path;
          } else if (input.action) {
            actionDescription = formatToolName(input.action);
          }
        }
      }

      return {
        toolName: formattedToolName,
        rawToolName: toolName,
        toolInput,
        actionDescription,
      };
    }

    if (message.type === "event" && message.kind) {
      const toolName = message.kind;
      const formattedToolName = formatToolName(toolName);
      let toolInput = "";
      let actionDescription = "";

      if (message.payload?.input) {
        const input = message.payload.input;
        // Extract meaningful information from input
        if (typeof input === "object") {
          // For computer tool actions
          if (toolName === "computer" || toolName.includes("computer")) {
            if (input.action) {
              if (
                input.action === "left_click" ||
                input.action === "right_click"
              ) {
                actionDescription =
                  input.action === "left_click" ? "Left Click" : "Right Click";
                if (input.coordinate && Array.isArray(input.coordinate)) {
                  toolInput = `(${input.coordinate[0]}, ${input.coordinate[1]})`;
                } else if (input.x !== undefined && input.y !== undefined) {
                  toolInput = `(${input.x}, ${input.y})`;
                }
              } else if (input.action === "type") {
                actionDescription = "Type";
                if (input.text) {
                  const preview = input.text.substring(0, 30);
                  toolInput = `"${preview}${
                    input.text.length > 30 ? "..." : ""
                  }"`;
                }
              } else if (input.action === "key") {
                actionDescription = "Key Press";
                if (input.text) {
                  toolInput = input.text;
                }
              } else {
                actionDescription = formatToolName(input.action);
              }
            }
          }
          // For bash commands
          else if (toolName.includes("bash") || input.command) {
            actionDescription = "Execute";
            if (input.command) {
              toolInput = input.command;
            }
          }
          // For edit operations
          else if (toolName.includes("edit") || input.path || input.file_path) {
            actionDescription = "Edit File";
            if (input.path || input.file_path) {
              toolInput = input.path || input.file_path;
            }
          }
          // Fallback
          else {
            if (input.coordinate && Array.isArray(input.coordinate)) {
              toolInput = `(${input.coordinate[0]}, ${input.coordinate[1]})`;
            } else if (input.x !== undefined && input.y !== undefined) {
              toolInput = `(${input.x}, ${input.y})`;
            } else if (input.text) {
              const preview = input.text.substring(0, 50);
              toolInput = `"${preview}${input.text.length > 50 ? "..." : ""}"`;
            } else if (input.command) {
              toolInput = input.command;
            } else if (input.path || input.file_path) {
              toolInput = input.path || input.file_path;
            }
          }
        } else if (typeof input === "string") {
          toolInput = input.substring(0, 50);
          if (input.length > 50) {
            toolInput += "...";
          }
        }
      }

      return {
        toolName: formattedToolName,
        rawToolName: toolName,
        toolInput,
        actionDescription,
      };
    }

    if (message.type === "function_call" && message.functionName) {
      return {
        toolName: formatToolName(message.functionName),
        rawToolName: message.functionName,
        toolInput: "",
        actionDescription: "",
      };
    }

    return null;
  };

  const toolInfo = getToolInfo();
  // Check if this is a tool message (either explicit type or contains tool_use data)
  const isToolMessage =
    message.type === "function_call" ||
    message.type === "function_result" ||
    message.type === "event" ||
    (message.type === "assistant" && toolInfo !== null);

  // Get tool-specific config if it's a tool message
  let toolConfig = null;
  if (isToolMessage && toolInfo) {
    // Use raw tool name if available, otherwise try to extract from message
    let actualToolName = toolInfo.rawToolName || "";
    let actionDescription = toolInfo.actionDescription || "";

    // Fallback: check message content or event kind
    if (!actualToolName) {
      if (message.type === "event" && message.kind) {
        actualToolName = message.kind;
      } else if (
        message.type === "assistant" &&
        typeof message.content === "object" &&
        message.content !== null
      ) {
        if (message.content.type === "tool_use" && message.content.name) {
          actualToolName = message.content.name;
          // Extract action from input if available
          if (message.content.input && message.content.input.action) {
            actionDescription = message.content.input.action;
          }
        } else if (Array.isArray(message.content)) {
          const toolUseBlock = message.content.find(
            (block: any) => block && block.type === "tool_use"
          );
          if (toolUseBlock && toolUseBlock.name) {
            actualToolName = toolUseBlock.name;
            if (toolUseBlock.input && toolUseBlock.input.action) {
              actionDescription = toolUseBlock.input.action;
            }
          }
        }
      }
    }

    toolConfig = getToolConfig(actualToolName, actionDescription);
  }

  // Use tool message config if it's a tool message, otherwise use regular config
  const config =
    isToolMessage && toolInfo && toolConfig
      ? toolConfig
      : getMessageConfig(message.type);

  const Icon = config.icon;
  const messageText = getMessageText(message.content);

  return (
    <div
      className={`p-3 rounded-lg ${config.bgColor} ${
        isToolMessage
          ? `border ${config.borderColor || "border-yellow-300"}`
          : ""
      } mb-3`}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <Icon
            className={`w-5 h-5 ${
              isToolMessage && toolConfig
                ? toolConfig.iconColor
                : "text-gray-500"
            } mt-0.5`}
          />
        </div>
        <div className="flex-1 min-w-0">
          {!isToolMessage && (
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-gray-600">
                {config.label}
              </span>
              <span className="text-xs text-gray-400">{message.timestamp}</span>
            </div>
          )}
          <div className={`text-sm ${config.textColor}`}>
            {isToolMessage && toolInfo ? (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-semibold ${config.textColor}`}
                    >
                      {toolInfo.actionDescription || toolInfo.toolName}
                    </span>
                    {toolInfo.actionDescription &&
                      toolInfo.toolName !== toolInfo.actionDescription && (
                        <span
                          className={`text-xs opacity-70 ${config.textColor}`}
                        >
                          {toolInfo.toolName}
                        </span>
                      )}
                  </div>
                  <span className={`text-xs opacity-60 ${config.textColor}`}>
                    {message.timestamp}
                  </span>
                </div>
                {toolInfo.toolInput && (
                  <div className="mt-1.5">
                    <p
                      className={`text-xs font-mono bg-white/50 px-2 py-1 rounded border ${
                        config.textColor
                      } ${config.borderColor || "border-gray-300"}`}
                    >
                      {toolInfo.toolInput}
                    </p>
                  </div>
                )}
                {message.type === "function_result" && messageText && (
                  <p className="text-xs mt-2 opacity-80 italic">
                    {messageText}
                  </p>
                )}
              </div>
            ) : message.type === "screenshot" && message.url ? (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-blue-700">
                    {config.label}
                  </span>
                  <span className="text-xs text-blue-600">
                    {message.timestamp}
                  </span>
                </div>
                <img
                  src={`http://localhost:8000${message.url}`}
                  alt="Screenshot"
                  className="mt-2 max-w-full h-auto rounded border"
                  style={{ maxHeight: "200px" }}
                />
              </div>
            ) : (
              <div className="break-words leading-relaxed text-base">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => (
                      <p className="mb-2 last:mb-0">{children}</p>
                    ),
                    h1: ({ children }) => (
                      <h1 className="text-2xl font-bold mb-2 mt-4 first:mt-0">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-xl font-bold mb-2 mt-4 first:mt-0">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-lg font-bold mb-2 mt-4 first:mt-0">
                        {children}
                      </h3>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc list-inside mb-2 space-y-1">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside mb-2 space-y-1">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => <li className="ml-2">{children}</li>,
                    code: ({ children, className }) => {
                      const isInline = !className;
                      if (isInline) {
                        return (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800">
                            {children}
                          </code>
                        );
                      }
                      // For code blocks (with className), render as block
                      return (
                        <code className="block bg-gray-100 p-3 rounded text-sm font-mono overflow-x-auto mb-2 text-gray-800 whitespace-pre">
                          {children}
                        </code>
                      );
                    },
                    pre: ({ children }) => (
                      <pre className="bg-gray-100 p-3 rounded text-sm font-mono overflow-x-auto mb-2 text-gray-800 whitespace-pre">
                        {children}
                      </pre>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-gray-300 pl-4 italic my-2">
                        {children}
                      </blockquote>
                    ),
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        className="text-blue-600 hover:underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-bold">{children}</strong>
                    ),
                    em: ({ children }) => (
                      <em className="italic">{children}</em>
                    ),
                  }}
                >
                  {messageText}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
