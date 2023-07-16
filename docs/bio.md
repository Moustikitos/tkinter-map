<a id="tkmap.bio"></a>

# tkmap.bio

Basic input/output module.

<a id="tkmap.bio.StopWorkException"></a>

## StopWorkException Objects

```python
class StopWorkException(Exception)
```

Used to stop the worker loop

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
def __init__(job: queue.Queue, result: queue.Queue, db_name: str) -> None
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

