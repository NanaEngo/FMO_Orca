import logging
import os
import sys
import uuid
import time
import hashlib
import psutil

def setup_logger(run_id=None, log_dir=None, level_console=logging.INFO, level_file=logging.DEBUG):
    """
    Configure logger with run_id, console/file output, different levels and timestamped log file.
    """
    logger = logging.getLogger("orca_workflow")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(run_id)s] %(message)s')

    # Add run_id as filter
    if not run_id:
        run_id = str(uuid.uuid4())[:8]

    class RunIdFilter(logging.Filter):
        def filter(self, record):
            record.run_id = run_id
            return True

    logger.handlers = []
    logger.filters = []
    logger.addFilter(RunIdFilter())

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level_console)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler with date in name
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        logfile = os.path.join(log_dir, f"orca_{run_id}_{time.strftime('%Y%m%d_%H%M%S')}.log")
        fh = logging.FileHandler(logfile)
        fh.setLevel(level_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger, run_id

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def sha256_of_string(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def detect_orca_in_path():
    """Try to find 'orca' executable in $PATH."""
    for p in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(p, "orca")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None

def get_logical_cpu_count():
    return psutil.cpu_count(logical=True)

def get_available_memory_mb():
    return int(psutil.virtual_memory().available / (1024 ** 2))

def profile_step(logger, step_name):
    """Decorator to profile memory/time of a step."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"[{step_name}] START")
            t0 = time.time()
            mem0 = get_available_memory_mb()
            result = func(*args, **kwargs)
            mem1 = get_available_memory_mb()
            t1 = time.time()
            logger.info(f"[{step_name}] END | Duration: {t1-t0:.1f}s | Mem Δ: {mem1-mem0} MB")
            return result
        return wrapper
    return decorator