import logging
import pytest
from bfs_mro import BFSMRO


class Adventurer:
    @staticmethod
    def get_country_name():
        return 'Mrotopia'

    def explore(self):
        return f"A {self.__class__.__name__} is exploring"

    @classmethod
    def rest(cls):
        return f"{cls.__name__} rests"


class Wizard(Adventurer):
    def cast(self):
        return f"A {self.__class__.__name__} casts a generic spell"


class WhiteWizard(Wizard):
    @classmethod
    def cast_light(cls):
        return f"{cls.__name__} casts light"

    @staticmethod
    def get_element():
        return "light"

    def heal(self):
        return f"A {self.__class__.__name__} heals with light"


class DarkWizard(Wizard):
    @classmethod
    def cast_shadow(cls):
        return f"{cls.__name__} casts shadow"

    @staticmethod
    def get_element():
        return "shadow"

    def curse(self):
        return f"A {self.__class__.__name__} curses with shadow"

# We use _Wizard to hold a reference to the Wizard class
# so we can safely use 'as Wizard' in the context manager
# without triggering UnboundLocalError due to name shadowing.

# Alternatively, if we're working inside a function, we must change the variable
# after as - and to change what's used in assertion as well.
_Wizard = Wizard

def test_mro_lookup_original_in_assertion():
    """Adventurer's methods should be found via MRO (up)."""
   
    with BFSMRO(_Wizard) as Wizard:
        assert Wizard.get_country_name() == "Mrotopia"
        assert Wizard.rest() == "Wizard rests"
    with BFSMRO(_Wizard()) as wizard:
        assert wizard.explore() == "A Wizard is exploring"

def test_mro_lookup_original_in_addon():
    """Adventurer's methods should be found via MRO (up)."""

    with BFSMRO(Wizard) as _Wizard:
        assert _Wizard.get_country_name() == "Mrotopia"
        assert _Wizard.rest() == "Wizard rests"
    wizard = Wizard()
    with BFSMRO(wizard) as _wizard:
        assert _wizard.explore() == "A Wizard is exploring"


def test_direct_method_no_lookup_original_in_assertion():
    """Wizard's own method should be found directly."""
    with BFSMRO(_Wizard()) as wizard:
        assert wizard.cast() == "A Wizard casts a generic spell"


def test_direct_method_no_lookup_original_in_addon():
    """Wizard's own method should be found directly."""
    wizard = Wizard()
    with BFSMRO(wizard) as _wizard:
        assert _wizard.cast() == "A Wizard casts a generic spell"

def test_bfs_lookup_original_in_assertion():
    """White/DarkWizard classmethods should be found via BFS (down)."""
    with BFSMRO(_Wizard) as Wizard:
        assert "Wizard casts shadow" == Wizard.cast_shadow()
        assert "Wizard casts light" == Wizard.cast_light()
        assert "light" == Wizard.get_element() # because LightWizard is defined earlier
    with BFSMRO(_Wizard()) as wizard:
        assert wizard.curse() == "A Wizard curses with shadow"
        assert wizard.heal() == "A Wizard heals with light"


def test_bfs_lookup_original_in_addon():
    """White/DarkWizard classmethods should be found via BFS (down)."""
    with BFSMRO(Wizard) as _Wizard:
        assert _Wizard.cast_shadow() == "Wizard casts shadow"
        assert _Wizard.cast_light() == "Wizard casts light"
        assert _Wizard.get_element() == "light" # because LightWizard is defined earlier
    wizard = Wizard()
    with BFSMRO(wizard) as _wizard:
        assert _wizard.curse() == "A Wizard curses with shadow"
        assert _wizard.heal() == "A Wizard heals with light"


def test_not_found_original_in_assertion():
    """Should raise AttributeError when method is not found."""
    with BFSMRO(_Wizard) as Wizard:
        with pytest.raises(AttributeError):
            Wizard.missing_method()

    with BFSMRO(_Wizard()) as wizard:
        with pytest.raises(AttributeError):
            wizard.missing_action()


def test_not_found_original_in_addon():
    """Should raise AttributeError when method is not found."""
    with BFSMRO(Wizard) as _Wizard:
        with pytest.raises(AttributeError):
            _Wizard.missing_method()

    wizard = Wizard()
    with BFSMRO(wizard) as _wizard:
        with pytest.raises(AttributeError):
            _wizard.missing_action()


def test_debug_mode_original_in_assertion(caplog):
    """Debug mode should log BFS lookup and enhance errors."""
    with caplog.at_level(logging.DEBUG):
        with BFSMRO(_Wizard, debug=True) as Wizard:
            with pytest.raises(AttributeError):
                Wizard.missing_method()

        assert any("searching subclasses" in record.message for record in caplog.records)


def test_debug_mode_original_in_addon(caplog):
    """Debug mode should log BFS lookup and enhance errors."""
    with caplog.at_level(logging.DEBUG):
        with BFSMRO(Wizard, debug=True) as _Wizard:
            with pytest.raises(AttributeError):
                _Wizard.missing_method()

        assert any("searching subclasses" in record.message for record in caplog.records)


def test_thread_safe_original_in_assertion():
    """Thread-safe mode should not crash."""
    with BFSMRO(_Wizard, thread_safe=True) as Wizard:
        assert Wizard.rest() == "Wizard rests"

    with BFSMRO(_Wizard(), thread_safe=True) as wizard:
        assert wizard.explore() == "A Wizard is exploring"


def test_thread_safe_original_in_addon():
    """Thread-safe mode should not crash."""
    with BFSMRO(Wizard, thread_safe=True) as _Wizard:
        assert _Wizard.rest() == "Wizard rests"

    wizard = Wizard()
    with BFSMRO(wizard, thread_safe=True) as _wizard:
        assert _wizard.explore() == "A Wizard is exploring"
