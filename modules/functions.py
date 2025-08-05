## Imports ##
import requests, requests_cache, inspect
from modules.globals import *
requests_cache.install_cache("http_cache", expire_after=60, allowable_methods=["GET"]) # 1 minute requests cache

## Shared ##
def show_message(message: str = None, mtype: str = "Standard"):
    if not check_type(message, str, 1, True): return
    if not check_type(mtype, str, 2, True): return

    if mtype == "Standard":
        print(f"[{version}] {message}", flush=True)
    elif mtype == "Error":
        print(f"[{version}] Error: {message}", flush=True)
    elif mtype == "Http" and show_http:
        print(f"[{version}] Http: {message}", flush=True)
    elif mtype != "Http":
        show_message(f"Ignored show_message due to invalid mtype ('{mtype}')")


def check_type(value, class_, argnumber: int, internal: bool = True):
    #if not check_type(argnumber, int, 3, True): return
    #if not check_type(internal, bool, 4, True): return

    # advanced debugger, don't bother checking this out if you don't have a lot of python knowledge
    funcname = "<unknown>"
    stack = inspect.stack()
    if len(stack) > 1:
        frame = stack[1].frame
        raw_funcname = stack[1].function
        self_obj = frame.f_locals.get("self")

        try:
            if raw_funcname == "__init__" and self_obj:
                cls = self_obj.__class__
                funcname = f"{cls.__name__}.__init__"
                func_obj = cls.__init__
            else:
                funcname = raw_funcname
                func_obj = frame.f_globals.get(funcname)
        except Exception:
            func_obj = None

        try:
            if func_obj:
                sig = inspect.signature(func_obj)
                args = str(sig)
            else:
                args = f"(..., <unknown>:{class_.__name__}, ...)"
        except Exception:
            args = f"(..., <unknown>:{class_.__name__}, ...)"
    else:
        funcname = "<main thread?>"
        args = f"(..., <unknown>:{class_.__name__}, ...)"

    if type(value) != class_:
        show_message(
            f"Expected arg{argnumber} to be class {class_.__name__} instead of {value.__class__.__name__} in {funcname}{args} {internal and "(internal)" or " "}", "Error")
        return False

    return True
    

def server_request(type: str = "get", url: str = server_question, data: dict = {}):
    if not check_type(type, str, 1, True): return
    if not check_type(url, str, 2, True): return
    if not check_type(data, dict, 3, True): return

    if not url:
        show_message(
            f"Can't send {type.upper()} request to empty url!", "Error")
    try:
        method = getattr(requests, type.lower())
        response = method(url, json=data)

#       show_message(
#           f"Response Status Code (Server Interaction): {response.status_code}", "Http")

        return response.status_code < 400, response

    except requests.exceptions.RequestException as e:
        show_message(f"Request failed (Server Interaction): {str(e)}", "Error")
        return False, None