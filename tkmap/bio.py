# -*- coding:utf-8 -*-
import os
import ssl
import queue
import base64
import sqlite3
import logging
import threading

from urllib.request import Request, OpenerDirector, HTTPHandler
from urllib.request import HTTPSHandler
from tkmap import MAPS


class StopWorkException(Exception):
    "Used to stop the worker loop"


class TileWorker(threading.Thread):
    """
    Tile downloader daemon. The only task to do is getting tile url from
    job queue and pushing downloaded data to result queue.

    Attributes:
        job (queue.Queue): queue from where url are pulled.
        result (queue.Queue): queue where data are pushed into.

    Args:
        job (queue.Queue): queue from where url are pulled.
        result (queue.Queue): queue where data are pushed into.
    """

    # LOCK = threading.Lock()
    timeout = 5
    opener = None

    def __init__(
        self, job: queue.Queue, result: queue.Queue, db_name: str
    ) -> None:
        threading.Thread.__init__(self)
        self.job = job
        self.result = result
        self.db_name = db_name
        self.daemon = True
        self.stop = threading.Event()

        if TileWorker.opener is None:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            TileWorker.opener = OpenerDirector()
            TileWorker.opener.add_handler(HTTPHandler())
            TileWorker.opener.add_handler(HTTPSHandler(context=ctx))

        self.start()

    def kill(self) -> None:
        self.stop.set()
        self.job.put([None, None])

    def run(self) -> None:
        self.db = Database(self.db_name)  # sqlite
        while not self.stop.is_set():
            try:
                tag, model = self.job.get()
                if tag is None:
                    raise StopWorkException("stop signal received")

                zoom, row, col = [int(e) for e in tag.split("_")]
                data = self.db.get(zoom, row, col)

                if not data:
                    url = model.get_tile_url(row, col, zoom)
                    data = self.get(url, model.headers)
                    self.db.put(zoom, row, col, data)

                self.result.put(
                    [tag, base64.b64decode(data).decode("utf-8")]
                )
            except StopWorkException as error:
                logging.info(f" -> {__class__.__name__}: {error}")
            except Exception as error:
                logging.error(f" -> {__class__.__name__}: {error}")
        self.db.close()

    def get(self, url: str, headers: dict) -> str:
        req = Request(url, None, headers)
        res = TileWorker.opener.open(req, timeout=TileWorker.timeout)
        data = res.read().decode(
            res.headers.get_content_charset("latin-1")
        ).encode("utf-8")
        return base64.b64encode(data).decode("utf-8")


class Database:

    LOCK = threading.Lock()

    def __init__(self, name: str) -> None:
        sqlite = sqlite3.connect(os.path.join(MAPS, name + ".sqlm"))
        sqlite.row_factory = sqlite3.Row
        sqlite.execute(
            "CREATE TABLE IF NOT EXISTS tiles(zoom INTEGER, "
            "row INTEGER, col INTEGER, data TEXT);"
        )
        sqlite.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS tile_index ON "
            "tiles(zoom, row, col);"
        )
        sqlite.commit()
        self.sqlite = sqlite

    def get(self, zoom: int, row: int, col: int) -> str:
        req = self.sqlite.execute(
            "SELECT data FROM tiles WHERE zoom=? AND row=? AND col=?;",
            (zoom, row, col)
        ).fetchall()
        if len(req):
            return req[0]['data']
        else:
            return False

    def put(self, zoom: int, row: int, col: int, data: str) -> str:
        with Database.LOCK:
            self.sqlite.execute(
                "INSERT INTO tiles(zoom, row, col, data) VALUES(?,?,?,?);",
                [zoom, row, col, data]
            )
            self.sqlite.commit()

    def close(self) -> None:
        with Database.LOCK:
            self.sqlite.commit()
        self.sqlite.close()
