# Source Generated with Decompyle++
# File: decorators.pyc (Python 3.10)

import logging
import time
from functools import wraps
from typing import Callable, Any, Union
from flashing_tool.logging import UniformSamplingFilter
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def trace(debug = None, sample_rate = None):
    '''
    Traces and times function execution.

    When a `sample_rate` is provided [0.0, 1.0], only a percentage of the traces will
    be logged.  This is enforced by the `flashing_tool.logging.UniformSamplingFilter`
    logging filter. The objective is sampling is to mitigate a deluge of traces which
    can make it difficult to spot anomalies.

    :param debug: When True, the filter level is raised to DEBUG and function parameters are dumped to stdout.
    :param sample_rate: Probability that the trace logged. Float value in the range [0.0, 1.0].
    :return:
    '''
    filter_level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(filter_level)
    if sample_rate is not None:
        logger.addFilter(UniformSamplingFilter(sample_rate, filter_level, **('p', 'level')))
    
    def decorator(func = None):
        
        def inner(*args, **kwargs):
            inner.call_count += 1
            logger.info(f'''Call no. {inner.call_count} of {func.__name__}''')
            if debug:
                args_repr = (lambda .0: [ repr(a) for a in .0 ])(args)
                args_repr.extend((lambda .0: [ f'''{k}={repr(v)}''' for k, v in .0 ])(kwargs.items()))
                signature = ', '.join(args_repr)
                logger.debug(f'''Calling {func.__name__}({signature})''')
            started_at = time.perf_counter()
        # Assignment completed
        inner = None(inner)
        inner.call_count = 0
        return inner

    return decorator


def handle_exceptions(exceptions = None, raise_as = None):
    '''Handles a list of exceptions and optionally re-raises them as a different exception.'''
    
    def decorator(func = None):
        
        def inner(*args, **kwargs):
            pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
        inner = None(inner)
        return inner

    return decorator

