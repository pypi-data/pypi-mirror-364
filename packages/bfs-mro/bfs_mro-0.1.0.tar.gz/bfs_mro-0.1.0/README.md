# BFSMRO

> ⚠️ **Note**: This is a **pet project** for practicing advanced Python concepts like metaprogramming, context managers, and dynamic method resolution.  
> It is not intended for production use. Features like `__slots__`, `property`, and full descriptor support are not implemented.

BFS-enhanced method lookup for Python classes and instances.

This context manager allows a class or instance to access `@classmethod`, `@staticmethod`, and instance methods from its subclasses — even if they’re not in the MRO.

It uses **Breadth-First Search (BFS)** to find methods downward in the inheritance tree, while preserving normal MRO lookup (upward) as the first priority.

Ideal for dynamic plugin systems, framework extensions, and exploratory programming.

## 🔧 Features

- ✅ Works on **classes** and **instances**
- ✅ Supports `@classmethod`, `@staticmethod`, and instance methods
- ✅ Lookup order: **MRO first (up)**, then **BFS in subclasses (down)**
- ✅ Opt-in `debug` mode: logs lookup and enhances error messages
- ✅ Thread-safe mode available
- ✅ Zero changes to existing classes

## 🚀 Usage

```python
from bfs_mro import BFSMRO

class Wizard: pass
class WhiteWizard(Wizard):
    @classmethod
    def cast_light(cls):
        return f"{cls.__name__} casts light"
    
    def heal(self):
        return f"A {self.__class__.__name__} heals"

# Enhance class to access subclass methods
with BFSMRO(Wizard) as Wizard:
    print(Wizard.cast_light())  # → "Wizard casts light"

# Enhance instance
wizard = Wizard()
with BFSMRO(wizard) as wizard:
    print(wizard.heal())  # -> "A Wizard heals"
```
⚠️ Name Shadowing in Functions

Due to Python’s scoping rules, you cannot use the same name in the with ... as target if it’s also used in the expression, when inside a function:
```python
def bad():
    with BFSMRO(Wizard) as Wizard:  # ❌ UnboundLocalError
        Wizard.cast_light()
```
✅ Workaround

Use a temporary name for the class or instance:
```python
_Wizard = Wizard

def good():
    with BFSMRO(_Wizard) as Wizard:
        assert Wizard.cast_light() == "Wizard casts light"
```
This allows you to preserve the original name in the as clause while avoiding the scoping conflict.


## 📦 Installation
```bash
pip install bfs-mro
```

## 🛠 Development
```bash
# Clone and install in dev mode
git clone https://github.com/AlexShchW/bfs_mro.git
cd bfs_mro
pip install -e .[dev]

# Run tests
pytest
```

📄 License
MIT — see LICENSE file.

