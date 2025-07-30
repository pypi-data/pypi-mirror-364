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

## 💡 Why BFSMRO?

Python's standard MRO only searches upward in the inheritance tree. BFSMRO adds downward lookup while maintaining:

1. **Backward Compatibility**: Normal MRO has priority
2. **Binding Consistency**: Methods use caller's context (`self`/`cls`)
3. **Dynamic Discovery**: Find methods added after class definition

This enables novel patterns like:

```python
# Framework core remains unchanged
class Core: pass

class PluginA(Core):
    def feature_a(self):
        return f"Feature A from plugin, used by {self.__class__.__name__}"

class PluginB(Core):
    def feature_b(self):
        return f"Feature B from plugin, used by {self.__class__.__name__}"

# Core can now access plugin features without knowing about them
with BFSMRO(Core()) as enhanced:
    print(enhanced.feature_a())  # → "Feature A from plugin, used by Core"
    print(enhanced.feature_b())  # → "Feature B from plugin, used by Core"
```
Perfect for plugin architectures, testing scenarios, and exploratory programming where you want to access subclass functionality dynamically

## 🚀 Usage Guide

### ⚠️ Critical Limitation: Name Shadowing

Due to Python's scoping rules, using the same name in both the expression and as clause causes issues:

**Classes for following examples:**
```python
from bfs_mro import BFSMRO

class Wizard: pass
class WhiteWizard(Wizard):
    @classmethod
    def cast_light(cls):
        return f"{cls.__name__} casts light"
    
    def heal(self):
        return f"A {self.__class__.__name__} heals"
```

**Outside functions**: works once, then breaks subsequent usage:
```python
with BFSMRO(Wizard) as Wizard:
    print(Wizard.cast_light())  # This works
# But now Wizard is the proxy object, not the class!

wizard = Wizard() # ❌ TypeError: 'UniversalProxy' object is not callable
with BFSMRO(wizard) as wizard:
    print(wizard.heal())
```
**Inside functions**: fails immediately:
```python
def bad_example():
  with BFSMRO(Wizard) as Wizard: # "UnboundLocalError: cannot access local variable 'Wizard' where it is not associated with a value"
    Wizard.cast_light()

bad_example()
```

✅ **Solution 1: Use Different Names**

Use different name in the as clause:
```python
def good_example():
    with BFSMRO(Wizard) as EnhancedWizard:
        assert EnhancedWizard.cast_light() == "Wizard casts light"
        
    wizard = Wizard()
    with BFSMRO(wizard) as enhanced_wizard:
        assert enhanced_wizard.heal() == "A Wizard heals"
```

✅ **Solution 2: Preserve Original Name**

Store the original class/instance in a temporary variable:
```python
_Wizard = Wizard

def good_example():
    with BFSMRO(_Wizard) as Wizard:
        assert Wizard.cast_light() == "Wizard casts light"
        
    wizard = _Wizard()
    with BFSMRO(wizard) as wizard:
        assert wizard.heal() == "A Wizard heals"
```

### 🔍 Method Binding Semantics

BFSMRO preserves Python's standard method binding behavior - the calling object determines `cls`/`self`, not the defining class:

```python
class Wizard: pass

class WhiteWizard(Wizard):
    @classmethod
    def whoami(cls):
        return f"Method called on {cls.__name__}"
    
    def instance_class(self):
        return f"Instance of {self.__class__.__name__}"

# Class method: cls = Wizard (the enhanced class, not WhiteWizard!)
with BFSMRO(Wizard) as EnhancedWizard:
    print(EnhancedWizard.whoami())  # → "Method called on Wizard"

# Instance method: self = Wizard() (the enhanced instance)
wizard = Wizard()
with BFSMRO(wizard) as enhanced_wizard:
    print(enhanced_wizard.instance_class())  # → "Instance of Wizard"
```
This matches Python's normal behavior. Just like `super().__init__()` passes the current self to the parent method, BFSMRO passes the enhanced object to borrowed methods.

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
