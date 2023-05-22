# import time


import threading
import time


def f():
    import time

    t = threading.currentThread()

    bar = [
        " [=     ]",
        " [ =    ]",
        " [  =   ]",
        " [   =  ]",
        " [    = ]",
        " [     =]",
        " [    = ]",
        " [   =  ]",
        " [  =   ]",
    ]
    i = 0
    while getattr(t, "do_run", True):
        print(bar[i % len(bar)], end="\r")
        time.sleep(0.2)
        i += 1


t1 = threading.Thread(target=f)

print("Starting thread")
t1.start()
time.sleep(5)
print("Something done")
t1.do_run = False
t1.join()
print("Thread Done")
