# coding=utf-8
from threading import Lock

def synchronized(lock):
    '''Synchronization decorator.'''
    def wrap(f):
         def new_function(*args, **kw):
             lock.acquire()
             try:
                 return f(*args, **kw)
             finally:
                 lock.release()
         return new_function
    return wrap

def sprint(*a, **b):
    '''
    thread-safe print
    '''
    with CONSOLE_LOCK:
        print(*a, **b)


def test():
    pass

CONSOLE_LOCK = Lock()

if __name__ == '__main__':
    test()
