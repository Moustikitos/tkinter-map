# -*- coding:utf-8 -*-
"""
Basic input/output module.
"""

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
from typing import Union


class TileWorker(threading.Thread):
    """
    Tile downloader daemon. It gets data from sqlite database or from url
    request if not found. It works with two LIFO queues. `TileWorker` is a
    subclass of `threading.Thread`, it is set as a `daemon` on initialization
    and starts immediately.

    Attributes:
        timeout (int): (class attribute) timeout delay when tile data is
            requested from url.
        opener (urllib.request.OpenerDirector): (class attribute) url opener
            used by all `TileWorker` intances. It is set only with the first
            class instanciation.
        job (queue.Queue): queue from where tile tag and map model.
        result (queue.Queue): queue where tile tag and data are pushed into.
        db_name (str): database base name.
        stop (threading.Event): event used to stop forever loop.
    """

    timeout = 5
    opener = None

    def __init__(
        self, job: queue.Queue, result: queue.Queue, db_name: str
    ) -> None:
        """
        Args:
            job (queue.Queue): queue from where tile tag and map model.
            result (queue.Queue): queue where tile tag and data are pushed
                into.
            db_name (str): database base name.
        """
        threading.Thread.__init__(self)
        self.job = job
        self.result = result
        self.db_name = db_name
        self.daemon = True
        # initialize url opener if it does not exist. It is designed to handle
        # http and https requests
        if TileWorker.opener is None:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            TileWorker.opener = OpenerDirector()
            TileWorker.opener.add_handler(HTTPHandler())
            TileWorker.opener.add_handler(HTTPSHandler(context=ctx))

        self.start()

    def kill(self) -> None:
        "Stop the forever loop"
        self.job.put([None, None])  # unlock the loop blocked on the queue

    def run(self) -> None:
        "Forever loop"
        db = Database(self.db_name)
        while True:
            try:
                # tag is a formated string "{zoom}_{row}_{col}"
                # model is a model.MapModel object
                tag, model = self.job.get()
                if tag is None:
                    break
                zoom, row, col = [int(e) for e in tag.split("_")]
                data = db.get(zoom, row, col)  # False if not found
                if not data:
                    # download tile using model information
                    url, headers = model.get_tile_url(row, col, zoom)
                    logging.debug(f" -> {__class__.__name__}: {url}")
                    data = self.get(url, headers)
                    db.put(zoom, row, col, data)
                # sends tag and data to the result queue
                self.result.put(
                    [tag, base64.b64decode(data).decode("utf-8")]
                )
            except Exception as error:
                self.result.put([tag, False])
                logging.error(
                    f" -> {__class__.__name__}: {error}",
                    # exc_info=True
                )
        db.close()
        logging.info(f" -> {__class__.__name__}: {self} exiting")

    def get(self, url: str, headers: dict = {}) -> str:
        """Download tile from server.

        Args:
            url (str): tile ressource location.
            headers (dict): headers used in request.

        Returns:
            str: base64-encoded data.
        """
        req = Request(url, None, headers)
        res = TileWorker.opener.open(req, timeout=TileWorker.timeout)
        if res.status == 200:
            data = res.read().decode(
                res.headers.get_content_charset("latin-1")
            )
            return base64.b64encode(data.encode("utf-8")).decode("utf-8")
        else:
            raise Exception(f"error {res.status} - {res.reason}")


class Database:
    """
    `sqlite3` database implementation used for tile caching.
    """

    LOCK = threading.Lock()

    def __init__(self, name: str) -> None:
        """
        Args:
            name (str): database name. Database is created in the tkmap.MAPS
            folder with ".sqlm" extention.
        """

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

    def get(self, zoom: int, row: int, col: int) -> Union[str, bool]:
        """
        Get a tile from database using row, column and zoom parameters.

        Args:
            zoom (int): tile set zoom level.
            row (int): tile set row.
            col (int): tile set column.

        Returns:
            str | bool: base64-encoded data if any tile found else `False`
        """

        req = self.sqlite.execute(
            "SELECT data FROM tiles WHERE zoom=? AND row=? AND col=?;",
            (zoom, row, col)
        ).fetchall()
        if len(req):
            return req[0]['data']
        else:
            return False

    def put(self, zoom: int, row: int, col: int, data: str) -> None:
        """
        Set tile data in database with row, column and zoom informations.

        Args:
            zoom (int): tile set zoom level.
            row (int): tile set row.
            col (int): tile set column.
            data (str): base64-encoded string.
        """
        with Database.LOCK:
            self.sqlite.execute(
                "INSERT OR REPLACE INTO tiles(zoom, row, col, data) "
                "VALUES(?,?,?,?);", [zoom, row, col, data]
            )
            self.sqlite.commit()

    def close(self) -> None:
        """
        Save and close database.
        """
        with Database.LOCK:
            self.sqlite.commit()
        self.sqlite.close()
