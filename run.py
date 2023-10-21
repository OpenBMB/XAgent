import os
import sys
import argparse

from XAgent.config import CONFIG
from command import CommandLine,XAgentServerEnv

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str,
                        help="task description",required=True)
    parser.add_argument("--upload_files", nargs='+',
                        help="upload files")
    parser.add_argument("--model", type=str, default=CONFIG.default_completion_kwargs['model'],)
    parser.add_argument("--record_dir", type=str, default=None)
    parser.add_argument("--mode", type=str, default="auto",
                        help="mode, only support auto and manual, if you choose manual, you need to press enter to continue in each step")
    parser.add_argument("--quiet", action="store_true",default=False)
    
    
    parser.add_argument("--max_subtask_chain_length", type=int, default=CONFIG.max_subtask_chain_length)
    parser.add_argument("--enable_ask_human_for_help", action="store_true",default=CONFIG.enable_ask_human_for_help)
    parser.add_argument("--max_plan_refine_chain_length", type=int, default=CONFIG.max_plan_refine_chain_length)
    parser.add_argument("--max_plan_tree_depth", type=int, default=CONFIG.max_plan_tree_depth)
    parser.add_argument("--max_plan_tree_width", type=int, default=CONFIG.max_plan_tree_width)
    parser.add_argument("--max_retry_times", type=int, default=CONFIG.max_retry_times)
    parser.add_argument("--config_file",type=str,default="config.yml")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    CONFIG.reload(args.config_file)
    CONFIG.default_completion_kwargs['model']  = args.model
    CONFIG.enable_ask_human_for_help = args.enable_ask_human_for_help
    CONFIG.max_subtask_chain_length = args.max_subtask_chain_length
    CONFIG.max_plan_refine_chain_length = args.max_plan_refine_chain_length
    CONFIG.max_plan_tree_depth = args.max_plan_tree_depth
    CONFIG.max_plan_tree_width = args.max_plan_tree_width
    CONFIG.max_retry_times = args.max_retry_times   



    cmd = CommandLine(XAgentServerEnv)
    if args.quiet:
        original_stdout = sys.stdout
        from XAgent.running_recorder import recorder
        sys.stdout = open(os.path.join(recorder.record_root_dir,"command_line.ansi"),"w",encoding="utf-8")
    cmd.start(
        args.task,
        role="Assistant",
        mode=args.mode,
        upload_files=args.upload_files,
        record_dir=CONFIG.record_dir,
    )
    if args.quiet:
        sys.stdout.close()
        sys.stdout = original_stdout
    