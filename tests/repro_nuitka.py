print("Hello from Nuitka Minimal Repro!")
import sys
print(f"Python: {sys.version}")
try:
    import PyQt6.QtWidgets
    print("PyQt6 imported successfully")
except ImportError:
    print("PyQt6 not found")
