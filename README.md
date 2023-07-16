# Tkmap widget

**Efficient web map canvas for tkinter.**

## Install

```bash
python -m pip install tkinter-map
```

## Requirement

If you plan to use `Tkmap` widget with map providers sending JPEG-based tiles,
it is recommended to install the `tcl` package
[`tkimg`](https://sourceforge.net/projects/tkimg/). Binaries can be extracted in `.tcl` directory at the root of `tkmap` package.

## Use

```python
>>> from tkmap import widget, model
>>> canvas = widget.Tkmap()
>>> canvas.pack(fill="both", expand=True)
>>> canvas.open(model.OpenStreetMap(), zoom=10, location=(48.645272, 1.841411))
```

![Tkmap widget](/widget.png)
