"""
Python treading example based on https://pymotw.com/2/threading/
"""

import threading
import time

def print_start():
    print threading.currentThread().getName(), 'Starting'

def print_exit():
    print threading.currentThread().getName(), 'Exiting'

def do_t1():
    print_start()
    lst = ('a', 'b', 'c', 'd')
    for s in lst:
        print(s)
    print_exit()

def do_t2():
    print_start()
    lst = (1, 2, 3, 4)
    for s in lst:
        time.sleep(2)
        print(s)
    print_exit()

def f():
    print_start()
    lst = (10, 20, 30, 40)
    for s in lst:
        time.sleep(2)
        print(s)
    print_exit()
    

def make_threads():

    t1 = threading.Thread(name='t1', target = do_t1, args = ())
    t2 = threading.Thread(name='t2', target = do_t2, args = ())

    t1.start()
    t2.start()
    
    t1.join()  
    #t2.join()    
    print("exiting make_threads")

def my_service():
    print_start()
    time.sleep(3)
    print_exit()


if __name__ == "__main__":

    #t = threading.Thread(name='my_service', target=my_service)
    #t.start()

    make_threads()
    f()