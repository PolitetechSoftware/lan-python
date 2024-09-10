import time

from decorators import tracker

@tracker
def example(throw_error=False):
    if throw_error:
        raise Exception("Simulated Error")
    time.sleep(1)


if __name__ == '__main__':
    try:
        example()
        example(True)
    except:
        pass

    metrics = tracker.get_metrics('example')
    print(metrics)

    tracker.save_metrics('example')
    output = tracker.read_metrics('example')
    print(output)
