import { useState } from "react";
import { TaskSidebar } from "@/components/TaskSidebar";
import { VNCPanel } from "@/components/VNCPanel";
import { ChatPanel } from "@/components/ChatPanel";
import { FilePanel } from "@/components/FilePanel";

const Index = () => {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  const handleNewTask = () => {
    console.log("Starting new agent task...");
    // Here you would implement the logic to start a new task
  };

  return (
    <div className="h-screen bg-background flex overflow-hidden">
      {/* Left Sidebar - Task History */}
      <TaskSidebar onNewTask={handleNewTask} />
      
      {/* Middle Panel - VNC Connection */}
      <VNCPanel className="flex-1" />
      
      {/* Right Panel - Chat and File Management */}
      <div className="w-96 flex flex-col min-h-0">
        {/* Chat Session - Top Half */}
        <ChatPanel className="flex-1 min-h-0" />
        
        {/* File Management - Bottom Half */}
        <FilePanel className="h-80 flex-shrink-0 border-t border-panel-border" />
      </div>
    </div>
  );
};

export default Index;
