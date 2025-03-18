from lib import threading
from pytest import mark, raises
from time import sleep


@mark.thread_test
def test_returning_thread_double_join():
    def target():
        return "yolo"

    t = threading.ReturningThread(target=target)
    t.start()
    assert t.join() == "yolo"
    assert t.join() == "yolo"


@mark.thread_test
def test_returning_thread_double_start():
    def target():
        return "yolo"

    t = threading.ReturningThread(target=target)
    t.start_safe()
    assert t.join() == "yolo"
    t.start_safe()
    assert t.join() == "yolo"


@mark.thread_test
def test_exception():
    def will_raise():
        raise Exception("oops")

    t = threading.ReturningThread(target=will_raise)
    t.start_safe()
    with raises(Exception):
        t.join()


@mark.thread_test
def test_thread_stop():
    def target():
        while True:
            print("yolo")
            sleep(1)

    t = threading.ReturningThread(target=target, daemon=True)
    t.start_safe()
    with raises(threading.ThreadExit):
        t.stop()
