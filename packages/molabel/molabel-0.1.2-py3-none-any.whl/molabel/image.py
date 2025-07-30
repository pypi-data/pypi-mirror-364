import anywidget
import traitlets
import base64
from pathlib import Path

def to_src(path: str) -> str:
    """Converts a path to a base64 string if it's a local file."""
    if path.startswith("http"):
        return path
    path_obj = Path(path)
    with open(path_obj, "rb") as f:
        return f"data:image/{path_obj.suffix[1:]};base64," + base64.b64encode(f.read()).decode("utf-8")

class ImageLabel(anywidget.AnyWidget):
    """
    An annotation tool for images.

    Args:
        paths (list): A list of paths to images to annotate.
        classes (list, optional): A list of classes to use for annotation. Defaults to None.
    """
    _esm = (Path(__file__).parent / "static" / "image-widget.js").read_text()
    _css = (Path(__file__).parent / "static" / "image-widget.css").read_text()
    
    srcs = traitlets.List([]).tag(sync=True)
    annotations = traitlets.List([]).tag(sync=True)
    classes = traitlets.List([]).tag(sync=True)
    colors = traitlets.Dict({}).tag(sync=True)

    def __init__(self, paths=None, classes=None, colors=None, **kwargs):
        super().__init__(**kwargs)
        if paths:
            self.srcs = [to_src(p) for p in paths]
            self.annotations = [{"src": src, "elements": []} for src in self.srcs]
        if classes:
            self.classes = classes
        if colors:
            if isinstance(colors, list):
                if len(colors) != len(self.classes):
                    raise ValueError("The length of `colors` must match the length of `classes`.")
                self.colors = dict(zip(self.classes, colors))
            else:
                self.colors = colors
