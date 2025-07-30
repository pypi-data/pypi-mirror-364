# __init__.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Bind and exception handling for applications available at solentware.co.uk.

Store the identifiers returned by tkinter.Misc.bind() to allow deletion of
the bound function with unbind without memory leak (quoting the docstring
for bind).

Previously this stuff was in solentware_misc including the exception handling
for callback functions.  The addition of identifier handling to deal with
memory leaks forces introduction of solentware_bind so the stuff can be made
easily available to solentware_base and solentware_grid too.

The tkinter.Canvas.tag_bind() and tkinter.Text.tag_bind() methods are added
to those handled. Both tag_bind docstrings say "See bind for the return
value".

"""
