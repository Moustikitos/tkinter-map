<a id="tkmap.bio"></a>

# tkmap.bio

Basic input/output module.

<a id="tkmap.bio.TileWorker"></a>

## TileWorker Objects

```python
class TileWorker(threading.Thread)
```

Tile downloader daemon. It gets data from sqlite database or from url
request if not found. It works with two LIFO queues. `TileWorker` is a
subclass of `threading.Thread`, it is set as a `daemon` on initialization
and starts immediately.

**Attributes**:

- `timeout` _int_ - (class attribute) timeout delay when tile data is
  requested from url.
- `opener` _urllib.request.OpenerDirector_ - (class attribute) url opener
  used by all `TileWorker` intances. It is set only with the first
  class instanciation.
- `job` _queue.Queue_ - queue from where tile tag and map model.
- `result` _queue.Queue_ - queue where tile tag and data are pushed into.
- `db_name` _str_ - database base name.
- `stop` _threading.Event_ - event used to stop forever loop.

<a id="tkmap.bio.TileWorker.__init__"></a>

#### \_\_init\_\_

```python
def __init__(job: queue.Queue, result: queue.Queue, db_name: str,
             **options) -> None
```

**Arguments**:

- `job` _queue.Queue_ - queue from where tile tag and map model.
- `result` _queue.Queue_ - queue where tile tag and data are pushed
  into.
- `db_name` _str_ - database base name.

<a id="tkmap.bio.TileWorker.kill"></a>

#### kill

```python
def kill() -> None
```

Stop the forever loop

<a id="tkmap.bio.TileWorker.run"></a>

#### run

```python
def run() -> None
```

Forever loop

<a id="tkmap.bio.TileWorker.get"></a>

#### get

```python
def get(url: str, headers: dict = {}) -> str
```

Download tile from server.

**Arguments**:

- `url` _str_ - tile ressource location.
- `headers` _dict_ - headers used in request.
  

**Returns**:

- `str` - base64-encoded data.

<a id="tkmap.bio.Database"></a>

## Database Objects

```python
class Database()
```

`sqlite3` database implementation used for tile caching.

<a id="tkmap.bio.Database.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str) -> None
```

**Arguments**:

- `name` _str_ - database name. Database is created in the tkmap.MAPS
  folder with ".sqlm" extention.

<a id="tkmap.bio.Database.get"></a>

#### get

```python
def get(zoom: int, row: int, col: int) -> Union[str, bool]
```

Get a tile from database using row, column and zoom parameters.

**Arguments**:

- `zoom` _int_ - tile set zoom level.
- `row` _int_ - tile set row.
- `col` _int_ - tile set column.
  

**Returns**:

- `str|bool` - base64-encoded data if any tile found else `False`

<a id="tkmap.bio.Database.put"></a>

#### put

```python
def put(zoom: int, row: int, col: int, data: str) -> None
```

Set tile data in database with row, column and zoom informations.

**Arguments**:

- `zoom` _int_ - tile set zoom level.
- `row` _int_ - tile set row.
- `col` _int_ - tile set column.
- `data` _str_ - base64-encoded string.

<a id="tkmap.bio.Database.close"></a>

#### close

```python
def close() -> None
```

Save and close database.

