# coding=utf-8
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
