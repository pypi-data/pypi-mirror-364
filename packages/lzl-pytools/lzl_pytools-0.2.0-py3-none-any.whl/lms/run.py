import os
import sys
import argparse
import logging
import yaml
from dataclasses import asdict

from lzl_pytools.multi3.parallel_config import AioParallelConfig
from lzl_pytools.multi3.multi_process_mng import defautl_logger_setup, run_aio_parallel_task
from lms.lms_sub_proc import (InsertReqBuildProc, UpsertReqBuildProc, SearchReqBuildProc, QueryReqBuildProc, 
                              InsertReqBuildProcReplaceInt, UpsertReqBuildProcReplaceInt, AioHttpSendProc)
from lms.cmd import LmsCfg

logger = logging.getLogger()

def main():
    parallel_cfg = AioParallelConfig()
    dftCfg = LmsCfg()

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--task_type', type=str, default='insert', help='')
    parser.add_argument('-f', '--config', type=str, default='cfg.yaml', help='')
    parser.add_argument('--replace_field_name', type=str, default='', help='')
    parser.add_argument('--start', type=int, default=0, help='')
    parser.add_argument('--end', type=int, default=1000, help='')
    parser.add_argument('--group_num', type=int, default=100, help='')


    dftCfg.add_argument(parser)
    parallel_cfg.add_argument(parser)

    args = parser.parse_args()
    if args.config != '' and os.path.isfile(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            obj = yaml.safe_load(f)
            lmscfg = LmsCfg(**obj)
    else:
        print(f'not find config file({args.config}), use default config.')
        lmscfg = LmsCfg()
    lmscfg.from_parser(args)
    parallel_cfg.from_parser(args)
    
    task_type = args.task_type

    defautl_logger_setup(log_dir='logs', stdout_show_log=True)
    logger.warning(f'task_type={task_type}, {lmscfg}, {parallel_cfg}')

    data = {'lms_cfg': asdict(lmscfg), 'task_type': task_type}
    build_class = None
    if args.replace_field_name != '':
        data['group_queue'] = InsertReqBuildProcReplaceInt.init_queue(args.start, args.end, args.group_num)
        data['replace_field_name'] = args.replace_field_name
        if task_type == 'insert':
            build_class = InsertReqBuildProcReplaceInt
        elif task_type == 'upsert': 
            build_class = UpsertReqBuildProcReplaceInt
    else:
        if task_type == 'insert':
            build_class = InsertReqBuildProc
        elif task_type == 'upsert': 
            build_class = UpsertReqBuildProc
        elif task_type == 'search': 
            build_class = SearchReqBuildProc
        elif task_type == 'query': 
            build_class = QueryReqBuildProc

    if build_class is None:
        raise Exception(f'task_type is error: {task_type}')
    run_aio_parallel_task(parallel_cfg, build_class, AioHttpSendProc, data)
    return 0

if __name__ == '__main__':
    sys.exit(main())