import time
import threading

def RunEvery(duration, function, *args, **kwargs):
    """Will run the given function every x seconds.
    Args:
        duration (float): Seconds to wait between each function call.
        function (callable): The function to run.
    """
    def wrapper():
        while True:
            function(*args, **kwargs)
            time.sleep(duration)

    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()

def RunIn(duration, function, mainThread=False, *args, **kwargs):
    """Will run the given function after x seconds.
    Args:
        duration (float): Seconds to wait before running the function.
        function (callable): The function to run.
        mainThread (bool, optional): Whether to run the function in the main thread. WARNING: This is not accurate. The accuracy of the sleep depends on the main thread FPS. Defaults to False.
    """
    if not mainThread:
        def wrapper():
            time.sleep(duration)
            function(*args, **kwargs)

        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
    else:
        def wrapper():
            time.sleep(duration)
            function(*args, **kwargs)

        threading.Timer(duration, wrapper).start()

def RunInMainThread(function, *args, **kwargs):
    """Will run the given function in the main thread.
    Args:
        function (callable): The function to run.
    """
    RunIn(0, function, mainThread=True, *args, **kwargs)
