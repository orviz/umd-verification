
from fabric.api import abort
from fabric.api import local
from fabric.api import puts
from fabric.api import settings
from fabric.colors import red


def to_file(r, logfile):
    """Writes Fabric capture result to the given file."""
    def _write(fname, msg):
        with open(fname, 'a') as f:
            f.write(msg)
            f.flush()
    l = []
    if isinstance(r, str):  # exception
        _fname = '.'.join([logfile, "stdout"])
        _write(_fname, r)
        l.append(_fname)
    else:
        if r.stdout:
            _fname = '.'.join([logfile, "stdout"])
            _write(_fname, r.stdout)
            l.append(_fname)
        if r.stderr:
            _fname = '.'.join([logfile, "stderr"])
            _write(_fname, r.stderr)
            l.append(_fname)

    return l


def info(msg):
    """Prints info/debug logs."""
    puts("[INFO] %s" % msg)


def fail(msg):
    """Prints info/debug logs."""
    abort("[%s] %s" % (red("FAIL"), msg))


def ok(msg):
    """Prints info/debug logs."""
    puts("[OK] %s" % msg)


def runcmd(cmd, fail_check=True, logfile=None):
    with settings(warn_only=True):
        r = local(cmd, capture=True)

    if logfile:
        logs = to_file(r, logfile)

    if fail_check:
        if r.failed:
            msg = "Error while executing command '%s'."
            if logs:
                msg = ' '.join([msg, "See more information in logs (%s)."
                                     % ','.join(logs)])
            abort(red(msg % cmd))
            # raise exception.ExecuteCommandException(("Error found while "
            #                                          "executing command: "
            #                                          "'%s' (Reason: %s)"
            #                                          % (cmd, r.stderr)))
    return r
