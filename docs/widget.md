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

