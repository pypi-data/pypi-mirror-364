# rundu.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess performance database update customozied for database engine.

The rundu function is run in a new multiprocessing.Process started from the
chess performance GUI.

Spawn the deferred update process by the multiprocessing module.

"""
import sys
import importlib

if sys.platform.startswith("openbsd"):
    import resource

from .. import write_error_to_log
from ..gui import performancedu


class RunduError(Exception):
    """Exception class for rundu module."""


def rundu(
    home_directory,
    pgn_directory,
    database_module_name,
):
    """Do the deferred update using the specified database engine.

    engine_module_name and database_module_name must be absolute path
    names: 'chesstab.gui.chessdb' as engine_module_name and
    'chesstab.apsw.chessapswdu' as database_module_name for example.

    A directory containing the chesstab package must be on sys.path.

    """
    database_module = importlib.import_module(database_module_name)
    if sys.platform.startswith("openbsd"):
        # The default user class is limited to 512Mb memory but imports need
        # ~550Mb at Python3.6 for sqlite3.
        # Processes running for users in some login classes are allowed to
        # increase their memory limit, unlike the default class, and the limit
        # is doubled if the process happens to be running for a user in one of
        # these login classes.  The staff login class is one of these.
        # At time of writing the soft limit is doubled from 512Mb to 1024Mb.
        try:
            b" " * 1000000000
        except MemoryError:
            soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
            try:
                resource.setrlimit(
                    resource.RLIMIT_DATA, (min(soft * 2, hard), hard)
                )
            except Exception as exc_a:
                try:
                    write_error_to_log(home_directory)
                except Exception as exc_b:
                    # Maybe the import is small enough to get away with
                    # limited memory (~500Mb).
                    raise SystemExit(
                        " reporting exception in ".join(
                            ("Exception while", "set resource limit in rundu")
                        )
                    ) from exc_b
                raise SystemExit(
                    "Exception in rundu while setting resource limit"
                ) from exc_a

    deferred_update = performancedu.DeferredUpdate(
        deferred_update_module=database_module,
        database_class=database_module.Database,
        home_directory=home_directory,
        pgn_directory=pgn_directory,
    )
    try:
        deferred_update.root.mainloop()
    except Exception as error:
        try:
            write_error_to_log(home_directory)
        except Exception:
            # Assume that parent process will report the failure.
            raise SystemExit(
                " reporting exception in ".join(
                    ("Exception while", "doing deferred update in rundu")
                )
            ) from error
        raise SystemExit(
            "Reporting exception in rundu while doing deferred update"
        ) from error
