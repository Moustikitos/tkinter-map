# -*- coding:utf-8 -*-
import math
import tkinter
import random

from typing import Tuple


class MapModel:

    name = "abstract"
    urls = []
    tile_w = 256
    tile_h = 256
    headers = {"User-agent": "tkmap/0.1"}
    a = 6378137.0
    zoom_max = 19

    @property
    def tilesize(obj) -> Tuple[int, int]:
        return obj.tile_w, obj.tile_h

    def get_tile_url(self, row: int, col: int, zoom: int) -> str:
        """return tile url from px, py coordinates"""
        return random.choice(self.urls).format(zoom=zoom, col=col, row=row)

    def init(self, canvas: tkinter.Canvas) -> None:
        n = 2**canvas.zoom
        canvas.mapsize = n, n
        canvas["scrollregion"] = 0, 0, n*self.tile_w, n*self.tile_h
        canvas.borderwidth = 2
        canvas.radius = max(self.tile_h, self.tile_w) * canvas.borderwidth

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


class OpenStreetMap(MapModel):

    urls = [
        "https://a.tile.openstreetmap.org/{zoom}/{col}/{row}.png",
        "https://b.tile.openstreetmap.org/{zoom}/{col}/{row}.png",
        "https://c.tile.openstreetmap.org/{zoom}/{col}/{row}.png",
    ]
    name = "openstreetmap"


class GoogleMap(MapModel):

    urls = [
        "https://mt0.google.com/vt/lyrs=m&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
        "https://mt1.google.com/vt/lyrs=m&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
        "https://mt2.google.com/vt/lyrs=m&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
        "https://mt3.google.com/vt/lyrs=m&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
    ]
    name = "google-map"


class GoogleSat(MapModel):

    urls = [
        "https://mt0.google.com/vt/lyrs=s&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
        "https://mt1.google.com/vt/lyrs=s&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
        "https://mt2.google.com/vt/lyrs=s&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
        "https://mt3.google.com/vt/lyrs=s&hl=en&x={col}&y={row}&z={zoom}&s=Ga",
    ]
    name = "google-satellite"
