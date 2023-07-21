# -*- coding:utf-8 -*-
import os
import math
import json
import tkinter
import random

from typing import Tuple
from tkmap import JSON


class MapModel:

    urls = []
    tile_w = 256
    tile_h = 256
    a = 6378137.0
    zoom_max = 19

    @property
    def tilesize(obj) -> Tuple[int, int]:
        return obj.tile_w, obj.tile_h

    def headers(self, *a, **kw) -> dict:
        return {"User-agent": "tkmap/0.1"}

    def get_tile_url(self, row: int, col: int, zoom: int) -> str:
        """Return tile url from row, column and zoom."""
        return random.choice(self.urls).format(
            zoom=zoom, col=col, row=row, **self.__dict__
        ), self.headers()

    def init(self, canvas: tkinter.Canvas, borderwidth: int = 2) -> None:
        n = 2**canvas.zoom
        canvas.mapsize = n, n
        canvas["scrollregion"] = 0, 0, n*self.tile_w, n*self.tile_h
        canvas.borderwidth = borderwidth
        canvas.radius = max(self.tile_h, self.tile_w) * borderwidth

    def Q(self, row: int, col: int, zoom: int) -> str:
        q = "" if zoom != 0 else "0"
        for i in range(zoom, 0, -1):
            digit, mask = 0, 1 << (i-1)
            if (col & mask) != 0:
                digit += 1
            if (row & mask) != 0:
                digit += 2
            q += str(digit)
        return q

    def ll2xy(self, lat: float, lon: float, zoom: int) -> Tuple[float, float]:
        n = 2**zoom
        lat = math.radians(lat)
        x = n * ((lon + 180.0) / 360.0)
        y = n * (1 - math.log(math.tan(lat) + (1/math.cos(lat))) / math.pi) / 2
        return x*self.tile_w, y*self.tile_h

    def xy2ll(self, x: float, y: float, zoom: int) -> Tuple[float, float]:
        n = 2**zoom
        x /= self.tile_w
        y /= self.tile_h
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y/n))))
        lon = x / n * 360.0 - 180.0
        return lat, lon

    @staticmethod
    def load(name, **kw):
        model = MapModel()
        with open(os.path.join(JSON, name + ".json"), "r") as in_:
            model.__dict__.update(json.load(in_), **kw)
        if len(getattr(model, "urls", [])):
            return model
        else:
            raise Exception("no url defined")
