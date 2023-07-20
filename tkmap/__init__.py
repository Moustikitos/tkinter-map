# -*- coding: utf-8 -*-

import os
import tkinter
import logging

HOME = os.path.dirname(__file__)
MAPS = os.path.join(HOME, ".maps")
JSON = os.path.join(HOME, ".json")
os.makedirs(MAPS, exist_ok=True)
os.makedirs(JSON, exist_ok=True)


def load_img_package(tk):
    """
    It tries to load tke `imgtk` tcl package to add JPEG codec to the tcl
    interpreter. It logs an error if `imgtk` package not found. To install
    it locally you can extract the `imgtk` package folder in a `.tcl` folder
    at the root of `tkmap` package (ie containing the `__init__.py`).
    """
    img_path = os.path.normpath(
        os.path.join(HOME, ".tcl")
    ).replace(os.sep, "/")
    if tk.call("lsearch", "auto_path", img_path) < 0:
        tk.call("lappend", "auto_path", img_path)
    try:
        tk.eval("package require Img")
    except tkinter.TclError as error:
        logging.error(
            f" -> {__name__}: {error} - "
            "you may not be able to see JPEG-based tile maps"
        )
