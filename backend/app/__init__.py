"""
Expose backend.app.computer_use_demo *also* as top-level
package name `computer_use_demo` so all absolute imports inside
that code keep working unchanged.
"""
import importlib
import sys

# Import the sub-package once …
_pkg = importlib.import_module(__name__ + ".computer_use_demo")
# …then register an alias so `import computer_use_demo` succeeds.
sys.modules["computer_use_demo"] = _pkg
