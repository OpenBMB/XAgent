import os
import sys
import argparse
from copy import deepcopy
from XAgent.config import CONFIG,ARGS
from command import CommandLine,XAgentServerEnv


def parse_args():
    """
    Parse command line arguments

    Returns:
        argparse.Namespace: Object containing command line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", type=str,
                        help="task description",required=True)
    parser.add_argument("--upload_files", nargs='+',
                        help="upload files")
    parser.add_argument("--model", type=str,)
    parser.add_argument("--record_dir", type=str,)
    parser.add_argument("--mode", type=str, default="auto",
                        help="mode, only support auto and manual, if you choose manual, you need to press enter to continue in each step")
    parser.add_argument("--quiet", action="store_true",default=False)

    parser.add_argument("--max_subtask_chain_length", type=int,)
    parser.add_argument("--enable_ask_human_for_help", action="store_true",)
    parser.add_argument("--max_plan_refine_chain_length", type=int,)
    parser.add_argument("--max_plan_tree_depth", type=int,)
    parser.add_argument("--max_plan_tree_width", type=int,)
    parser.add_argument("--max_retry_times", type=int,)
    parser.add_argument("--config_file",type=str,default=os.getenv('CONFIG_FILE', 'assets/config.yml'))

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    
    args = parse_args()
    os.environ['CONFIG_FILE'] = args.config_file

    cmd = CommandLine(XAgentServerEnv)
    
    if args.quiet:
        original_stdout = sys.stdout
        from XAgent.running_recorder import recorder
        sys.stdout = open(os.path.join(recorder.record_root_dir,"command_line.ansi"),"w",encoding="utf-8")


    args = vars(args)

    for key,value in args.items():
        if value is not None:
            if key == 'model':
                ARGS['default_completion_kwargs'] = deepcopy(CONFIG['default_completion_kwargs'])
                ARGS['default_completion_kwargs']['model'] = value
            else:
                ARGS[key] = value

    cmd.start(
        args['task'],
        role="Assistant",
        mode=args['mode'],
        upload_files=args['upload_files'],
    )
    
    if args.quiet:
        sys.stdout.close()
        sys.stdout = original_stdout