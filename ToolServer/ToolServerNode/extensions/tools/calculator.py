import requests
import xmltodict

from config import CONFIG
from core.register import toolwrapper
        

# @toolwrapper()
def calculator(expression:str)->str:
    """It is a simple calculator, which can execute Python expressions: e.g., "(123 + 234) / 23 * 1.5 - 8".
        
    :param string expression: The python expression you requested.
    :return string: The execution results of the expression.
    """
    globals={}
    locals={}
    try:
        # Wrap the code in an eval() call to return the result
        wrapped_code = f"__result__ = eval({repr(expression)}, globals(), locals())"
        exec(wrapped_code, globals, locals)
        return locals.get('__result__', None)
    except Exception as e:
        try:
        # If eval fails, attempt to exec the code without returning a result
            exec(expression, globals, locals)
            return "Code executed successfully."
        except Exception as e:
            return f"Error: {str(e)}"

#wolfram_cfg = CONFIG['wolfram']  
# @toolwrapper()
# def query_wolfram(query:str) -> list[dict]:
#     """Query WolframAlpha using natural language and return parsed results.

#     Query by access computation, math, curated knowledge & real-time data through Wolfram|Alpha and Wolfram Language. Note this tool is only used for high-level mathematically related queries, NOT the simple computations.

#     :param string query: The query you requested.
#     :return array[Object]: The results of the query.
#     """
#     response = requests.get(wolfram_cfg['endpoint'], params={'appid': wolfram_cfg['appid'], "input": query})
    
#     json_data = xmltodict.parse(response.text)
#     if 'pod' not in json_data["queryresult"]:
#         return "WolframAlpha API cannot parse the input query."
#     rets = json_data["queryresult"]['pod']

#     cleaned_rets = []
#     blacklist = ["@scanner", "@id", "@position", "@error", "@numsubpods", "@width", "@height", "@type", "@themes",
#                  "@colorinvertable", "expressiontypes"]

#     def filter_dict(d, blacklist):
#         if isinstance(d, dict):
#             return {k: filter_dict(v, blacklist) for k, v in d.items() if k not in blacklist}
#         elif isinstance(d, list):
#             return [filter_dict(i, blacklist) for i in d]
#         else:
#             return d

#     for ret in rets:
#         ret = filter_dict(ret, blacklist=blacklist)
#         # Do further cleaning to retain only the input and result pods
#         if "@title" in ret:
#             if ret["@title"] == "Input" or ret["@title"] == "Result":
#                 cleaned_rets.append(ret)

#     return cleaned_rets
