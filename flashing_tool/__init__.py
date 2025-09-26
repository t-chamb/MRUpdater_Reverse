# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.10)


class EmptyObject:
    '''An object for creating placeholder instances that are
    not yet ready for release.
    '''
    
    def __getattr__(self, name):
        
        def _missing(*args, **kwargs):
            pass

        return _missing


