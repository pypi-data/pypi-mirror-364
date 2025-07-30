# exceptionhandler.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Exception handling for methods called from threading or tkinter.

The ExceptionHandler class provides methods to intercept exceptions in
methods called from tkinter or threading and write the exception details to
the errorlog file before offering the option to display the exception
details.

The report_exception, try_command, try_event, and try_thread, methods are
defined to override the versions in the solentware_grid.gui.callbackexception
module's CallbackException class when used to report exceptions in datagrids.
Such as 'class DG(ExceptionHandler, DataGrid)'.

"""
import tkinter

BAD_WINDOW = 'bad window path name ".!'
DESTROYED_ERROR = (
    "".join(("can't invoke ", '"')),
    '" command:  application has been destroyed',
)
GRAB_ERROR = "grab".join(DESTROYED_ERROR)
FOCUS_ERROR = "focus".join(DESTROYED_ERROR)
DESTROY_ERROR = "destroy".join(DESTROYED_ERROR)


class ExceptionHandler:
    """Wrap methods run in separate threads or as tkinter callbacks.

    Exception details are written to the application's error log before
    offering the option to display the exception details in a dialogue.

    """

    _application_name = None
    _error_file_name = None

    @staticmethod
    def get_application_name():
        """Return the application name."""
        return str(ExceptionHandler._application_name)

    @staticmethod
    def get_error_file_name():
        """Return the exception report file name."""
        # Assumes set_error_file_name has been called
        return ExceptionHandler._error_file_name

    def report_exception(self, root=None, title=None, message=None):
        """Extend to write exception to errorlog if available.

        root - usually the application toplevel widget
        title - usually the application name
        message - usually the dialogue message if errorlog not available

        """
        # If root is left as None it is possible to generate the following on
        # stderr, maybe it's stdout, presumably from _tkinter:
        #
        # bgerror failed to handle background error.
        # Original Error:
        # ...
        #
        # by destroying the application toplevel before the exception report
        # toplevel(s).
        #
        # This may result in Microsoft Windows User Access Control preventing
        # an attempt to write an errorlog to the application folder in Program
        # Files by a py2exe generated executable.  Such attempts cause a
        # reasonable, but possibly worrying, error information dialogue to be
        # launched.

        import traceback
        import datetime
        import tkinter.messagebox

        if self.get_error_file_name() is not None:
            try:
                file = open(self.get_error_file_name(), "ab")
                try:
                    file.write(
                        "".join(
                            (
                                "\n\n\n",
                                " ".join(
                                    (
                                        self.get_application_name(),
                                        "exception report at",
                                        datetime.datetime.isoformat(
                                            datetime.datetime.today()
                                        ),
                                    )
                                ),
                                "\n\n",
                                traceback.format_exc(),
                                "\n\n",
                            )
                        ).encode("iso-8859-1")
                    )
                finally:
                    file.close()
                    message = "".join(
                        (
                            "An exception has occured.\n\nThe exception ",
                            "report has been appended to the error file.\n\n",
                            'Click "Yes" to see the detail\nor "No" ',
                            "to quit the application.",
                        )
                    )
            except:
                message = "".join(
                    (
                        "An exception has occured.\n\nThe attempt to append ",
                        "the exception report to the error file was not ",
                        'completed.\n\nClick "Yes" to see the detail\nor ',
                        '"No" to quit the application.',
                    )
                )

        # At 2009-08-01 calling tkMessageBox.askyesno and so on does not work
        # on Python2.6: s == YES compares booleanString with str
        # but calling _show works (as it does in tkMessageBox.py test stuff)
        # tkFileDialog functions seem ok

        # This method added at 30 August 2017 when moving dialogues module from
        # solentware_base.tools to solentware_misc.workarounds to avoid a
        # circular import loop between solentware_grid and solentware_misc.

        # Code commented 2020-10-03 while removing workarounds.dialogues.

        # def askyesno(title=None, message=None, **options):
        #    try:
        #        s = tkinter.messagebox._show(
        #            title,
        #            message,
        #            tkinter.messagebox.QUESTION,
        #            tkinter.messagebox.YESNO,
        #            **options)
        #        return str(s) == tkinter.messagebox.YES
        #    except tkinter.TclError as error:
        #        if str(error) != ''.join(("can't invoke ",
        #                                  '"grab" command:  ',
        #                                  'application has been destroyed')):
        #            raise

        if title is None:
            title = "Exception Report"
        if message is None:
            message = "".join(
                (
                    'An exception has occured.\n\nClick "Yes" to see ',
                    'the detail\nor "No" to quit the application',
                )
            )

        if root:
            try:
                pending = root.tk.call("after", "info")
                for callback in pending.split():
                    try:
                        root.after_cancel(callback)
                    except:
                        pass
            except:
                pass

        if root is None:
            dialtop = tkinter.Tk()
        else:
            dialtop = root
        try:
            try:
                show_exception = tkinter.messagebox.askyesno(
                    parent=dialtop, title=title, message=message
                )
            except tkinter.TclError as error:
                # GRAB_ERROR is anticipated if the window manager or desktop
                # destroys the application while the askyesno dialog is on
                # display.
                if str(error) != GRAB_ERROR:
                    # This dialogue added after a mistake creating a Toplevel
                    # in .reports.AppSysReportBase method _create_widget by
                    # Toplevel(master=parent) rather than
                    # Toplevel(master=parent.get_widget()).
                    # A consequence is a tkinter.TclError exception in the
                    # askyesno() call which is reported here minimally.
                    tkinter.messagebox.showinfo(
                        title="".join(("Exception in ", title)),
                        message="".join(
                            (
                                "Unable to show exception report.\n\n",
                                "The reported reason from tkinter is:\n\n",
                                str(error),
                            )
                        ),
                    )
                    raise
            except Exception as error:
                # Added in the hope any other exception from askyesno is dealt
                # with in a reasonable advertised way.
                tkinter.messagebox.showinfo(
                    title="".join(("Exception in ", title)),
                    message="".join(
                        (
                            "Unable to show exception report.\n\n",
                            "The reported reason is:\n\n",
                            str(error),
                        )
                    ),
                )
                raise
        except:
            # A non-error example, in context, is two failing after_idle calls.
            # Then click Quit on the second report before clicking No on the
            # first askyesno. The second askyesno has not been invoked yet.
            # If it is an error there is nothing realistic that can be done for
            # the application error being reported.
            try:
                dialtop.destroy()
            except:
                raise SystemExit(
                    "".join(
                        (
                            "Exception destroying application after ",
                            "exception in exception report dialogue",
                        )
                    )
                )
            raise SystemExit("Exception in exception report dialogue")

        if not show_exception:
            raise SystemExit("Do not show exception report")
        if root is None:
            top = dialtop
        else:
            top = tkinter.Toplevel(master=root)
        # It may be ok to allow the application to respond to keyboard and
        # pointer actions but exceptions when exceptions have already occurred
        # could loop indefinitely or be allowed to escape into Tkinter.  This
        # module is about stopping the latter; and it is confusing to say
        # 'something is wrong' and allow normal actions to proceed.
        # So grab_set.
        top.grab_set()
        top.wm_title(string=title)
        quit_ = tkinter.Button(master=top, text="Quit")
        quit_.pack(side=tkinter.BOTTOM)
        report = tkinter.Text(master=top, wrap=tkinter.WORD)
        quit_.configure(command=top.destroy)
        scrollbar = tkinter.Scrollbar(
            master=top, orient=tkinter.VERTICAL, command=report.yview
        )
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        report.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        report.configure(yscrollcommand=scrollbar.set)
        report.insert(tkinter.END, traceback.format_exc())
        top.wait_window()
        # Without the delete pending 'after' commands at start of method this
        # raise does not seem to be needed to quit the application.
        raise SystemExit("Dismiss exception report")

    @staticmethod
    def set_application_name(application_name):
        """Set the exception report application name.

        The class attribute is set once per run.

        """
        if ExceptionHandler._application_name is None:
            ExceptionHandler._application_name = application_name

    @staticmethod
    def set_error_file_name(error_file_name):
        """Set the exception report file name."""
        ExceptionHandler._error_file_name = error_file_name

    def try_command(self, method, widget):
        """Return wrapped method to report tkinter command exceptions.

        method - the command callback to be wrapped
        widget - usually the application toplevel widget

        Copied and adapted from Tkinter.

        """

        def wrapped_command_method(*a, **k):
            try:
                return method(*a, **k)
            except SystemExit as message:
                raise SystemExit(message)
            except tkinter.TclError as error:
                if str(error) != GRAB_ERROR:
                    if not str(error).startswith(BAD_WINDOW):
                        raise
            except:
                # If an unexpected exception occurs in report_exception let
                # Tkinter deal with it (better than just killing application
                # when Microsoft Windows User Access Control gets involved in
                # py2exe generated executables).
                self.report_exception(
                    root=widget.winfo_toplevel(),
                    title=self.get_application_name(),
                )
            return None

        return wrapped_command_method

    def try_event(self, method):
        """Return wrapped method to report tkinter event exceptions.

        method - the event callback to be wrapped

        Copied and adapted from Tkinter.

        """

        def wrapped_event_method(event):
            try:
                return method(event)
            except SystemExit as message:
                raise SystemExit(message)
            except tkinter.TclError as error:
                if str(error) != GRAB_ERROR:
                    if not str(error).startswith(BAD_WINDOW):
                        raise
            except:
                # If an unexpected exception occurs in report_exception let
                # Tkinter deal with it (better than just killing application
                # when Microsoft Windows User Access Control gets involved in
                # py2exe generated executables).
                self.report_exception(
                    root=event.widget.winfo_toplevel(),
                    title=self.get_application_name(),
                )
            return None

        return wrapped_event_method

    def try_thread(self, method, widget):
        """Return wrapped method to report threaded activity exceptions.

        method - the threaded activity to be wrapped
        widget - usually the application toplevel widget

        Copied and adapted from Tkinter.

        """

        def wrapped_thread_method(*a, **k):
            try:
                return method(*a, **k)
            except SystemExit as message:
                raise SystemExit(message)
            except tkinter.TclError as error:
                if str(error) != GRAB_ERROR:
                    if not str(error).startswith(BAD_WINDOW):
                        raise
            except:
                # If an unexpected exception occurs in report_exception let
                # Tkinter deal with it (better than just killing application
                # when Microsoft Windows User Access Control gets involved in
                # py2exe generated executables).
                self.report_exception(
                    root=widget.winfo_toplevel(),
                    title=self.get_application_name(),
                )
            return None

        return wrapped_thread_method

    # Take a snapshot of a tkinter.Text widget.  It is intended for problem
    # tracing.  It is saved as a sibling of ErrorLog.
    def dump_text_widget(self, textwidget, filename=None):
        """Save dump of a tkinter.Text widget in filename.

        Default filename is dumptextwidget in directory of error file.

        """
        if filename is None:
            filename = "dumptextwidget"
        import os
        import datetime

        filename = "_".join(
            (
                filename,
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
        )
        with open(
            os.path.join(
                os.path.dirname(self.get_error_file_name()), filename
            ),
            "w",
        ) as file:
            for text in textwidget.dump("1.0", tkinter.END):
                file.write(repr(text) + "\n")
