import time
from funix import funix


@funix()
def oh_iam_yield() -> str:
    yield "This is a function that needs 10 secs to run."
    for i in range(10):
        time.sleep(1)
        yield f"Update {i + 1}/10, Time: {time.time()}\n"
