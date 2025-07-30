# bindings.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide interface to tkinter bind, tag_bind, unbind, and tag_unbind.

Tcl/Tk uses the bind command to bind and unbind sequences; where giving the
empty string implements the removal of the current binding.

Adopting the same technique with the tkinter bind method causes a memory
leak.  The Python idiom is 'id = w.bind(seq); w.unbind(seq, funcid=a)',
where unbind calls Tcl/Tk bind the Tcl/Tk way, and avoids memory leaks.

This technique is described in the docstrings for tkinter bind and unbind.

(I managed to not notice this point for 20 years!; using tkinter bind as if
it were Tcl/Tk bind.)

This class manages the identifier returned by the Misc.bind, Text.tag_bind,
and Canvas.tag_bind methods of tkinter.  It handles the differences between
Canvas and Text tag_bind methods within the Bindings.tag_bind method, which
has widget as it's first argument.

"""
import tkinter

from .exceptionhandler import ExceptionHandler


class BindSequenceIsNone(Exception):
    """Exception raised if sequence or function argument is not given.

    Use tkinter.Misc.bind(...) directly to get the current bound script or
    list of bound events.
    """


class CanvasTagBindSequenceIsNone(Exception):
    """Exception raised if sequence or function argument is not given.

    Use tkinter.Canvas.tag_bind(...) directly to get the current bound
    script or list of bound events.
    """


class TextTagBindSequenceIsNone(Exception):
    """Exception raised if sequence or function argument is not given.

    Use tkinter.Canvas.tag_bind(...) directly to get the current bound
    script or list of bound events.
    """


class WidgetIsNotTextOrCanvas(Exception):
    """Exception raised if sequence or function argument is not given.

    Use tkinter.Canvas.tag_bind(...) directly to get the current bound
    script or list of bound events.
    """


class Bindings(ExceptionHandler):
    """Keep register of tkinter bind returns for use by tkinter unbind.

    _binding is the register with (widget, sequence) as the key and the
    function identifier returned by tkinter's bind() method as the value.

    _current_binding can be used to control changes to _binding and whether
    there should be a need to adjust bindings.  The protocol is chosen to
    fit the application.  Initial value is None, intended to mean 'clear
    the register before applying new bindings'.

    Canvas tags must use the canvas_tag_* methods and Text tags must use the
    text_tag_* methods.

    """

    def __init__(self, **k):
        """Initialize the bindings register."""
        super().__init__(**k)
        self._binding = {}
        self._tag_binding = {}
        self._current_binding = None
        self._frozen_binding = set()

    def __del__(self):
        """Destroy any bindings in _binding."""
        self.unbind_all_handlers(allow_exceptions=True)
        self._frozen_binding.clear()

        # Class hierarchy for Bindings is Bindings(ExceptionHandler(object))
        # ExceptionHandler does not have a __del__ method so only possible
        # source of __del__ method is something else between Bindings and
        # object in method resolution order.
        # Subclasses of Bindings should do super().__del__() unconditionally
        # in their __del__ methods if they have such.
        if hasattr(super(), "__del__"):
            super().__del__()

    def bind(self, widget, sequence, function=None, add=None):
        """Bind sequence to function for widget and note identity.

        BindSequenceIsNone is raised if the call is seeking information
        about the current binding: call tkinter bind method directly to
        do this.

        If a binding exists for widget for sequence it is destroyed.

        If bool(function) is True a new binding is created and noted.

        """
        if not bool(sequence):
            raise BindSequenceIsNone("sequence must be an event sequence")
        key = (widget, sequence)
        binding = self._binding
        if not bool(add):
            if key in binding:
                for function_id in binding[key]:
                    widget.unbind(sequence, funcid=function_id)
                binding[key].clear()
        if function:
            if key not in binding:
                binding[key] = set()
            binding[key].add(
                widget.bind(
                    sequence=sequence, func=self.try_event(function), add=add
                )
            )

    def tag_bind(self, widget, tag, sequence, function=None, add=None):
        """Bind sequence to function for tag in widget and note identity.

        widget must be an instance of tkinter.Canvas or tkinter.Text.

        tag must be a tag name for Text widgets, or a tag name or logical
        expression of tag names (see Tk Canvas documentation) for Canvas
        widgets.

        If bool(sequence) is False CanvasTagBindSequenceIsNone
        or TextTagBindSequenceIsNone is raised.

        If a binding exists for widget for sequence it is destroyed.

        If bool(function) is True a new binding is created and noted.

        """
        if not isinstance(widget, (tkinter.Text, tkinter.Canvas)):
            raise WidgetIsNotTextOrCanvas(
                "widget must be a tkinter Text or Canvas instance"
            )
        if not bool(sequence):
            if isinstance(widget, tkinter.Text):
                raise TextTagBindSequenceIsNone(
                    "sequence must be an event sequence"
                )
            raise CanvasTagBindSequenceIsNone(
                "sequence must be an event sequence"
            )
        key = (widget, tag, sequence)
        tag_binding = self._tag_binding
        if not bool(add):
            if key in tag_binding:
                for function_id in tag_binding[key]:
                    widget.tag_unbind(
                        tag,  # Different argument names in Text and Canvas.
                        sequence,
                        funcid=function_id,
                    )
                tag_binding[key].clear()
        if function:
            if key not in tag_binding:
                tag_binding[key] = set()
            tag_binding[key].add(
                widget.tag_bind(
                    tag,  # Different argument names in Text and Canvas.
                    sequence=sequence,  # Positional argument in Text.
                    func=self.try_event(function),
                    add=add,
                )
            )

    def unbind_all_handlers_except_frozen(self):
        """Unbind registered sequences which are not in _frozen_binding."""
        binding = self._binding
        for key in set(binding).difference(self._frozen_binding):
            for function in binding[key]:
                key[0].unbind(key[1], funcid=function)
            del binding[key]
        tag_binding = self._tag_binding
        for key in set(tag_binding).difference(self._frozen_binding):
            for function in tag_binding[key]:
                key[0].unbind(key[1], funcid=function)
            del tag_binding[key]
        self._current_binding = None

    def unbind_all_handlers(self, allow_exceptions=False):
        """Unbind all registered sequences.

        The default for allow_exceptions should be used everywhere except
        in the __del__ method.

        """
        for key, function_ids in self._binding.items():
            for function in function_ids:
                try:
                    key[0].unbind(key[1], funcid=function)
                except tkinter.TclError as exc:
                    if allow_exceptions:
                        if str(exc).startswith("bad window path name "):
                            continue
                        if str(exc).startswith('can\'t invoke "bind" command: '):
                            continue
                    raise
        for key, function_ids in self._tag_binding.items():
            for function in function_ids:
                try:
                    key[0].tag_unbind(key[1], key[2], funcid=function)
                except tkinter.TclError as exc:
                    if allow_exceptions:
                        if str(exc).startswith("bad window path name "):
                            continue
                        if str(exc).startswith(
                            'can\'t invoke "bind" command: '
                        ):
                            continue
                        # Allow for attempts to unbind tag bindings after
                        # destruction of widget.
                        if str(exc).startswith(
                            'invalid command name '
                        ):
                            continue
                    raise
        self._binding.clear()
        self._tag_binding.clear()
        self._current_binding = None

    def set_frozen_bindings(self):
        """Set _frozen_binding to set of _binding' keys."""
        self._frozen_binding.clear()
        self._frozen_binding.update(self._binding)
        self._frozen_binding.update(self._tag_binding)

    def unset_frozen_bindings(self):
        """Set _frozen_binding to empty."""
        self._frozen_binding.clear()

    @staticmethod
    def return_break(event):
        """Do nothing and return 'break' in response to event."""
        del event
        return "break"

    @staticmethod
    def return_continue(event):
        """Do nothing and return 'continue' in response to event."""
        del event
        return "continue"

    @staticmethod
    def return_none(event):
        """Do nothing and return None in response to event."""
        del event
