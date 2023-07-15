# -*- coding:utf-8 -*-
import os
import time
import json
import queue
import tkinter
import logging
import threading
import functools
import collections

from tkmap import JSON, load_img_package, bio, model
from typing import List, Tuple
from tkinter import ttk


class Tile:

    TILE_CMD_CREATE = \
        "if {[%(w)s find withtag %(t)s] eq {}} { " +\
        "%(w)s lower [%(w)s create image " +\
        "[expr {%(c)s * [image width %(n)s]}] " +\
        "[expr {%(r)s * [image height  %(n)s]}] " +\
        "-anchor nw -image %(n)s -tags {%(t)s tile} -state hidden] }"
    TILE_CMD_SHOW = "%(w)s itemconfig %(t)s -state normal; update"
    TILE_CMD_HIDE = "%(w)s itemconfig %(t)s -state hidden"
    TILE_CMD_CLEAR = "image delete %(t)s"
    tkeval = None
    tkcall = None

    def __init__(self, master: tkinter.BaseWidget) -> None:
        if Tile.tkeval is None or Tile.tkcall is None:
            Tile.tkeval = master.tk.eval
            Tile.tkcall = master.tk.call
        self.w_name = master._w

    def create(self, tag: str, data: str) -> None:
        imgtk = \
            Tile.tkcall("image", "create", "photo", tag, "-data", data)
        _, row, col = tag.split("_")
        args = {"w": self.w_name, "n": imgtk, "r": row, "c": col, "t": tag}
        Tile.tkeval(Tile.TILE_CMD_CREATE % args)
        self._clear = Tile.TILE_CMD_CLEAR % args
        self._hide = Tile.TILE_CMD_HIDE % args
        self._show = Tile.TILE_CMD_SHOW % args
        self._imgtk = imgtk

    def show(self) -> None:
        logging.info(f" -> {__class__.__name__} {self._imgtk} show")
        Tile.tkeval(self._show)

    def hide(self) -> None:
        logging.info(f" -> {__class__.__name__} {self._imgtk} hidden")
        Tile.tkeval(self._hide)

    def clear(self) -> None:
        logging.info(f" -> {__class__.__name__} {self._imgtk} cleared")
        Tile.tkeval(self._clear)


# inertia computation @ 100Hz & k = 0.9
def _drift(obj: tkinter.Canvas, speed_x: float, speed_y: float) -> None:
    t = time.time()
    dt = t - obj._tps[1]
    dx = speed_x * dt
    dy = speed_y * dt
    obj._tps[1] = t
    if obj._tps[0] is None and (dx*dx + dy*dy) > 1:
        obj.tk.eval(
            f"{obj._w} xview scroll {int(round(dx))} units;"
            f"{obj._w} yview scroll {int(round(dy))} units"
        )
        obj._after_tasks.append(
            obj.after(
                int(10 - (time.time() - t)*1000),
                lambda o=obj, sx=speed_x*0.9, sy=speed_y*0.9: _drift(o, sx, sy)
            )
        )
    obj._update_drawarea()


# draw loop
def _drawloop(obj: tkinter.Canvas, ms: int) -> None:
    # schedule a new task
    obj._after_tasks.append(
        obj.after(ms, lambda o=obj, d=ms: _drawloop(o, d))
    )
    # _update canvas with available tiles and queue unavailable ones
    if obj._drawarea != obj.drawarea:
        obj._drawarea = obj.drawarea
        obj._update()

    # _update canvas with queued tiles
    while not obj.DONE.empty():
        try:
            tag, data = obj.DONE.get()
            tile = Tile(obj)
            tile.create(tag, data)
            tile.show()
            obj.cache[tag] = tile
            with obj.QUEUED.mutex:
                if tag in obj.QUEUED.queue:
                    obj.QUEUED.queue.remove(tag)
        except Exception as error:
            logging.error(f" -> _drawloop error: {error} - tag {tag}")
    # clean _after_tasks list
    for callback in obj._after_tasks[:]:
        # if task info unavailable (it raises TclError) then it is running or
        # terminated
        try:
            obj.tk.eval(f"after info {callback}")
        except tkinter.TclError:
            obj._after_tasks.remove(callback)


class Tkmap(tkinter.Canvas):

    LOCK = threading.Lock()

    @property
    def xnw(obj) -> float:
        return float(obj.tk.eval(f"{obj._w} canvasx 0"))

    @property
    def ynw(obj) -> float:
        return float(obj.tk.eval(f"{obj._w} canvasy 0"))

    @property
    def xse(obj) -> float:
        return float(
            obj.tk.eval(f"{obj._w} canvasx [expr [winfo width {obj._w}]]")
        )

    @property
    def yse(obj) -> float:
        return float(
            obj.tk.eval(f"{obj._w} canvasy [expr [winfo height {obj._w}]]")
        )

    def __init__(self, master=None, cnf={}, **kw) -> None:
        self.framerate = kw.pop("framerate", 4)
        self.cachesize = kw.pop("framerate", 500)

        tkinter.Canvas.__init__(self, master, cnf, **kw)
        self["xscrollincrement"] = self["yscrollincrement"] = 1

        ttk.Label(
            relief="solid", padding=(5, 1),
            font=("calibri", "8"), textvariable="coords"
        ).place(y=4, relx=0.5, anchor="n")

        load_img_package(self.tk)

        self.JOB = queue.LifoQueue()
        self.DONE = queue.LifoQueue()
        self.QUEUED = queue.Queue()

        self.cache: Cache = Cache(size=self.cachesize)
        self.mapmodel: model.MapModel = None
        self.workers: List[bio.TileWorker] = []
        self.latlon: List[float] = [0.0, 0.0]

        self._drawarea = ()
        self._after_tasks = []
        self._tps = [None, 0., 0., 0., 0.]

        self.borderwidth = 0
        self.drawarea = ()
        self.mapsize = 1, 1
        self.radius = 0
        self.zoom = 0

    def save_location(self) -> None:
        if self.mapmodel is not None:
            self.save_coords(self.winfo_width()/2, self.winfo_height()/2)
            with open(os.path.join(JSON, ".loc"), "w") as out:
                json.dump({"zoom": self.zoom, "latlon": self.latlon}, out)

    def load_location(self) -> None:
        try:
            with open(os.path.join(JSON, ".loc"), "r") as in_:
                return json.load(in_)
        except Exception:
            return {}

    def open(
        self, model: model.MapModel, zoom: int = None,
        location: List[float] = None
    ) -> None:
        self.close()
        data = self.load_location()
        self.zoom = zoom or data.get("zoom", 0)
        self.latlon = location or data.get("latlon", [0., 0.])
        self.tk.setvar(
            "coords",
            f"lat {self.latlon[0]:3.5f}° | lon {self.latlon[1]:3.5f}°"
        )
        self.mapmodel = model
        model.init(self)
        self.center()
        self._start()

    def close(self) -> None:
        self._stop()
        self.clear_canvas()
        self.save_location()
        self.mapmodel = None

    def center(self, px: float = None, py: float = None) -> None:
        px = px or self.winfo_width()/2
        py = py or self.winfo_height()/2
        nrow, ncol = self.mapsize
        width = ncol * self.mapmodel.tile_w
        height = nrow * self.mapmodel.tile_h
        x, y = self.mapmodel.ll2xy(*self.latlon, zoom=self.zoom)
        self.xview_moveto(
            (width * x/width - px or self.winfo_width()/2) / width
        )
        self.yview_moveto(
            (height * y/height - py or self.winfo_height()/2) / height
        )

    def clear_canvas(self, keep_cache: bool = False) -> None:
        if not keep_cache:
            self.cache.clear()
        else:
            [tile.hide() for tile in self.cache.values()]

    def destroy(self) -> None:
        self.close()
        tkinter.Canvas.destroy(self)

    def save_coords(self, x: float = None, y: float = None) -> None:
        self.latlon = list(
            self.mapmodel.xy2ll(
                self.canvasx(x or self.winfo_width()/2),
                self.canvasy(y or self.winfo_height()/2),
                self.zoom
            )
        )

    def _cancel_tasks(self) -> None:
        for callback in self._after_tasks:
            try:
                self.tk.eval(f"after cancel {callback}")
            except tkinter.TclError:
                pass
        self._after_tasks.clear()

    def _start(self) -> None:
        self.bind("<Button-1>", self.on_button_1)
        self.bind("<B1-Motion>", self.on_button_1_motion)
        self.bind("<Motion>", self.on_motion)
        self.bind("<ButtonRelease-1>", self.on_button_1_release)
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<Configure>", lambda e: self._update_drawarea())
        self.bind(
            "<Control-B1-Motion>", lambda e: self.on_button_1_motion(e, 5)
        )
        self.workers = [
            bio.TileWorker(self.JOB, self.DONE, self.mapmodel.name),
            bio.TileWorker(self.JOB, self.DONE, self.mapmodel.name)
        ]
        self._drawarea = -1, -1, -1, -1
        self._update_drawarea()
        _drawloop(self, 1000//self.framerate)

    def _stop(self) -> None:
        self._cancel_tasks()
        self.unbind("<Button-1>")
        self.unbind("<B1-Motion>")
        self.unbind("<Motion>")
        self.unbind("<ButtonRelease-1>")
        self.unbind("<MouseWheel>")
        self.unbind("<Configure>")
        self.unbind("<Control-B1-Motion>")
        with Tkmap.LOCK:
            while len(self.workers):
                self.workers.pop(0).kill()
            self._clear_queues()

    def _update_drawarea(self) -> None:
        tw, th = self.mapmodel.tilesize
        nr, nc = self.mapsize
        bd = self.borderwidth
        self.drawarea = (
            int(max(0, self.xnw//tw-bd)), int(max(0, self.ynw//th-bd)),
            int(min(nr, self.xse//tw+bd)), int(min(nc, self.yse//th+bd))
        )

    def _update(self) -> None:
        c1, r1, c2, r2 = self.drawarea
        radius = self.radius
        cmd = self.tk.eval
        _w = self._w

        tags_to_show = set(
            functools.reduce(
                list.__add__,
                (
                    [f"{self.zoom}_{r}_{c}" for c in range(c1, c2)]
                    for r in range(r1, r2)
                )
            )
        )

        cached_tiles = set(self.cache.keys())
        for tag in tags_to_show - cached_tiles:
            if tag not in self.QUEUED.queue:
                self.QUEUED.put(tag)
                self.JOB.put([tag, self.mapmodel])

        all_tiles = cmd(f"{_w} find overlapping {self['scrollregion']}")
        tile_to_show = cmd(
            f"{_w} find overlapping "
            f"{self.xnw - radius} {self.ynw - radius} "
            f"{self.xse + radius} {self.yse + radius}"
        )
        tile_to_hide = set(all_tiles.split()) - set(tile_to_show.split())
        standing_by_tiles = tags_to_show & cached_tiles

        try:
            cmd(
                "foreach id {" + " ".join(tile_to_hide) + "} "
                "{" + _w + " itemconfig $id -state hidden};"
                "foreach tag {" + " ".join(standing_by_tiles) + "} "
                "{" + _w + " itemconfig $tag -state normal};"
            )
        except tkinter.TclError as error:
            # due to cache size limitation some images may be deleted
            # during the tcl command execution
            logging.info(f" -> _update error: {error}")

    def _clear_queues(self) -> None:
        with self.JOB.mutex:
            self.JOB.queue.clear()
        with self.DONE.mutex:
            self.DONE.queue.clear()
        with self.QUEUED.mutex:
            self.QUEUED.queue.clear()

    def on_button_1(self, event: tkinter.Event) -> None:
        self.configure(cursor="fleur")
        self.tk.call(self._w, 'scan', 'mark', event.x, event.y)
        self._tps = [time.time(), event.x, event.y, 0., 0.]

    def on_motion(self, event: tkinter.Event) -> None:
        lat, lon = self.mapmodel.xy2ll(
            self.canvasx(event.x), self.canvasy(event.y), self.zoom
        )
        self.tk.setvar("coords", f"lat {lat:3.5f}° | lon {lon:3.5f}°")

    def on_button_1_motion(self, event: tkinter.Event, gain: int = 1) -> None:
        self.tk.call(self._w, 'scan', 'dragto', event.x, event.y, gain)
        self._update_drawarea()
        # speed computation
        t, x, y = time.time(), event.x, event.y
        dt = t - self._tps[0]
        if dt >= 0.01:
            self._tps[-2] = (x - self._tps[1]) / dt
            self._tps[-1] = (y - self._tps[2]) / dt
            self._tps[:3] = [t, x, y]

    def on_button_1_release(self, event: tkinter.Event) -> None:
        self.configure(cursor="arrow")
        self.save_coords()
        if self._tps[0]:
            self._tps[0] = None
            self._tps[1] = time.time()
            speed_x, speed_y = self._tps[-2:]
            self.after(10, lambda: _drift(self, -speed_x, -speed_y))

    def on_mouse_wheel(self, event: tkinter.Event) -> None:
        zoom_max = getattr(self.mapmodel, "zoom_max", 17)
        delta = 1 if event.num == 4 or event.delta == 120 else -1
        zoom = min(max(0, self.zoom + delta), zoom_max)
        if zoom == self.zoom:
            return

        self.save_coords(event.x, event.y)
        self.zoom = zoom
        with Tkmap.LOCK:
            self._clear_queues()
            self.clear_canvas(keep_cache=True)
            self.mapmodel.init(self)
            self.center(event.x, event.y)
            self._update_drawarea()


class Cache(dict):

    def __init__(self, *args, **kwargs) -> None:
        self.size = kwargs.pop("size", 150)
        self.store = collections.deque()
        self.update(dict(*args, **kwargs))

    def __setitem__(self, key: str, value: Tile) -> None:
        self.store.append(key)
        if len(self.store) > self.size:
            tile = self.pop(self.store[0])
            tile.clear()
        dict.__setitem__(self, key, value)

    def clear(self) -> None:
        self.store.clear()
        for tile in self.values():
            tile.clear()
        dict.clear(self)

    def pop(self, key: str) -> Tile:
        self.store.remove(key)
        return dict.pop(self, key)

    def popitem(self) -> Tuple[str, Tile]:
        item = dict.popitem(self)
        self.Store.remove(item[0])
        return item
