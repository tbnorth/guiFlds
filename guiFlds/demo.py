from guiFldsTk import guiFldsTk

from guiFlds import guiFlds


class pgSSDR(guiFlds):

    # fields and commands, see guiFlds.py for documentation
    fldList = (
        "server",
        "user",
        "dbname",
        ("port", str, "port", "5432"),
        "password",
        ("dbdir", str, "dbdir", "", "__OPENDIR__"),
        ("pgdir", str, "PG bin dir", "", "__OPENDIR__"),
        ("dumpdir", str, "dump dir", "", "__OPENDIR__"),
        ("dump", bool, "Dump on stop", "yes"),
        ("stop", bool, "Stop on exit", "yes"),
        ("exit", bool, "Dump on exit", "yes"),
        ("comp", bool, "No comp.", "nocomp", "__RADIO__"),
        ("comp", bool, "Zip", "zip", "__RADIO__"),
        ("comp", bool, "GZip", "gzip", "__RADIO__"),
        ("comp", bool, "Bzip2", "bzip2", "__RADIO__"),
        ("Start", None),
        ("Stop", None),
        ("Dump", None),
        ("Status", None),
        ("Create", None),
        ("Restore", None),
        ("Console", None),
        ("Help", None, "Help-->Help"),
    )

    pgEnv = "PGDATA", "PGDIR", "USER"  # relevant env entries

    def __init__(self):

        guiFlds.__init__(self)


guiFldsTk(pgSSDR())
