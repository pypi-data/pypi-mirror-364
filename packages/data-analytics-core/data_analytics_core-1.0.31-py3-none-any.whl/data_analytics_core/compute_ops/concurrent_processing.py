import os
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ProcessPoolExecutor
import itertools
from typing import Any
from data_analytics_core.logger import da_logger
import dill
import io
import multiprocessing


MIN_THREADS = 10


# We override the ForkingPickler methods to make sure all the methods and functions can be pickled
# and used with an on-top decorator
@classmethod
def _dumps(cls, obj):
    buf = io.BytesIO()
    dill.Pickler(buf, recurse=True).dump(obj)
    return buf.getbuffer()


multiprocessing.reduction.ForkingPickler.dumps = _dumps
multiprocessing.reduction.ForkingPickler.loads = dill.loads


def multi_threading_decorator(threads_number: int):
    """
    iterable: A collection of items to be processed.
    thread_number: An integer specifying the number of threads to use.
    *args: Additional positional arguments for the function.
    **kwargs: Additional keyword arguments for the function.
    """
    if threads_number < MIN_THREADS:
        da_logger.warning(message=f"Your thread count is {threads_number}. Multithreading may not be recommended.")

    def decorator(func):
        def wrapper(iterable, *args, **kwargs) -> list[Any]:
            parallel_results = []

            print(f"Num processes: {len(iterable)}")
            if len(iterable) < MIN_THREADS:
                da_logger.warning(message=f"Your iterable has length {len(iterable)}. Multithreading is only recommended with high waiting times processes.")

            with ThreadPoolExecutor(max_workers=threads_number) as executor:
                _pool_executor_process(args, func, executor, iterable, kwargs, parallel_results, threads_number)

            return parallel_results
        return wrapper
    return decorator


def multi_processing_decorator(cores_number: int = os.cpu_count()):
    """
    iterable: A collection of items to be processed.
    cores_number: An integer specifying the number of cores to use.
    *args: Additional positional arguments for the function.
    **kwargs: Additional keyword arguments for the function.
    """
    max_cpu_count = os.cpu_count()
    if cores_number > max_cpu_count:
        da_logger.warning(message=f"Your cores_number: {cores_number} is higher than your actual cpu max count: "
                                  f"{max_cpu_count}. Your max cpu cores number will be assigned.")
        cores_number = max_cpu_count
    elif cores_number == 1:
        da_logger.warning(message=f"You specified only one core, which makes your function not suitable for multicore"
                                  f" processing. Defaulting to cpu max count: {max_cpu_count}.")
        cores_number = max_cpu_count

    def decorator(func):
        def wrapper(iterable, *args, **kwargs) -> list[Any]:
            parallel_results = []

            print(f"Num processes: {len(iterable)}")
            if len(iterable) < 2:
                da_logger.warning(message=f"Your iterable has length {len(iterable)}. Multiprocessing is not required.")

            with ProcessPoolExecutor(max_workers=cores_number) as executor:
                _pool_executor_process(args, func, executor, iterable, kwargs, parallel_results, cores_number)

            return parallel_results

        return wrapper
    return decorator


def _pool_executor_process(args, function_to_execute, executor, iterable, kwargs, parallel_results, workers_number):
    iterator_list = iter(iterable)
    futures = {
        executor.submit(function_to_execute, it, *args, **kwargs)
        for it in itertools.islice(iterator_list, workers_number)
    }
    while futures:
        # Wait for the next future to complete.
        done, futures = wait(
            futures, return_when=FIRST_COMPLETED
        )

        for fut in done:
            try:
                new_result = fut.result()
                parallel_results.append(new_result)
            except Exception as e:
                print(f"One process failed. Exception: {e}")
                raise e

        # Schedule the next set of futures.  We don't want more than N futures
        # in the pool at a time, to keep memory consumption down.
        for it in itertools.islice(iterator_list, len(done)):
            futures.add(executor.submit(function_to_execute, it, *args, **kwargs))
