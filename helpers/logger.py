import logging
from logging import StreamHandler, FileHandler, Formatter

def setup_logging(level: str = "INFO", logfile: str = "bot.log"):
    fmt = Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root = logging.getLogger()
    root.setLevel(level)

    ch = StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    fh = FileHandler(logfile, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)
