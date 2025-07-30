from dataclasses import dataclass, asdict
import argparse

class DataClassArgsTools:
    @staticmethod
    def add_arguments(dataclass_obj, parser: argparse.ArgumentParser):
        obj = asdict(dataclass_obj)
        for k,v in obj.items():
            parser.add_argument(f"--{k}", type=type(v), default=argparse.SUPPRESS, help=f'default={v}')

    @staticmethod
    def update_from_args(dataclass_obj, args):
        obj = asdict(dataclass_obj)
        for k in obj.keys():
            if k in args:
                setattr(dataclass_obj, k, getattr(args, k))

@dataclass
class ParallelConfig:
    producer_num : int = 5
    consumer_num : int = 2
    queue_size : int = 1
    queue_num : int = 500
    run_time_len : int = -1
    max_task_num : int = -1

    def add_argument(self, parser):
        DataClassArgsTools.add_arguments(self, parser)

    def from_parser(self, args):
        DataClassArgsTools.update_from_args(self, args)

@dataclass
class AioParallelConfig(ParallelConfig):
    aio_parallel_num : int = 5
    one_parallel_task_num : int = -1
    no_wait : bool = False
    aio_timeout : int = 300
