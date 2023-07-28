# Tkmap widget

**Efficient web map canvas for tkinter.**

[![pypi](https://img.shields.io/pypi/l/tkinter-map.svg)](https://github.com/Moustikitos/tkinter-map/blob/master/LICENSE)

## Support this project

[![Liberapay receiving](https://img.shields.io/liberapay/goal/Toons?logo=liberapay)](https://liberapay.com/Toons/donate)
[![Paypal me](https://img.shields.io/badge/PayPal-00457C?logo=paypal&logoColor=white)](https://paypal.me/toons)

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

![Tkmap widget](https://raw.githubusercontent.com/Moustikitos/tkinter-map/master/img/widget.png)

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
