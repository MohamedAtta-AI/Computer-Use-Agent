import Header from "@/components/Header";
import LeftSidebar from "@/components/LeftSidebar";
import VncPanel from "@/components/VncPanel";
import ChatPanel from "@/components/ChatPanel";
import FilePanel from "@/components/FilePanel";

const Index = () => {
  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <div className="flex flex-1 min-h-0">
        {/* Left Sidebar */}
        <div className="w-80 flex-shrink-0">
          <LeftSidebar />
        </div>
        
        {/* Middle Panel - VNC */}
        <div className="flex-1 min-w-0">
          <VncPanel />
        </div>
        
        {/* Right Panel - Split between Chat and File Management */}
        <div className="w-96 flex-shrink-0 flex flex-col">
          <div className="flex-1 min-h-0">
            <ChatPanel />
          </div>
          <div className="h-64 flex-shrink-0">
            <FilePanel />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
