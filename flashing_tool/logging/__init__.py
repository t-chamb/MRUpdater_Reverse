# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.10)

import logging
import random
import re
import time

class IntervalSamplingFilter(logging.Filter):
    '''
    A logging filter for emitting events on a fixed time interval.

    Each filter object will always have a unique ID; a hash value that is a
    combination of the name and interval. Therefore, when multiple filters
    are added to the same logger via `Logger.addFilter`, only the new filters
    will be added to the logger\'s internal list of filters.

    The time interval uses monotonic time. In this way, it is unaffected
    by system time and shield from things like clock drift and timezone changes.

    Example usage:

    .. code-block:: python
    from flashing_tool.logging import IntervalSamplingFilter

    logger = logging.getLogger(__name__)

    # Create the filter and add it to the logger.
    interval_filter = IntervalSamplingFilter(name="chromatic_scan_error", interval=3)
    logger.addFilter(interval_filter)

    # Annotate the log message with the filter
    logger.info(f"{interval_filter} Chromatic scan error")
    '''
    previous: float = 0
    
    def __init__(self = None, name = None, interval = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def __str__(self = None):
        return self.log_tag

    
    def __hash__(self = None):
        return hash(self.name + str(self.interval))

    
    def log_tag(self = None):
        return f'''tag:{self.name}'''

    log_tag = None(log_tag)
    
    def filter(self = None, record = None):
        message = record.getMessage()
        if None((lambda .0 = None: for c in .0:
c in message)((self.log_tag,))) is False:
            return True
        filter_name_re = None.compile(re.escape(self.log_tag) + '\\s+?')
        sanitized_msg = filter_name_re.sub('', message, re.I)
        record.msg = sanitized_msg
        if self.previous == 0 or self.elapsed_time >= self.interval:
            self.previous = time.monotonic()
            return True

    
    def elapsed_time(self = None):
        return time.monotonic() - self.previous

    elapsed_time = None(elapsed_time)


class UniformSamplingFilter(logging.Filter):
    '''
    A logging filter for sampling logs with a fixed probability.

    This filter can either be attached to a handler or logger object. When
    attached to a handler, the filter will be consulted before the event is
    emitted by the handler. However, when attached to the logger, the filter
    will be consulted before the event is sent to the handler.

    p - probability that the log record is emitted. Float value in the range [0.0, 1.0].
    level - sampling applies to log records with this level or lower. Other records always pass through.
    '''
    
    def __init__(self = None, p = None, level = None):
        super().__init__()
        # Incomplete decompilation - manual review needed
        pass
    def filter(self = None, record = None):
        if record.levelno >= self.level:
            return random.random() < self.sample_rate

    __classcell__ = None

