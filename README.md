# Tkmap widget

**Efficient web map canvas for tkinter.**

## Install

### Version 0.1

```bash
python -m pip install tkinter-map
```

### Developpment version

```bash
python -m pip install git+https://github.com/Moustikitos/tkinter-map.git@master
```

## Requirement

If you plan to use `Tkmap` widget with map providers sending JPEG-based tiles,
it is recommended to install the `tcl` package
[`tkimg`](https://sourceforge.net/projects/tkimg/). Binaries can be extracted
in `.tcl` directory at the root of `tkmap` package (ie the one containing the
`__init__.py` module).

## Use

```python
>>> from tkmap import widget, model
>>> canvas = widget.Tkmap()
>>> canvas.pack(fill="both", expand=True)
>>> canvas.open(model.OpenStreetMap(), zoom=10, location=(48.645272, 1.841411))
```

![Tkmap widget](./docs/widget.png)

## Features

- [x] Tile set:
  - [x] Google map
  - [x] Google satellite
  - [x] Open Street map
  - [x] Mapbox satellite
- [x] Custom map
- [x] Zoom, pan and fast pan mouse action
- [x] Latitude longitude pixel location
- [x] Tile caching

### Ongoing work

- [ ] Location format and projection
