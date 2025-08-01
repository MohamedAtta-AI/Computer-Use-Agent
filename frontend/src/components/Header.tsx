import { Minimize2, Square, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const Header = () => {
  return (
    <div className="h-12 bg-background border-b border-border flex items-center justify-between px-4">
      {/* Left side - Logo/Title */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">S</span>
        </div>
        <h1 className="text-lg font-semibold text-foreground">Legent AI</h1>
      </div>

      {/* Right side - Window controls */}
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Minimize2 className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Square className="h-3 w-3" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground">
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default Header;