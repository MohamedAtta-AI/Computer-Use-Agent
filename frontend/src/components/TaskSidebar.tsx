import { Plus, History, FolderOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

interface TaskItem {
  id: string;
  title: string;
  date: string;
}

interface TaskSidebarProps {
  tasks?: TaskItem[];
  onNewTask?: () => void;
}

export function TaskSidebar({ tasks = [], onNewTask }: TaskSidebarProps) {
  const defaultTasks: TaskItem[] = [
    { id: "1", title: "Audio Transcription Request", date: "2h ago" },
    { id: "2", title: "Free Zone Tax: Crucial Guidance", date: "1d ago" },
    { id: "3", title: "BSEE API Well Numbers", date: "3d ago" },
  ];

  const taskList = tasks.length > 0 ? tasks : defaultTasks;

  return (
    <div className="w-64 bg-card border-r border-panel-border flex flex-col h-full">
      {/* Search */}
      <div className="p-4 border-b border-panel-border">
        <Input 
          placeholder="Search" 
          className="w-full bg-muted/30 border-border"
        />
      </div>

      {/* Task History Section */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="p-4 border-b border-panel-border">
          <h2 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
            <History className="h-4 w-4" />
            Task History
          </h2>
        </div>
        
        <ScrollArea className="flex-1 min-h-0">
          <div className="p-4 space-y-2">
            {taskList.map((task) => (
              <div
                key={task.id}
                className="p-2 rounded-md hover:bg-muted/50 cursor-pointer transition-colors"
              >
                <div className="text-sm text-foreground font-medium line-clamp-2">
                  {task.title}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {task.date}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Library Section */}
        <div className="border-t border-panel-border">
          <div className="p-4 border-b border-panel-border">
            <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
              <FolderOpen className="h-4 w-4" />
              Library
            </h3>
          </div>
          <ScrollArea className="h-32">
            <div className="p-4 space-y-2">
              <div className="text-xs text-muted-foreground">
                Uploaded files will appear here
              </div>
            </div>
          </ScrollArea>
        </div>

        <div className="border-t border-panel-border">
          <div className="p-4">
            <h3 className="text-sm font-medium text-foreground mb-3">
              Prompt Gallery
            </h3>
            <ScrollArea className="h-24">
              <div className="space-y-2">
                <div className="text-xs text-muted-foreground">
                  Saved prompts will appear here
                </div>
              </div>
            </ScrollArea>
          </div>
        </div>
      </div>

      {/* New Agent Task Button */}
      <div className="p-4 border-t border-panel-border">
        <Button 
          onClick={onNewTask}
          className="w-full bg-agent-blue hover:bg-agent-blue-hover text-white"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Agent Task
        </Button>
      </div>
    </div>
  );
}