from colorama import Fore
from XAgent.utils import ToolCallStatusCode,get_token_nums,clip_text
from XAgent.ai_functions import function_manager
from XAgent.config import CONFIG
from XAgent.logs import logger

SINGLE_ACTION_MAX_LENGTH = CONFIG.summary['single_action_max_length']
MAX_RETURN_LENGTH = CONFIG.summary['max_return_length']
MAX_PLAN_LENGTH = CONFIG.max_plan_length

def summarize_action(action_process:list[dict], task:str,)->(list[str],str):
    """
    Generate a summarized series of actions.

    Args:
        action_process (list[dict]): The list of actions to process.
        task (str): The task name.

    Returns:
        str: The string contains a summary of the actions.
    """
    if len(action_process) < 1:
        return "No steps found"
    
    def generate_func_args(args:dict,black_list=[])->str:
        """
        Generate function arguments in the form of strings.

        Args:
            args (dict): A dictionary of arguments.
            black_list (list): A list of forbidden or restricted words or keys in the args dictionary.

        Returns:
            str: A string that summarizes the function arguments.
        """
        ret = ''
        args_len = 0
        for k,v in args.items():
            if k in black_list:
                v = '`wrapped`'
            v_str,v_len = clip_text(str(v),SINGLE_ACTION_MAX_LENGTH-args_len,clip_end=True)
            if v_len < SINGLE_ACTION_MAX_LENGTH-args_len:
                ret += f'{k}="{v_str}",' if isinstance(v,str) else f'{k}={v_str},'
                args_len += v_len
            else:
                ret += f'{k}="{v_str}...",' if isinstance(v,str) else f'{k}={v_str}...,'
                args_len += SINGLE_ACTION_MAX_LENGTH-args_len
                
        return ret[:-1] # remove last comma
    
    # wrap old content
    raw_actions = {}
    accessed_files = []
    last_successful_action_index = None
    last_failed_action_index = None
    for index,action in zip(range(len(action_process)-1,-1,-1),action_process[::-1]):
        if last_successful_action_index is None and action['tool_status_code'] == ToolCallStatusCode.TOOL_CALL_SUCCESS:
            last_successful_action_index = index
        if last_failed_action_index is None and action['tool_status_code'] == ToolCallStatusCode.TOOL_CALL_FAILED:
            last_failed_action_index = index
        
        command = action["command"]["properties"]
        if command['name'] == '' or not isinstance(command['args'],dict):
            continue
        
        raw_action = ['`placeholder`','`placeholder`']
        
        if "FileSystem" in command["name"] and "filepath" in command["args"] and action["tool_status_code"] == ToolCallStatusCode.TOOL_CALL_SUCCESS:
            raw_action[0] = command['name']+f"({generate_func_args(command['args'],black_list=['content','new_content'])})"
            if command['args']['filepath'] in accessed_files:
                raw_action[1] = "`Old Content has been wrapped, check latest filesystem calling`"
            else:
                raw_action[1] = str(action['tool_output'])
                accessed_files.append(command["args"]["filepath"])
        else:
            raw_action[0] = command['name']+f"({generate_func_args(command['args'])})"
            raw_action[1] = str(action['tool_output'])
            
        raw_actions[index] = raw_action
    valid_index = list(raw_actions.keys())
    valid_index.sort()
    
    ret = {}
    for index in valid_index:
        action = action_process[index]
        if 'summary' not in action:
            raw_actions_des = '\n'.join([
                f'[{k}] {v}' for k,v in action['thoughts']['properties'].items()
            ] + [
                f"[tool_status_code] {action['tool_status_code']}",
                f"[tool calling] {raw_actions[index][0]}",
                f"[return] "
            ])
            raw_actions_des += clip_text(raw_actions[index][1],MAX_RETURN_LENGTH-get_token_nums(raw_actions_des))[0]
            
            summary,tokens = function_manager('summarize_action',
                                              action=raw_actions_des,current_task=task,
                                              return_generation_usage=True,)
            action['summary'] = summary
            logger.typewriter_log(f"Action summarized in {tokens['completion_tokens']} tokens",Fore.YELLOW)
        else:
            summary = action['summary']
        
        act_str = '\n'.join([
            f'[{index}] {raw_actions[index][0]}',
            f"[{index}][summary] {summary['summary']}",
            f"[{index}][description] {summary['description']}",
            f"[{index}][status code] {action['tool_status_code']}"
        ])
        if 'failed_reason_and_reflection' in summary and summary['failed_reason_and_reflection'] != '':
            act_str += f'\n[{index}][failed reason] {summary["failed_reason_and_reflection"]}'
        
        # directly adding short returns
        if len(raw_actions[index][1]) < 1000 and get_token_nums(raw_actions[index][1]) < 150:
            act_str += f'\n[{index}][return] {raw_actions[index][1]}'
            
        ret[index] = act_str
    
    reflection = function_manager('actions_reflection',
                                  actions=clip_text('\n'.join([ret[i] for i in valid_index]),MAX_RETURN_LENGTH)[0],
                                  current_task=task)
    
    ret_lenght = {k:get_token_nums(v) for k,v in ret.items()}
    total_length = sum(ret_lenght.values())
    
    # adding more return to last successful action
    for i in [last_successful_action_index,last_failed_action_index]:
        if i is not None and '[return]' not in ret[i]:
            s = f'\n[{i}][return] {clip_text(raw_actions[i][1],(MAX_RETURN_LENGTH-total_length)//2)[0]}'
            return_length = get_token_nums(s)
            ret_lenght[i] += return_length
            total_length += return_length
            ret[i] += s

    key_actions:list = reflection['key_actions']
    key_actions.sort(reverse=True)
    for i in key_actions:
        if total_length >= MAX_RETURN_LENGTH:
            break
        if i in ret and action_process[i]["tool_status_code"] == ToolCallStatusCode.TOOL_CALL_SUCCESS and '[return]' not in ret[i]:
            s = f'\n[{i}][return] {clip_text(raw_actions[i][1],SINGLE_ACTION_MAX_LENGTH-ret_lenght[i])[0]}'
            if (tokens := get_token_nums(s))> MAX_RETURN_LENGTH-total_length:
                continue
            total_length += tokens
            ret[i] += s
    
    while len(valid_index) > 0:
        i = valid_index.pop()
        if total_length >= MAX_RETURN_LENGTH:
            break
        if action_process[i]["tool_status_code"] == ToolCallStatusCode.TOOL_CALL_SUCCESS and '[return]' not in ret[i]:
            s = f'\n[{i}][return] {clip_text(raw_actions[i][1],SINGLE_ACTION_MAX_LENGTH-ret_lenght[i])[0]}'
            if (tokens := get_token_nums(s))> MAX_RETURN_LENGTH-total_length:
                continue
            total_length += tokens
            ret[i] += s


    valid_index = list(ret.keys())
    valid_index.sort()
    ordered_rets = [ret[i] for i in valid_index] + [f'[suggestion] {sugg}'for sugg in reflection["suggestions"]]
    
    return '\n'.join(ordered_rets)

def summarize_plan(plans:dict)->str:
    """
    Generate a summarized plan based on provided plans.

    Args:
        plans (dict): The plans to provide.

    Returns:
        str: The string contains a summary of the plan.
    """
    summary:list[list] = []
    task_ids = []
    detailed_info:dict[str,list] = {}
    current_task_id = None
    def recursive_summary(plan:dict,):
        """
        Generate a summarized plan in a recursive process.

        Args:
            plan (dict): A dictionary of plans.

        Returns:
            None
        """
        nonlocal summary
        nonlocal current_task_id
        plan_des = [
            f'[Task ID] {plan["task_id"]}',
            f'[Name] {plan["name"]}',
            f'[Goal] {plan["goal"]}',
            f'[Status] {plan["exceute_status"]}',
        ]
        if current_task_id is None and plan['exceute_status'] == 'DOING':
            current_task_id = plan['task_id']
            
        if 'milestones' in plan and len(plan['milestones']) > 0:
            plan_des.extend(['[Milestones]']+['- '+milestone for milestone in plan["milestones"]])

        
        if 'action_list_summary' not in plan and 'prior_plan_criticism' in plan:
            plan_des.append(f'[Prior Plan Criticism] {plan["prior_plan_criticism"]}')
        
        if 'submit_result' in plan and 'args' in plan['submit_result']:
            submission = plan['submit_result']['args']
            plan_des.append(f'[Action Status] {"Success" if submission["result"]["success"] else "Fail"}')
            
            # possible too long part
            action_des = [
                '[Action Info]',
                f"- [Conclusion] {submission['result']['conclusion']}"
            ]
            if 'action_list_summary' in plan:
                action_des.append(f'- [Summary] {plan["action_list_summary"]}')  
            if submission['suggestions_for_latter_subtasks_plan']['need_for_plan_refine']:
                if submission['suggestions_for_latter_subtasks_plan']['reason'] != '':
                    action_des.append(f"- [Proposal] {submission['suggestions_for_latter_subtasks_plan']['reason']}")
            detailed_info[plan['task_id']] = action_des
        
        task_ids.append(plan['task_id'])
        summary.append(plan_des)
        if "subtask" in plan:
            for subtask in plan["subtask"]:
                recursive_summary(subtask)
    recursive_summary(plans)
    total_tokens = sum([get_token_nums('\n'.join(plan)) for plan in summary])
    if current_task_id is None:
        current_task_id = task_ids[-1]
    for task_id,plan in zip(task_ids[::-1],summary[::-1]):
        if task_id <= current_task_id and task_id in detailed_info:
            if (tokens:=get_token_nums('\n'.join(detailed_info[task_id]))) > MAX_PLAN_LENGTH-total_tokens:
                continue
            else:
                total_tokens += tokens
                plan.extend(detailed_info[task_id])
    # logger.typewriter_log(f'Plan summarized {total_tokens}',Fore.YELLOW)
    ret = []
    for plan in summary:
        ret.append('\n'.join(plan))
    return '\n'.join(ret)