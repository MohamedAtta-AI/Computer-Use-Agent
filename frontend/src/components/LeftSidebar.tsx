import { Search, Library, History, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useApp } from "@/contexts/AppContext";
import { useState } from "react";

const LeftSidebar = () => {
  const { sessions, createSession, selectSession, isLoading, currentSession } = useApp();
  const [searchTerm, setSearchTerm] = useState("");

  const handleCreateSession = async () => {
    await createSession("New Agent Task", "New task created from UI");
  };

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-full bg-sidebar-bg border-r border-border flex flex-col">
      {/* Search */}
      <div className="p-4 flex-shrink-0">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search" 
            className="pl-10 bg-background"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Task History */}
      <div className="flex-1 px-4 overflow-y-auto min-h-0">
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <History className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-medium text-foreground">Task History</h2>
          </div>
        </div>

        {/* Sessions List */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Library className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-medium text-foreground">Sessions</h2>
          </div>
                                <div className="space-y-1">
                        {filteredSessions.map((session) => (
                          <Card 
                            key={session.id} 
                            className={`p-2 hover:bg-task-item-hover cursor-pointer transition-colors ${
                              currentSession?.id === session.id ? 'bg-task-item-hover border-primary' : ''
                            }`}
                            onClick={() => selectSession(session)}
                          >
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 bg-muted rounded-sm" />
                              <span className="text-sm text-foreground truncate">{session.title}</span>
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                              {new Date(session.created_at).toLocaleDateString()}
                            </div>
                          </Card>
                        ))}
            {filteredSessions.length === 0 && (
              <div className="text-sm text-muted-foreground p-2">
                No sessions found
              </div>
            )}
          </div>
        </div>

        {/* Prompt Gallery */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-4 h-4 bg-muted-foreground rounded-sm" />
            <h2 className="text-sm font-medium text-foreground">Prompt Gallery</h2>
          </div>
        </div>
      </div>

      {/* New Agent Task Button */}
      <div className="p-4 border-t border-border flex-shrink-0">
        <Button 
          className="w-full" 
          size="lg" 
          onClick={handleCreateSession}
          disabled={isLoading}
        >
          <Plus className="h-4 w-4 mr-2" />
          {isLoading ? "Creating..." : "New Agent Task"}
        </Button>
      </div>
    </div>
  );
};

export default LeftSidebar;
