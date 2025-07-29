Kiosk Project
-------------

The ``kiosk`` project launches a minimal browser window using ``pywebview``.
It works on Windows and on Linux (tested on Raspberry Pi OS).
Use it to present a local web application without any browser chrome.

Usage
=====

From a recipe::

    kiosk show --url http://127.0.0.1:8888

Or launch the built-in Recipe Launcher::

    gway -r recipe_launcher

Parameters
==========

``url``
  Full address to load. If omitted, ``host`` and ``port`` are used.
``host``
  Host name when constructing the URL, default ``0.0.0.0``.
``port``
  Port number when constructing the URL, default ``8888``.
``width`` and ``height``
  Window dimensions in pixels.
``fullscreen``
  If ``True`` the window occupies the entire screen.
