import sys
import inspect

print(f"--- Inspecting the 'deepteam' library installed in: {sys.executable} ---")

try:
    import deepteam.attacks.single_turn as single_turn
    print("\n[+] Available single-turn attacks:")
    # Inspect the module and find all class names
    class_names = [name for name, obj in inspect.getmembers(single_turn) if inspect.isclass(obj) and not name.startswith('_')]
    print(class_names)
except ImportError as e:
    print(f"Could not import single-turn attacks: {e}")

try:
    import deepteam.attacks.multi_turn as multi_turn
    print("\n[+] Available multi-turn attacks:")
    class_names = [name for name, obj in inspect.getmembers(multi_turn) if inspect.isclass(obj) and not name.startswith('_')]
    print(class_names)
except ImportError as e:
    print(f"Could not import multi-turn attacks: {e}")