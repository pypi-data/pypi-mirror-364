# molabel

A simple annotation widget for labeling examples with speech recognition support.

For an interactive demo check GitHub pages [here](https://koaning.github.io/molabel/). 

## Features

![localhost_2719_](https://github.com/user-attachments/assets/58c9622d-e497-4965-a564-b8340e66da90)

- **Interactive annotation**: <kbd>Yes</kbd>/<kbd>No</kbd>/<kbd>Skip</kbd> buttons with <kbd>Previous</kbd> navigation
- **Keyboard shortcuts**: Alt+1-6 for quick navigation and actions
- **Gamepad support**: Controller input with push-to-talk speech
- **Notes field**: Text annotations with live speech transcription

## Installation

```bash
uv pip install molabel
```

## Usage

```python
from molabel import SimpleLabel

def render_example(example):
    return f"<p>{example['text']}</p>"

# Create annotation widget
widget = SimpleLabel(
    examples=[{"text": "example 1"}, {"text": "example 2"}],
    render=render_example,
    notes=True
)

# Display in notebook
widget

# Get annotations after labeling
annotations = widget.get_annotations()
```

### Custom Shortcuts

```python
widget = SimpleLabel(
    examples=examples,
    render=render_example,
    shortcuts={"Alt+Q": "prev", "Alt+W": "yes"},  # Custom keyboard
    gamepad_shortcuts={"button_7": "yes"}  # Custom gamepad
)
```

If you're keen to understand your gamepad better and how to map the buttons to actions, you can check [this notebook](https://koaning.github.io/mopad/). It will show every name of every button that you press in real time via the browser gamepad API. 

## Controls

- **Mouse**: Click buttons or microphone icon
- **Keyboard**: Alt+1 (prev), Alt+2 (yes), Alt+3 (no), Alt+4 (skip), Alt+5 (focus notes), Alt+6 (speech toggle)
- **Gamepad**: Button mappings with push-to-talk speech on left trigger

You can assign keyboard/gamepad shortcuts to the widget for all the possible actions: 

- `prev` - go to the previous example
- `yes` - label the example as yes
- `no` - label the example as no
- `skip` - skip the example
- `focus_notes` - focus the notes field
- `speech_notes` - start/stop speech recognition

## Requirements

- Modern web browser for Speech Recognition/Gamepad API support
- Microphone access for speech features
