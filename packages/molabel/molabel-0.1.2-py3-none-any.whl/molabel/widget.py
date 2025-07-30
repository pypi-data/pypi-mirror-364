import anywidget
import traitlets
from pathlib import Path


def _autocast(func): 
    def inner(example): 
        out = func(example)
        if hasattr(out, "_display_"):
            return str(out)
        if hasattr(out, "_repr_markdown_"):
            return str(out)
        if hasattr(out, "_repr_html_"):
            return str(out)
        return out
    return inner

# Default shortcuts with Alt modifier (using event.code format)
_default_shortcuts = {
    "Alt+1": "prev",
    "Alt+2": "yes", 
    "Alt+3": "no",
    "Alt+4": "skip",
    "Alt+5": "focus_notes",
    "Alt+6": "speech_notes"
}

# Default gamepad shortcuts
_default_gamepad_shortcuts = {
    "button_0": "yes",     # Often A button
    "button_1": "no",      # Often B button  
    "button_2": "skip",    # Often X button
    "button_3": "prev",    # Often Y button
    "button_4": "speech_notes",  # Often left bumper
    "button_6": "focus_notes",   # Often left trigger
}

class SimpleLabel(anywidget.AnyWidget):
    """
    A simple label widget that allows you to label examples.

    You can assign keyboard/gamepad shortcuts to the widget for all the possible actions: 
    
    - `prev` - go to the previous example
    - `yes` - label the example as yes
    - `no` - label the example as no
    - `skip` - skip the example
    - `focus_notes` - focus the notes field
    - `speech_notes` - start/stop speech recognition

    Be careful with the shortcuts, as they are global and will override the default shortcuts assigned to your notebook environment. You also cannot override the default shortcuts of the browser with this widget.

    Parameters
    ----------
    examples : list
        A list of examples to label.
    render : function
        A function that renders an example.
    notes : bool, optional
        Whether to show the notes field, default is True.
    shortcuts : dict, optional
        A dictionary of shortcuts for the keyboard. Syntax is `{"Alt+1": "prev", ...}`.
    gamepad_shortcuts : dict, optional
        A dictionary of gamepad shortcuts. Syntax is `{"button_0": "yes", ...}`.
    """
    _esm = Path(__file__).parent / "static" / "widget.js"
    _css = Path(__file__).parent / "static" / "widget.css"
    
    # Widget state
    examples = traitlets.List([]).tag(sync=True)
    notes = traitlets.Bool(True).tag(sync=True)
    shortcuts = traitlets.Dict({}).tag(sync=True)
    gamepad_shortcuts = traitlets.Dict({}).tag(sync=True)
    
    # Current state
    current_index = traitlets.Int(0).tag(sync=True)
    annotations = traitlets.List([]).tag(sync=True)
    
    def __init__(self, examples, render, notes=True, shortcuts=_default_shortcuts, gamepad_shortcuts=_default_gamepad_shortcuts):
        super().__init__()
        render_func = _autocast(render)
        self.examples = [{**ex, "_html": render_func(ex)} for ex in examples]
        self.notes = notes
        
        # Use provided shortcuts or defaults
        self.shortcuts = shortcuts if shortcuts is not None else _default_shortcuts
        self.gamepad_shortcuts = gamepad_shortcuts if gamepad_shortcuts is not None else _default_gamepad_shortcuts

    def get_annotations(self):
        """Return the collected annotations"""
        return self.annotations
