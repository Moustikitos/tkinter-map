<a id="tkmap.widget"></a>

# tkmap.widget

This module provides the core widget of tkmap package.

<a id="tkmap.widget.Tile"></a>

## Tile Objects

```python
class Tile()
```

`Tile` class to leverage the tcl interpreter to perform fast image
operation on canvas.

**Attributes**:

- `TILE_CMD_CREATE` _str_ - (class attribute) tcl command pattern to create
  the image canvas item.
- `TILE_CMD_SHOW` _str_ - (class attribute) tcl command pattern to show the
  image canvas item.
- `TILE_CMD_HIDE` _str_ - (class attribute) tcl command pattern to hide the
  image canvas item.
- `TILE_CMD_CLEAR` _str_ - (class attribute) tcl command pattern to delete
  the image data.
- `tkeval` _callable_ - (class attribute) the tk `eval` command.
- `tkcall` _callable_ - (class attribute) the tk `call` command.
- `w_name` _str_ - master canvas name.

<a id="tkmap.widget.Tile.__init__"></a>

#### \_\_init\_\_

```python
def __init__(master: tkinter.Canvas) -> None
```

**Arguments**:

- `master` _tkinter.Canvas_ - master canvas instance on wich tile is
  about to be managed.

<a id="tkmap.widget.Tile.create"></a>

#### create

```python
def create(tag: str, data: str) -> None
```

Create the image data inside tcl interpreter and generate the
associated canvas image-item.

**Arguments**:

- `tag` _str_ - tile tag with format `{zoom}_{row}_{col}`.
- `data` _str_ - image data as string.

<a id="tkmap.widget.Tile.show"></a>

#### show

```python
def show() -> None
```

Reveal the image item on the canvas.

<a id="tkmap.widget.Tile.hide"></a>

#### hide

```python
def hide() -> None
```

Hide the image item from the canvas.

<a id="tkmap.widget.Tile.clear"></a>

#### clear

```python
def clear() -> None
```

Delete the image item from canvas and image data from tcl interpreter.

<a id="tkmap.widget.Tkmap"></a>

## Tkmap Objects

```python
class Tkmap(tkinter.Canvas)
```

`Tkmap` is a `tkinter.Canvas` object that leverages directly tcl code to
provide a smooth user experience.

**Attributes**:

- `coords` _tkinter.Label_ - widget to display map coordinates.
- `framerate` _int_ - rate of canvas update.
- `cachesize` _int_ - number of tile stored in Tkmap cache.
- `cache` _dict_ - tile cache.
- `mapmodel` _model.MapMode_ - map model used to generate tile url and
  compute map coordinates.
- `workers` _List[bio.TileWorker]_ - List of python thread used to perform
  tile downloads or database queries.

<a id="tkmap.widget.Tkmap.bbox"></a>

#### bbox

```python
@property
def bbox(obj) -> tuple
```

Returns east, north, west and south boundaries view on canvas area.

<a id="tkmap.widget.Tkmap.place_widget"></a>

#### place\_widget

```python
def place_widget(widget: str, cnf={}, **kw) -> None
```

Place inner widgets on the canvas instance.

**Arguments**:

- `widget` _str_ - widget attribute name to place.
- `cnf` _dict_ - key-value pairs to place the widget.
- `**kw` - keywords arguments to place the widget.

<a id="tkmap.widget.Tkmap.dump_location"></a>

#### dump\_location

```python
def dump_location() -> None
```

Drops cursor location into filesystem

<a id="tkmap.widget.Tkmap.save_coords"></a>

#### save\_coords

```python
def save_coords(x: float = None, y: float = None) -> None
```

Save map coordinates from canvas center or specific coordinates

**Arguments**:

- `x` _float_ - horizontal pixel coordinates.
- `y` _float_ - vertical pixel coordinates.

<a id="tkmap.widget.Tkmap.load_location"></a>

#### load\_location

```python
def load_location() -> None
```

loads last saved location from filesystem

<a id="tkmap.widget.Tkmap.open"></a>

#### open

```python
def open(model: model.MapModel,
         zoom: int = None,
         location: List[float] = None) -> None
```

Open a map.

**Arguments**:

- `model` _model.MapModel_ - map tile provider.
- `zoom` _int_ - zoom level to start at. If not provided, starts to 0
  or previously saved zoom level.
- `location` _List[float]_ - location to start at. If not provided,
  starts at longitude 0 and latitude 0 or previously saved
  location.

<a id="tkmap.widget.Tkmap.close"></a>

#### close

```python
def close() -> None
```

Close the map and clear the canvas.

<a id="tkmap.widget.Tkmap.center"></a>

#### center

```python
def center(px: float = None, py: float = None) -> None
```

Align canvas center or coordinates to the last saved coordinates.

**Arguments**:

- `px` _float_ - horizontal pixel coordinates.
- `py` _float_ - vertical pixel coordinates.

