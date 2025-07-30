'''
    ############################################################################
    ######################## Print Tricks & More - version 0.3.20 #############
    ############################################################################
    
    ######################## from print_tricks import pt #######################
    ############################################################################

    ### - Import by placing the following line with your other import statements:
    ###   from print_tricks import pt

    ### - read through the variables below: "ReadMe_Quick" & "ReadMe_Detailed",
    ### or type "pt.pt()" in your terminal to read these in a nicer formatted style.
'''

'''
ALL TODO  docstrings have been moved to the file @print_tricks_todo.md"

'''

############### Accessable names via imports ############
## Set classes you'd like to be imported when using from print_tricks import *
#   (user can manually import whatever they want though)
__all__ = ['pt', 'C', 'km', 'Profiler']

############### IMPORTS - Built-in Python ###############
from pathlib import Path
import sys, os, shutil, time, datetime, gc, warnings #import os import statements import all
import textwrap, ctypes, re, math
import subprocess, multiprocessing, threading, queue, random as ra
import ast  ## NOTE check to see if I'm using this
import traceback, inspect, linecache
import difflib, functools

############### imports - Built-In OS-Dependent Modules ###############
linux_Mac = False
if sys.platform.startswith("linux") or sys.platform == "darwin":
    # NOTE: I don't think this is currently going to work. Must test on Linux: readchar is not not
    # built-in, it's a downloaded module. I'll have to either require this module for linux users
    # to be able to read the keys, or look at licence and see if integration or importing
    # is more viable. if integrating, will need to look at the library readchar
    #     # from .readchar_linux import readchar  ## OLD CODE. New below
    #     from readchar.readchar_linux import readchar
    import tty, termios

    linux_Mac = True
elif sys.platform in ("win32", "cygwin"):
    import msvcrt


############### IMPORTS - pt debugger ################

if os.path.exists("print_tricks_debugger.py"):
    ...

else:
    #... ### db = copy.deepcopy(pt)
    class place_holder_db:
        def __init__(*args, **kwargs):
            '''PlaceHolder'''
            print('The print_tricks_debugger has not been installed')
            return



class C:
    """class for generating colors in the terminal

    - All colors should be working on Windows, Linux, Mac, and any IDE that supports colors.
    - I have some WIP code to try to find out if a terminal does not support colors, and then disable it. But haven't actually built or tested a working version yet
    """

    os.system(
        ""
    )  ## NOTE NOTE THIS ONE LINE ALLOWS WINDOWS TO PRINT COLORS IN THE CMD/PYTHON TERMINAL!!
    ### It's just initiating a system call and must pass something, so we just pass empty strings :)
    
    co = "\033["
    ### Foreground colors
    Fore_BLACK = co + "30m"
    Fore_GRAY = co + "90m"  ## ANSI Escape code 'Bright Black'
    Fore_RED = co + "31m"
    Fore_RED_BRIGHT = co + "91m"
    Fore_GREEN = co + "32m"
    Fore_GREEN_BRIGHT = co + "92m"
    Fore_YELLOW = co + "33m"
    Fore_YELLOW_BRIGHT = co + "93m"
    Fore_BLUE = co + "34m"
    Fore_BLUE_BRIGHT = co + "94m"
    Fore_PURPLE = co + "35m"
    Fore_PURPLE_BRIGHT = co + "95m"
    Fore_CYAN = co + "36m"
    Fore_CYAN_BRIGHT = co + "96m"
    Fore_WHITE = co + "37m"
    Fore_WHITE_BRIGHT = co + "97m"
    ###   shortcuts to foreground colors
    fbl = Fore_BLACK
    fgr = Fore_GRAY
    fr = Fore_RED
    frb = Fore_RED_BRIGHT
    fg = Fore_GREEN
    fgb = Fore_GREEN_BRIGHT
    fy = Fore_YELLOW
    fyb = Fore_YELLOW_BRIGHT
    fb = Fore_BLUE
    fbb = Fore_BLUE_BRIGHT
    fp = Fore_PURPLE
    fpb = Fore_PURPLE_BRIGHT
    fc = Fore_CYAN
    fcb = Fore_CYAN_BRIGHT
    fw = Fore_WHITE
    fwb = Fore_WHITE_BRIGHT
    ### Background colors
    Back_BLACK = co + "40m"
    Back_GRAY = co + "100m"  ## ANSI Escape code 'Bright Black'
    Back_RED = co + "41m"
    Back_RED_BRIGHT = co + "101m"
    Back_GREEN = co + "42m"
    Back_GREEN_BRIGHT = co + "102m"
    Back_YELLOW = co + "43m"
    Back_YELLOW_BRIGHT = co + "103m"
    Back_BLUE = co + "44m"
    Back_BLUE_BRIGHT = co + "104m"
    Back_PURPLE = co + "45m"
    Back_PURPLE_BRIGHT = co + "105m"
    Back_CYAN = co + "46m"
    Back_CYAN_BRIGHT = co + "106m"
    Back_WHITE = co + "47m"
    Back_WHITE_BRIGHT = co + "107m"
    ###   shortcuts to background colors
    bbl = Back_BLACK
    bgr = Back_GRAY
    br = Back_RED
    brb = Back_RED_BRIGHT
    bg = Back_GREEN
    bgb = Back_GREEN_BRIGHT
    by = Back_YELLOW
    byb = Back_YELLOW_BRIGHT
    bb = Back_BLUE
    bbb = Back_BLUE_BRIGHT
    bp = Back_PURPLE
    bpb = Back_PURPLE_BRIGHT
    bc = Back_CYAN
    bcb = Back_CYAN_BRIGHT
    bw = Back_WHITE
    bwb = Back_WHITE_BRIGHT
    ### Effects for Text
    Effect_RESET = co + "0m"
    Effect_BOLD = co + "1m"
    Effect_DIM = co + "2m"
    Effect_ITALICS = co + "3m"
    Effect_UNDERLINE = co + "4m"
    Effect_BACKGROUND_SWAP = co + "7m"
    Effect_STRIKEOUT = co + "9m"  # This won't work on all terminals
    Effect_DOUBLE_UNDERLINE = co + "21m"  # This won't work on all terminals
    Effect_BLINKING_SLOW = co + "5m"  # This won't work on all terminals
    Effect_BLINKING_FAST = co + "6m"  # This won't work on all terminals
    ###   shortcuts to Text Effects
    er = Effect_RESET
    eb = Effect_BOLD
    ef = Effect_DIM
    ei = Effect_ITALICS
    eu = Effect_UNDERLINE
    ecs = Effect_BACKGROUND_SWAP
    es = Effect_STRIKEOUT  # This won't work on all terminals
    ed = Effect_DOUBLE_UNDERLINE  # This won't work on all terminals
    ebs = Effect_BLINKING_SLOW  # This won't work on all terminals
    ebf = Effect_BLINKING_FAST  # This won't work on all terminals
    ### Theme Colors (Print tricks color scheme)
    t1 = Fore_GREEN  ### Strings
    t2 = Fore_YELLOW  ### Arguments
    t3 = Fore_BLUE  ### Values of the variables (args)
    t4 = Fore_CYAN  ### Specialty (keys, errors etc.)

    ### Functions
    # my_varsOnly = []
    def __init__(self):
        """
        -Check if the current running process supports colors
            - Check if it's a tty /terminal
            - Check if it's running on supported platform
                - if False:
                - Check if it's running in a known-to-support color IDE (For now, check just the most common ide's, like vsCode, atom, pycharm? Like top 5), so even though win32 might not support color, vsCode does, so enable color
        - Disable color function (just set all color codes to '' blank strings)
        - Allow the person to independently enable/disable terminal colors on their own.
            -Possibly make this a pt.c / pt.color function instead of a C._disableColors because that won't be a known class to them. But have that function refer to these ones.
                -Possibly pass their functions return as this function running.
        """
        # print(vars(c))
        self.my_varsOnly = [
            x for x in dir(C) if not x.startswith("__")
        ]  ### Eliminates the built-in vars, so just the user-created ones are here.
        # pt(self.my_varsOnly)
        self.my_varsValuesOnly = []
        for var in self.my_varsOnly:
            value = getattr(C, var)
            self.my_varsValuesOnly.append(value)
        # pt(self.my_varsValuesOnly)

        colors = self._supports_color()
        if colors == False:
            self._disableColors(self.my_varsOnly)

        return

    def _supports_color(self):
        """
        Return True if the running system's terminal supports color, and False
        otherwise.

        NOTE - I'm not sure whether this actually works or not.
        - But if not, there is code in
            a color-supporting traceback library I was checking out, that had a possibly better code
            to what I'm trying to do here.
            - It was one of these:
                - https://pypi.org/project/traceback-with-variables/
                - https://pypi.org/project/pretty-traceback/#description
                - https://pypi.org/project/friendly-traceback/


        """
        plat = sys.platform
        supported_platform = plat != "Pocket PC" and (
            plat != "win32" or "ANSICON" in os.environ
        )
        print(supported_platform)
        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        print(is_a_tty)
        return supported_platform and is_a_tty

    def _disableColors(self, my_varsOnly):
        """Note, I have enable/disable color functions in both UTI and C... Not sure why I want both..."""
        for my_var in my_varsOnly:
            # print(my_var)
            if type(getattr(C, my_var)) == type(
                C._disableColors
            ):  ### If type of this var is same type as a function, ignore it.
                pass
            else:
                setattr(
                    C, my_var, ""
                )  ### Set the attributes of all of my vars of class C, to blank strings
        return

    def _enableColors(self, my_varsOnly):
        """Note, I have enable/disable color functions in both UTI and C... Not sure why I want both..."""

        return

############### Find which class was exported ################
statements = [
    "from print_tricks import pt as",
    "from print_tricks import p as",
    
    "from print_tricks import pt",
    "from print_tricks import p",
    
    "import print_tricks",
    "from print_tricks import *",
    "from print_tricks import PT",
]   
def find_which_was_exported():
# stack = traceback.extract_stack()
# ... ###db(stack)
# file_path, line_no, func_name, code = stack[0]
# ... ###db(code)
# ... ###db('---------------')
# for frame_summary in stack:
#     file_path, line_no, func_name, code = frame_summary
#     ... ###db(code)

    stack = traceback.extract_stack()
    all_lines = [frame.line for frame in stack]



    for i, line in enumerate(all_lines):
        if not line.strip().startswith('#'):
            for import_str in statements:
                if import_str in line:
                    return line
import_line = find_which_was_exported() if not None else "from print_tricks import pt"
# print(f'{import_line}')







############### main class pt - Import only this into any files ################
class pt:
    ##  TODO TODO NOTE: Not actually sure if these slots are helping at all... The time appears to be the same, 
    # but theoretically, it's saving on some memory and
    ## some tiny amount of time that may or may not add up...
    __slots__ = (
        "variables",
        "str_front",
        "str_back",
        "mvl",
        "print_this",
        "print_always",
        "end",
        "sep",
        "file",
        "flush",
        "line_no",
    )
    ############### pt vars for Class #################
    placeholder = 0.0
    orig_garb_collect_state = True
    del_setup_time = 0.0
    time_of_this_own_function = 0.0

    detailed_descriptions = False
    loops_through_pause = 0
    disable_this_after_pause_q = False
    enable_if_after_loops = 0
    pause_completed = 0

    ## For Fast pt prints of rapid print calls
    rapid_pt_bulk_print_block = ""
    sent_bulk_print_to_thread = False
    last_bulk_print_time = 0.0
    time_to_print = time.time()
    num_pt_count = 0
    bulk_print_list = []

    """ WARNING NOTE WARNING: Do not set these manually using "pt.print_deletes" etc.. 
        Always use "pt.disable(function_type)", so that it's handled correctly with a warning & reminder message. """
    print_deletes = True
    print_exceptions = True
    print_threads = True
    # print_infos       = True ### Should change this to "print Variables"
    print_locations = True
    print_pauses = True
    print_pt_statements = True
    print_timers = True
    print_waits = True
    print_pt_help = True
    print_colors = True
    print_colors_tags = True
    print_prefs = True
    print_profile_resources = True

    FUNC_AND_DICT_NUM = 4
    ## pt.t() timer dict
    sequences_dict = {}
    sequence_counters = {}
    sequence_args_dict = {}
    sequence_amt_del_dict = {}
    line_no_dict = {}

    ## pt.wait() dict:
    tag_waits_dict = {}
    ## pt.r() / release_enable dict:
    release_enable = {}

    ## UTI._simple_trace Vars:
    default_trace_level = -3
    new_trace_level = default_trace_level  ## I've moved the new_trace_level out of _simple_trace and to here, so that I can debug my own print_tricks statements using ... ###db() now. 
    ## Set to -3, because it'll skip the trace that actually retrieves the traceback "traceB = traceback.extractStack()", and it will
    ## then skip the function in init that calls my simple trace "simpTrace = UTI._simple_trace(argsLen)", finally landing on the 3rd next piece
    ## of code which ends up being the first line of code that was just ran in whatever app/call is outside of print_tricks.

    is_multi_pt_in_one_line = False  ## When there is more than one pt type statement on one line, like via seprated with ";"

    current_pt_on_multi_line = 0  ## keeping track of where we are on the ";" line to find the correct var.

    cur_exec_str = ""

    mag_dict_div = {
        "years": 31556952,
        "months": 2629800,
        "weeks": 604800,
        "days": 86400,
        "hours": 3600,
        "m": 60,
    }

    magnitude_dict_multiply = {
        "s" : 1000000000,
        "ms": 1000000,
        "us": 1000,
        "µs": 1000,
        "ns": 1,
    }

    easy_import_paths = set()
    
    counter_count = 0
    
    ## for pt.every()
    every_seconds_start = time.time()
    every_count = 0
    
    ## for pt.after()
    after_seconds_start = time.time()
    after_count = 0
    

    ############### Main PT functions #################

    def __init__(
        self,
        *variables,
        str_front=None,
        str_back=None,
        mvl=65,
        print_this=True,
        print_always=False,
        end="\n",
        sep=" ",
        file=None,
        flush=False,
        _line_no=None,
    ):
        """Currently supports printing variables, strings, or combinations of variables/strings using the + concatenator (not using commas "," etc)"""
        """ Parameters:
            - str_front: String to print before the variables.
            - str_back: String to print after the variables.
            - mvl: Max Var lines: The maximum lines to print of for each variable. 
            - print_always: If true, will print this statement even if all other pt statement prints have been turned off from printing. 
            - end/sep/file/flush are all default python arguments, and can be used for:
                - End: The character to print at the end of the statement.
                - Sep: The character to print between each variable.
                - File: The file to print to. (note, this will turn off some pt() behaviors in order to comply with a text file format. Like turning off console colors etc). 
                - Flush: If true, will flush the file after printing.
                
            """

        """ Now Plans = 
            - pt() - Fast single-line prints for rapid statements:
                - Avoid the slowdown that happens when you have your print statements printing rapidly. These statements will slow down your code tremendously. 
                - We can fix this by:
                    - We check the time between this pt statement and the last. If it is less than ___ seconds, we simply append all of the data that would 
                    have been printed (the whole line, with colors, line numbers etc)
            """

        if (
            print_this is False
            or pt.print_pt_statements is False
            and print_always is False
        ):
            return

        UTI.startup_print_tricks_times["pt()__init__"] = time.perf_counter()
        variables_len = len(variables)

        ## TEST SIMP TRACE OUTPUT SPEED IF I WERE TO eliminate traceback and GET THE LINE NUMBERS AND FORMATTING/STRINGS FIRST EXCEPT FOR THE ACTUAL VALUE OF THE VAR AT THE TIME)
        ## THE SPEED DIFFERENCE: 6-8ms for python print. 87ms for mine with traceback. 17ms for mine if traceback is basically eliminated.
        # simpTrace_output = ('print_tricks.py', 'i:\\.PythonProjects\\Print Tricks\\print_tricks.py', 4943, '', '', 'pt(num423)', 'num423', 'num423', '\x1b[33mnum423\x1b[0m', ['\x1b[33mnum423\x1b[0m'])

        simp_trace_output = UTI._simple_trace(variables_len)
        # simp_trace_output = UTI._simple_trace_new(variables_len)
        # simp_trace_output = ind.fast_trace_viability_test()

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = simp_trace_output
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no
        # print('code:\n', code, '\n')

        ## REMOVED ALL STRINGS "FEATURE"
        # all_is_str = UTI._allStringsQ(args)
        # ... ###db(args_with_specials, args_only, formatted_args, fmt_args_list)
        if variables_len == 0 and str_front is None:
            print(f"pt() (Line :{line_no}, {func_name_fmt}{file_name})")

        ## REMOVED ALL STRINGS "FEATURE"
        # elif all_is_str == True:
        #     ## if Not the last var in variables, then add a space after the variable, and append to final string. Else it's the last, so just append the variable.
        #     strfinal = ''
        #     for count, variable in enumerate(variables):
        #         if count < variables_len -1:
        #             strfinal += f'{variable} '
        #         else:
        #             strfinal += f'{variable}'

        #     fromType = ''

        #     if variables_len > 1:
        #         fromType = '(in tuple)' # If the strings were originally a tuple of strings, we will declare it

        #     print(f'{C.t1}{strfinal}{C.er} - pt({C.t2}{args_only}{C.er}) - str{fromType}, Length: {len(strfinal)}, (Line :{line_no}, {func_name_fmt}{file_name})')
        else:
            UTI._info(
                simp_trace_output,
                variables_len,
                variables,
                args_only,
                str_front=str_front,
                str_back=str_back,
                mvl=mvl,
                end=end,
                sep=sep,
                file=file,
                flush=flush,
            )

        return

        # end def init

    def c(
        string="",
        colors=None,
        print_always=False,
        end="\n",
        sep=" ",
        file=None,
        flush=False,
        _line_no=None,
    ):
        """Adds simple colored text to strings only. No extras. Just like a standard print, but with whatever colors/effects
        you want"""
        if pt.print_colors == False and print_always != True:
            return
        combined_colors = ""
        if type(colors) is list or type(colors) is tuple:
            for i, color in enumerate(colors):
                if i == 0:
                    combined_colors = f"{color[:-1]};"
                elif i == len(colors) - 1:
                    combined_colors += f"{color[2:]}"
                else:
                    combined_colors += f"{color[2:-1]};"

        elif colors is None:
            combined_colors = C.t1  ## sets default color
        else:
            combined_colors = colors  ## if there is just one color

        print(
            f"{combined_colors}{string}{C.er}",
            end="\n",
            sep=" ",
            file=None,
            flush=False,
        )

        return
        # end def c

    def ci(
        string,
        colors=None,
        print_always=False,
        end="\n",
        sep=" ",
        file=None,
        flush=False,
        _line_no=None,
    ):
        """Prints a colored string with the extra details that normally print with PT statements (line numbers, file location, etc)
        - must use the color/formatting commands found in the color class C.
            - For example:
                pt.ci('hello', C.t1)
        -
        """
        if pt.print_colors_tags == False and print_always != True:
            return
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace(1)

        ### Goal of the following block, is to combine the Ansi codes in a way that they are allowed to be combined, so cutting off bits of the front
        ###   and back to make them work together. For example, the 3 color codes (C.eb, C.fr, C.bw)
        ###   separately in Ansi would be: ('\x1b[1m','\x1b[31m', '\x1b[47m'), But are only valid when combined like this: '\x1b[1;31;47m'
        combined_colors = ""
        if type(colors) is list or type(colors) is tuple:
            for i, color in enumerate(colors):
                if i == 0:
                    combined_colors = f"{color[:-1]};"
                elif i == len(colors) - 1:
                    combined_colors += f"{color[2:]}"
                else:
                    combined_colors += f"{color[2:-1]};"

        elif colors is None:
            combined_colors = C.t1  ## sets default color
        else:
            combined_colors = colors  ## if there is just one color
        print(
            f"{combined_colors}{string}{C.er} - pt.ci({C.t2}{args_only}{C.er}) (Line :{line_no}, {func_name_fmt}{file_name})",
            end="\n",
            sep=" ",
            file=None,
            flush=False,
        )

        return
        # end def ci

    def counter(
        str_front="",
        str_back="",
        print_this=True,
        print_always=False
        ):
        
        '''
        A counter that will count how many times a certain function is called.
        '''
        
        if (
            print_this is False
            or pt.print_pt_statements is False
            and print_always is False
        ):
            return
        
        my_string, filler = UTI._custom_str(str_front)
        
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no
        
        pt.counter_count += 1

        print(
            f"\n{NAM.inst_nam}.counter({C.t1}{formatted_args}{C.er}): "
            f"{C.t2}{pt.counter_count}{C.er} "
            f"(Line :{line_no}, {func_name_fmt}{file_name}) {str_back}\n")

    def counter_fast(
        str_front="",
        str_back="",
        print_this=True,
        print_always=False
        ):
        
        '''
        A counter that will count how many times a certain function is called.
        '''
        
        if (
            print_this is False
            or pt.print_pt_statements is False
            and print_always is False
        ):
            return

        pt.counter_count += 1

        print(
            f"\n{NAM.inst_nam}.counter_fast({str_front}): "
            f"{C.t2}{pt.counter_count}{C.er} {str_back}"
        )

    def delete(
        delete_what="",
        replace_with="",
        file_to_edit=None,
        print_always=False,
        _line_no=None,
    ):
        """Currently acts as a "Find and Replace" command but allows you to delete/replace ANYTHING in ANY FILE in your computer.
        The default is the current file that you are entering the command into, unless you input the file_to_edit.

        Next Version:
            Be able to target all pt.#() statements, or specific types of statements (like all pt.p()).

        NOTE A purposeful conflict with a parameter for pausing on pt.p() exists for safety reasons:
        If disable_this_after_pause is set to true within an app that has pause functions, calling this pt.delete()
        function will auto-disable the disable_this_after_pause parameter as a safety mechanism to ensure that the pt.delete
        function can ask the user for permission before proceeding with the deletion.

        """
        if pt.print_deletes == False:
            if print_always == True:
                pass
            else:
                return
        # if file_to_edit ==None:
        #     file_to_edit=''
        if replace_with == None:
            replace_with = ""

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no
        # ... ###db(code)

        dir_only = os.path.split(file_path)[0]

        ## NOTE: THIS IS PROBABLY A TEMPORARY SOLUTION BELOW. Without this code, my pt.delete('') statements come up strange. This temporary band-aid will work fine for
        ## these delete statements, but I think other similar problems could happen in other pt.___ statements if I don't have a more low level solution to this.
        # if '.delete' in args_only:
        #     args_only = args_only.replace('.delete', '')

        if file_to_edit == None:
            my_file = file_path
            # ... ###db(1)
        elif ":\\" in file_to_edit or ":/" in file_to_edit:
            ## We are seeing if it's a full path, like C:/ or C:\
            my_file = file_to_edit
            # ... ###db(2)
        else:
            my_file = dir_only + "\\" + file_to_edit
            # ... ###db(3)

        num_instances = 0
        with open(my_file) as f:
            for line in f:
                if delete_what in line:
                    num_inst_this_line = line.count(delete_what)
                    num_instances += num_inst_this_line  ### We are saying to count how many instances show up on the line and add them to the current num_instances
        f.close()

        print(
            f"pt.delete({C.t2}{formatted_args}{C.er})"
            f" - (Line :{line_no}, {func_name_fmt}{file_name}"
        )
        if num_instances == 0 or delete_what == "":
            pt.p(
                "y",
                f"There are currently {C.t2}{C.eb}{C.eu}NO{C.er}"
                f' instances of "{C.t3}{delete_what}{C.er}" to delete',
                disable_this_after_pause=False,
                print_always=True,
                print_originating_code=False,
            )
        else:
            len_num_instances = len(str(num_instances))
            pt.p(
                "y",
                f"{C.er}Are you sure you want to {C.t2}DELETE/replace{C.er} all "
                f'{C.t2}{C.eb}{C.eu}{num_instances}{C.er} of {"these" if len_num_instances > 1 else "this"} '
                f'data instance(s): "{C.t3}{delete_what}{C.er}"? {"They" if len_num_instances > 1 else "It"} '
                f'will be replaced with: "{C.t3}{replace_with}{C.er}".',
                disable_this_after_pause=False,
                print_always=True,
                print_originating_code=False,
            )
            UTI._delete_it(my_file, delete_what, replace_with, num_instances)

        return
        # end def delete

    def delete_new(_line_no=None):
        """The main improvements to this deletion method, is to focus on the ability to delete any and all print statements. So it looks for and recognizes print() statements and pt() and pt.*() statements.
        - It can delete all types of statements in general
            -do this: delete_what = 'print(*)'
                - This will delete all print statements that have anything in between the brackets. This will work for 'pt(*)' as well as UTI._info(*) and the others.
        - It can also specifically target just the type of print statements that match it exactly. Like this: delete_what = 'print(time.time())'

        A further new delete system:
            -A more future version will utilize the pt.f Find function to look for data wherever, and then delete it.
        """

        return
        # end def delete_new

    def disable(function_type=None, _line_no=None, print_this=True):
        """pt.disable() = Disabling pt functions won\'t stop the initial check. While each check is resource-friendly, taking 1/5th of a billionth of a second can still add up to 200 milliseconds extra processing if your loop runs a billion times (based on i5 CPU from era 2014). If your app requires such extensive loop processing and precision timing is necessary, just comment out each pt line directly."""
        class_name, function_type = UTI._enable_disable_type_class_name_func_type(
            function_type
        )

        UTI._turn_on_off_functions(function_type, "disable")

        if print_this == True:
            print(
                f"{C.t3}~Notice: {class_name}{function_type}() statements have been {C.t1}disabled.~{C.er}",
                f"\n\t> {C.t3}Comment out or Disable pt() & python print() statements when profiling/measuring the performance of your code.{C.er}",
            )
        return
        # end def disable

    def enable(function_type=None, _line_no=None, print_this=True):
        """pt.enable ."""
        class_name, function_type = UTI._enable_disable_type_class_name_func_type(
            function_type
        )

        UTI._turn_on_off_functions(function_type, "enable")

        if print_this == True:
            print(
                f"{C.t3}~ {class_name}{function_type}() statements have been {C.t1}re-enabled.~{C.er}"
            )

        return
        # end def enable

    def e(
        error_msg="",
        
        str_front=None,
        str_back="",
        msg_type="simple",
        full_trace = False,
        print_file_loc="",
        print_always=False,
        _line_no=None,
    ):
        """Exception Handling with all relevant _information {}
        - Will only work if placed inside of the 'except:' section of a 'try/except' statement
        - For example:
            try:
                (print(len(int)))
            except:
                pt.e()

        """
        full = False
        if msg_type == "full" or msg_type == "fullType" or full_trace is True:
            full = True
        if pt.print_exceptions == False and print_always != True:
            return
        my_string, filler = UTI._custom_str(str_front)

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


        dir_only = os.path.split(file_path)[0]

        detailed_intro = ""
        if error_msg:
            detailed_intro = f"{C.t3}<<<Error Details: {C.er}"

        # error_type = ''
        culprit, error_type = UTI._error_trace_simple()
        if full == False:

            print(
                f"{C.t2}<<<Error>>> {C.er}"
                f"{C.t1}{my_string}{C.er}{filler}pt.e(): {C.t3}{error_type}{C.er}"
                f" (Line :{C.t4}{line_no}{C.er}, {func_name_fmt}{file_name}) {C.t1}{str_back}{C.er}\n"
                f"{C.t3}<<<Code with Error: {C.t4}{culprit}{C.er}\n"
                f"{detailed_intro}{error_msg}\n"
            )
        else:
            _error_trace_full = UTI._error_trace_full()
            print(f"\n{_error_trace_full}")
            print(
                f"{C.t2}<<<Error - Full Traceback Above. Summary: >>> {C.er}"
                f"{C.t2}<<<Error>>> {C.er}"
                f"{C.t1}{my_string}{C.er}{filler}pt.e(): {C.t3}{error_type}{C.er}"
                f" (Line :{C.t4}{line_no}{C.er}, {func_name_fmt}{file_name}) {C.t1}{str_back}{C.er}\n"
                f"{C.t3}<<<Code with Error: {C.t4}{culprit}{C.er}\n"
                f"{detailed_intro}{error_msg}\n"
            )

        _readable_time = ""
        if print_file_loc != "":
            error_save_loc = dir_only + "\Error_Logs\\" + print_file_loc
            os.makedirs(os.path.dirname(error_save_loc), exist_ok=True)
            unixTime = time.time()
            _readable_time = UTI._readable_time(unixTime)
            with open(error_save_loc, "a") as f:
                f.write(f"{_readable_time} {_error_trace_full}")
        return
        # end def e

    def easy_testing(name=None):
        '''
        Tags: 
            easy_testing aka run_project_here, run_from_here, run from here, run_here, run here, easy testing easy def easy testing def project run here def run project here, run_this_as_main, run_project_here
        
        Explanation:
            A utility class for setting up the working directory and environment for testing or running scripts.
            Ensures the script runs from the correct directory by updating `sys.argv[0]` and setting the current working directory.
        
        Useful for: 
            - You want to run a script that is several subdirectories down from your main project, and you want this script
            to access another subfolder right next to it (like an assets folder in this location). 
        
        Optimization:
            pass in __name__ for fastest time. Or leave blank if don't feel like it. 
                easy_testing(__name__)      5u - 12u microseconds
                easy_testing()              5ms - 6ms milliseconds
            
        Use only:
            - Use within "if __name__ == 'main':" 
            (because this is useful when this script is ran directly, as the main)
            '''
        
        if name == '__main__':
            cwd = os.getcwd()
            os.chdir(cwd)
            sys.argv[0] = cwd
            ### NOTE: 12u microseconds
            
        elif name is None:
            current_file = inspect.stack()[-1].filename
            file_path = Path(current_file).resolve()
            _main_file_path = Path(sys.argv[0]).resolve()
            
            if file_path == _main_file_path:
                cwd = os.getcwd()
                os.chdir(cwd)
                sys.argv[0] = cwd
                
            ### NOTE: 6ms milliseconds, if you don't include __name__ in the arguments. 

    @staticmethod
    def easiest_imports(*import_paths, add_intermediate_paths=True, exclude_dirs=None):
        """
        Explanation:
        - Enhanced version of easy_imports that automatically adds all parent directories 
        between the calling script and the current working directory.
        - Also adds specified directories to `sys.path` for easier module imports.
        - Handles both absolute and relative paths, and skips redundant paths.
        
        Parameters:
        - *import_paths: Optional additional paths to add to sys.path
        - add_intermediate_paths: Whether to add intermediate directories between target paths
        - exclude_dirs: List of directory names to exclude (e.g., "__pycache__", ".git")
        
        Used in:
        - Import at the very top of your file, before everything else.
        - Particularly useful when you need to access modules in parent directories
        without hardcoding paths.
        """
        # Default exclude directories
        if exclude_dirs is None:
            exclude_dirs = [
                "__pycache__",
                ".directory",
                ".Trashes",
                ".Python",
                ".pybuilder",
                ".ipynb_checkpoints",
                ".venv",
                ".git",
                ".vscode",
            ]
        
        # First, add all paths between the calling script and CWD
        current_file = inspect.stack()[-1].filename
        calling_file_path = Path(current_file).resolve()
        cwd_path = Path(os.getcwd()).resolve()
        
        # Check if the calling file path is already in our tracked paths
        if str(calling_file_path.parent) not in pt.easy_import_paths:
            # Add the directory containing the calling script
            parent_dir = calling_file_path.parent
            if str(parent_dir) not in sys.path:
                sys.path.append(str(parent_dir))
                pt.easy_import_paths.add(str(parent_dir))
                pt._print_easy_imports(parent_dir)
        
        # Add all parent directories between calling script and CWD
        parent_dirs = []
        
        # If calling file is not in CWD or its parents, we need to handle both paths
        if calling_file_path.parent != cwd_path and not any(p == cwd_path for p in calling_file_path.parents):
            # Collect parent directories of the calling file
            temp_path = calling_file_path.parent
            while temp_path != temp_path.parent:  # Until reaching root
                parent_name = temp_path.name
                if parent_name not in exclude_dirs and str(temp_path) not in sys.path:
                    parent_dirs.append(str(temp_path))
                temp_path = temp_path.parent
                
            # Collect parent directories of CWD
            temp_path = cwd_path
            while temp_path != temp_path.parent:  # Until reaching root
                parent_name = temp_path.name
                if parent_name not in exclude_dirs and str(temp_path) not in sys.path:
                    parent_dirs.append(str(temp_path))
                temp_path = temp_path.parent
        else:
            # Determine which is the ancestor and which is the descendant
            if cwd_path in calling_file_path.parents:  # CWD is an ancestor of calling file
                temp_path = calling_file_path.parent
                while temp_path != cwd_path.parent:  # Until reaching parent of CWD
                    parent_name = temp_path.name
                    if parent_name not in exclude_dirs and str(temp_path) not in sys.path:
                        parent_dirs.append(str(temp_path))
                    temp_path = temp_path.parent
            else:  # Calling file is an ancestor of CWD
                temp_path = cwd_path
                while temp_path != calling_file_path.parent.parent:  # Until reaching parent of calling file's parent
                    parent_name = temp_path.name
                    if parent_name not in exclude_dirs and str(temp_path) not in sys.path:
                        parent_dirs.append(str(temp_path))
                    temp_path = temp_path.parent
        
        # Add all collected parent directories to sys.path
        for dir_path in parent_dirs:
            if dir_path not in pt.easy_import_paths:
                sys.path.append(dir_path)
                pt.easy_import_paths.add(dir_path)
                pt._print_easy_imports(dir_path)
        
        # Then handle any additional import paths using the existing easy_imports functionality
        if import_paths:
            pt.easy_imports(*import_paths, add_intermediate_paths=add_intermediate_paths)


    @staticmethod
    def setup_project_imports():
        ... ###db.c('setup project imports')
        # Get the absolute path of the script being executed
        calling_script = Path(sys.argv[0]).absolute()
        
        # Find project root (where this script is located)
        project_root = Path(__file__).parent.absolute()
        
        # Add project root to path if not already there
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Add all direct subdirectories to path
        for item in project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('__'):
                if str(item) not in sys.path:
                    sys.path.insert(0, str(item))

    setup_project_imports()

    # @staticmethod
    # def setup_project_imports(self, add_subdirs=True):
    #     """
    #     Add the project root and optionally its subdirectories to the Python path.
        
    #     Args:
    #         add_subdirs (bool): Whether to add direct subdirectories to path
    #     """07
    #     import os
    #     import sys
    #     from pathlib import Path
        
    #     # Find project root (try to find the root of the current project)
    #     calling_script = Path(sys.argv[0]).absolute()
    #     project_root = calling_script.parent
        
    #     # Add project root to path if not already there
    #     if str(project_root) not in sys.path:
    #         sys.path.insert(0, str(project_root))
    #         print(f"Added project root to path: {project_root}")
        
    #     # Add all direct subdirectories to path if requested
    #     if add_subdirs:
    #         for item in project_root.iterdir():
    #             if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('__'):
    #                 if str(item) not in sys.path:
    #                     sys.path.insert(0, str(item))
    #                     print(f"Added directory to path: {item}")
        
    #     return project_root


    def _append_parents_to_sys_path(source):
        ''' Status: 
                Currently unused (Supposed to be a part of easy_imports)
            Goal: 
                To append all paths between the source file, and the current file location
                Note: So far, with my one test, has not helped me to negate the issue of
                different import statements depending on where we reside. 
            Technique: 
                If it worked, I would use this code: 'pt._append_parents_to_sys_path(source)'
                right before a return statement within pt.easy_imports
            '''
        source_path = Path(source).resolve()
        current_file = inspect.stack()[-1].filename
        current_file_path = Path(current_file).resolve()
        pt(current_file, source_path, current_file_path)

        # Get all parent directories of the current file until the source directory
        parent_dirs = []
        while current_file_path != source_path:
            parent_dirs.append(str(current_file_path))
            current_file_path = current_file_path.parent

        # Append all parent directories to sys.path
        for dir in parent_dirs:
            if dir not in sys.path:
                sys.path.append(dir)

    def _print_easy_imports(path, msg=''):
        pt.new_trace_level -= 1
        file_name, file_path, line_no, func_name, func_name_fmt, code, args_with_specials, args_only, formatted_args, fmt_args_list  = UTI._simple_trace(-1)
        
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        
        import_str = f"{C.t1}  > {'successful' if str(path) in sys.path else 'Did not complete: '}{C.er}" \
                    f" - The directory {C.t2}'{path}'{C.er} {'is now' if str(path) in sys.path else 'does not exist and was not'} added to the system path.{C.er}"
                    
        if msg != '':
            msg_str = '\n'.join([
                textwrap.fill(
                    text, 
                    initial_indent='  > ', 
                    width=terminal_width,
                ) 
                for text in textwrap.dedent(msg).split('\n')
            ])
            msg_str += '\n'
        else:
            msg_str = ''
            
        print_str = (
            f"{NAM.inst_nam}.easy_imports({formatted_args}): "
            f"(Line :{line_no}, {func_name_fmt}{file_name})\n"
            f"{msg_str}"
            f"{import_str}\n"
        )
        print(print_str)
        return

    def any_imports(root_dir=".", excludes=[]):
        _excludes = [
            "__pycache__",
            ".directory",
            ".Trashes",
            ".Python",
            ".pybuilder",
            ".ipynb_checkpoints",
            ".venv",
            ".git",
            ".vscode",
        ]
        _excludes += excludes
        for (dir_path, dir_names, file_names) in os.walk(root_dir):
            if any(ex in dir_path for ex in _excludes):
                continue  # Skip this directory as it's in the exclude list
            sys.path.insert(0, dir_path)
            print(dir_path)

    def all_imports(*import_paths):
        ...

    @staticmethod
    def easy_imports(*import_paths, add_intermediate_paths=True):
        """
            Explanation:
            - A utility class for managing import paths (`sys.path`) to resolve module import issues.
            - Adds specified directories to `sys.path` for easier module imports, handling both absolute and relative paths.
            - Skips redundant paths and optionally includes intermediate directories for comprehensive path resolution.
            
            Useful for:
            - Seeing imports that you shouldn't actually be able to access (imports from levels above)
            - Adding a directory to the Python path without hardcoding the full path.
            - Automatically managing dependencies for scripts that need to access specific files or modules.
            
            Used in:
            - import at the very top of your file, before everything else. 
            - Can possibly use it in "if name is main" section. 
        """
    

    
    
        ## Unpack the single list or tuple argument
        if len(import_paths) == 1 and (isinstance(import_paths[0], list) or isinstance(import_paths[0], tuple)):
            import_paths = import_paths[0]   
            
        ## Quick return if all import_paths are already in sys.path
        if len(import_paths) == 1:
            if import_paths[0] in pt.easy_import_paths:
                return
        
        ## Empty path passed
        if not import_paths:
            pt._handle_empty_path(add_intermediate_paths)
            return

        ## Quick return if all path_dirs are already in the set
        all_in_import_paths = all(src in pt.easy_import_paths for src in import_paths)
        if all_in_import_paths:
            return

        ## If one or more import_paths
        for path in import_paths:
            if not path:  # Skip empty paths
                continue

            ## Add all import_paths to our set
            if path not in pt.easy_import_paths:
                pt.easy_import_paths.add(path)
                
            if os.path.isabs(path):  # Handle absolute paths
                # pt()
                pt._handle_full_path(path, add_intermediate_paths)
            else:  # Handle relative paths
                # pt()
                current_file, file_path, _, parent, _main_file_path = pt._get_file_info()
                if file_path == _main_file_path:
                    pt._handle_partial_path(path, parent, add_intermediate_paths)

    def _handle_full_path(path, add_intermediate_paths=False):
        if os.path.exists(path):
            if path not in sys.path:
                if add_intermediate_paths:
                    pt.add_paths_to_sys_path(target_path=path, add_intermediate_paths=add_intermediate_paths)
                else:
                    pt.append_path_and_print(path)
        else:
            ## If the path does not exist, print a message indicating this
            pt._print_easy_imports(path=path, msg=f"The path {path} does not exist.")

    @staticmethod
    def _handle_partial_path(path, parent, add_intermediate_paths=False):
        
        similar_paths = []
        root_reached = False
        while parent:
            list_dir_parent = os.listdir(parent)
            if path in list_dir_parent:
                if '.py' not in path:
                    parent = parent / path
                if add_intermediate_paths:
                    pt.add_paths_to_sys_path(target_path=parent, add_intermediate_paths=add_intermediate_paths)
                else:
                    pt.append_path_and_print(path=parent)
                return
            else:
                similar_paths = pt._check_similar_paths(path, list_dir_parent, parent, similar_paths)
            if root_reached:
                pt._handle_root_reached(path, similar_paths)
                return
            parent = parent.parent
            if parent == parent.parent:
                root_reached = True

    @staticmethod
    def _handle_empty_path(add_intermediate_dirs=False):
        target_path = os.getcwd()
        pt.new_trace_level -= 1

        pt.add_paths_to_sys_path(target_path, add_intermediate_dirs)

    @staticmethod
    def add_paths_to_sys_path(target_path, add_intermediate_paths=False):
        caller_frame = inspect.stack()[1]
        start_path = Path(os.path.dirname(caller_frame.filename))
        target_path = Path(target_path)

        ## Make sure the target_path is an ancestor before possibly adding the
        ## intermediate paths
        if start_path in target_path.parents or target_path in start_path.parents:
            ## Add all directories from start_path to target_path to sys.path if requested
            if add_intermediate_paths:
                path_to_add = start_path
                while path_to_add != target_path:
                    pt.append_path_and_print(path_to_add)
                    if path_to_add == target_path.parent:
                        break
                    # Determine next path to move towards target_path
                    path_to_add = path_to_add.parent if target_path in path_to_add.parents else path_to_add / path_to_add.relative_to(target_path.parent)
        
        ## Ensure the target_path itself is added to sys.path
        pt.append_path_and_print(target_path)

    def append_path_and_print(path):

        if str(path) not in sys.path:
            sys.path.append(str(path))
            pt.new_trace_level -= 2
            pt._print_easy_imports(path=path)

    @staticmethod
    def _get_file_info():
        current_file = inspect.stack()[-1].filename
        file_path = Path(current_file).resolve()
        filename = file_path.name
        parent = file_path.parent
        _main_file_path = Path(sys.argv[0]).resolve()
        return current_file, file_path, filename, parent, _main_file_path

    @staticmethod
    def _check_similar_paths(path, list_dir_parent, parent, similar_paths):
        for dir in list_dir_parent:
            ratio = difflib.SequenceMatcher(None, path.lower(), dir.lower()).ratio()
            if ratio > 0.44:
                possible_mistyped_path = parent / dir
                similar_paths.append((possible_mistyped_path, dir, ratio))
        return similar_paths

    @staticmethod
    def _handle_root_reached(path, similar_paths):
        if similar_paths:
            similar_paths.sort(key=lambda x: x[2], reverse=True)
            combined_message = "\n".join([
                f"{C.t2}{dir}{C.er} - '{path}'  ({C.t1}{score:.0%}{C.er} similar)"
                for path, dir, score in similar_paths
            ])

            pt.new_trace_level -= 2
            pt._print_easy_imports(path=path, msg=
                f'Did not find "{C.t2}{path}{C.er}", but found similar path(s):\n'
                f'Did you mean to type in one of these?\n\n'
                f'{combined_message}\n')
        else:

            pt.new_trace_level -= 2
            pt._print_easy_imports(path=path, msg="That doesn't seem to exist, ")



    
    def ex(*args, print_originating_code=True, _line_no=None):
        """exit app, quit app, end app. pt.exit, pt.ex, pt.quit, pt.end"""
        
        ## Can accept anything (like a string for easy diagnoses). But takes
        ##  the first int and uses this as the status code.
        exit_status_code = 0
        for arg in args:
            if type(arg) is int:
                exit_status_code = arg
        
        
        simp_trace_output = UTI._simple_trace()
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = simp_trace_output
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


        if print_originating_code == True:
            print(
                f"{C.t2}>>>Exited App<<<{C.er} - pt.ex({C.t2}{formatted_args}{C.er}): (Line :{line_no}, {func_name_fmt}{file_name})")
        else:
            print(f"{C.t2}>>>Exited App<<<{C.er} - pt.ex()")
        pt.pause_completed = 1
        sys.exit(exit_status_code)

    def h(function_thread=None, get_results=False, str_front=None, str_back='', daemon=True, print_always=False, *args, _line_no=None, **kwargs):
        '''
        - Re-Do: pt.h()
            - If no args passed, just print out thread number
            - If function passed (search for:   if "()" in code:  ), then send the argument to a function
                -Example: pt.h(myFunction) - Then the pt.h() turns into a threading.thread thing.
                (Finishing this will bring module to 0.62)
            - if returnVar is passed, swap to save_thread_with_result function
                - Example: pt.h((myFunction, args, kwargs), testVar)
                    -This will look for "return testVar" in the threaded function and return that result. 
                (Finishing this will bring module to 0.65)
        '''
        if pt.print_threads == False:
            if type(function_thread) == type(pt.h) or type(function_thread) == type(open): ## NOTE: This is a workaround to check if our passed variable is a function by comparing it's type to any existing user-created function and also testing against a python built-in function. If either of these is true, because it is indeed some type of function, then do the code. 

                pass
            elif print_always != True:
                # print('return')
                return
            '''NOTE print_always defaults to True for pt.h statements that have a function attached because they are likely an integral part of your code. 
            However, it allows the turning off of pt.h statements purely meant to show your thread number '''

        thread_id = threading.get_ident()
        process_id = os.getpid()
        file_name, file_path, line_no, func_name, func_name_fmt, code, args_with_specials, args_only, formatted_args, fmt_args_list  = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        ## This interprets a pt.h('string') as a simple message, being passed, not a function.
        if type(function_thread) == str:
            str_front = function_thread
        my_string, filler = UTI._custom_str(str_front)

        ## TODO: I think the "or type(function_thread) == str' will no longer be relevant because this is handling a str in the code, but I will be
        #   ## sending all code extras through a custom print function that has all same functionality as tradtional print statements. "
        if function_thread is None or type(function_thread) == str:

            print(
                f'{C.t1}{my_string}{C.er}{filler}'
                f'pt.h({formatted_args}): '
                f'{C.t2}Thread ID: {C.er}'
                f'{C.t3}{thread_id}{C.er}. '
                f'{C.t2}Process ID: {C.er}'
                f'{C.t3}{process_id}{C.er} - '
                f'(Line) :{line_no}, {func_name_fmt}{file_name} - {C.t1}{str_back}{C.er}'
                )

        elif function_thread != '':

            if get_results == False:
                # print('if get_results False')
                ## do normal thread
                threading.Thread(target=function_thread, daemon=daemon, args=args, kwargs=kwargs).start()
                
                return
            elif get_results == True:
                # print('if get_results True')

                thread = ThreadWithResult(target=function_thread, daemon=daemon) ## We are setting daemon to daemon because it'll take the true/false and add it in here.
                thread.start()
                thread.join()
                if getattr(thread, 'result', None):
                    return thread.result
                else:
                    print('ERROR! Something went wrong while executing this thread, and the function you passed in did NOT complete!!')

        return
        # end def h

    def hr(
        function_thread=None,
        get_results=True,
        str_front=None,
        str_back="",
        daemon=True,
        print_always=False,
        _line_no=None,
    ):
        """This function shortcuts all data to the pt.h() function, but sets "get_results=True" just to save time."""
        return pt.h(function_thread, get_results, str_front, str_back, daemon, print_always)
        # end def hr

    def help(_line_no=None):
        """A supplemental alternative name for def pt"""
        """NOTE It's supposed to be bad practice to name your own function after python functions, right? """
        print("help")
        # end def help

    def l(
        passedfile_name=None,
        getFile=False,
        print_this=False,
        print_always=False,
        _line_no=None,
    ):
        """NOTE WE DO NOT PUT IN THE TURN OFF STATEMENT AT THE TOP FOR PT.L instead we place it just at the print statement location. That way we can still get the return on this location and use it throughout our code, regardless of whether we want it to print or not."""
        this_File = ""
        new_File = ""

        ### Setting File & Path _info: ###
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        # print('file_name: ', file_name)
        # print('file_path: ', file_path)
        dir_only = os.path.split(file_path)[0]
        # print('path only: ', dir_only)
        file_path_andSlash = dir_only + "\\"
        this_File = file_path_andSlash + file_name

        ### Setting up the new File Name parameter ###
        if passedfile_name is None:
            new_File = None

        else:
            # print(' else, we DID pass pass a file_name')
            new_File = file_path_andSlash + passedfile_name

        ### printing only if the printing bools are set to true
        if print_this == True:
            if pt.print_locations == False and print_always != True:
                return new_File, this_File, dir_only

            print(
                f"pt.l({formatted_args}) - {C.t2}New File:  {C.t3}{new_File}{C.er} - (Line :{str(line_no)}, {func_name_fmt}{file_name})"
            )
            print(
                f"pt.l({formatted_args}) - {C.t2}This File: {C.t3}{this_File}{C.er} - (Line :{str(line_no)}, {func_name_fmt}{file_name})"
            )
            print(
                f"pt.l({formatted_args}) - {C.t2}Path Only: {C.t3}{dir_only}{C.er} - (Line :{str(line_no)}, {func_name_fmt}{file_name})"
            )

        if passedfile_name is not None:
            return new_File
        elif getFile == True:
            return this_File
        else:
            return dir_only
        # end def l

    def _get_func_values(passed_func):
        source = inspect.getsource(passed_func)
        # ... ###db(source)
        source = source.lstrip()
        parsed = ast.parse(source)
        # ... ###db(parsed)
        var_dict = {}

        for node in ast.walk(parsed):
            if isinstance(node, ast.Assign):
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    var_name = target.id
                    var_value = ast.literal_eval(node.value)
                    var_dict[var_name] = var_value

        return var_dict

## pt_line = f"{NAM.inst_nam}.props({C.t1}{formatted_args}{C.er}) - (Line :{str(line_no)}, {func_name_fmt}{file_name})\n



    @staticmethod
    def props(passed_obj):
        if not callable(passed_obj):
            warning_msg = 'pt.props() requires a callable, like a function or a class, not a ' + str(type(passed_obj))
            warnings.warn(warning_msg)
            return
        file_name, file_path, line_no, func_name, func_name_fmt, code, args_with_specials, args_only, formatted_args, fmt_args_list  = UTI._simple_trace()
        name = ''
        
        class_title         = f"  {C.t2}Class {passed_obj.__name__}{C.er}:\n"
        # method_title        =  ## can't keep this up here, look below under "if inspect.isfunction(value):"
        function_title      = f"  {C.t1}> {passed_obj.__name__}{C.er}\n"
        vars_title          = f"    {C.t3}> Vars{C.er}:\n"
        class_vars_title    = f"    {C.t3}> Class Vars{C.er}:\n"
        parameters_title    = f"    {C.t3}> Parameters{C.er}:\n"
        output = f"{NAM.inst_nam}.props({C.t1}{formatted_args}{C.er}) - (Line :{str(line_no)}, {func_name_fmt}{file_name})\n"

        def process_function(func):
            nonlocal output
            output += parameters_title
            params = inspect.signature(func).parameters
            if params:
                for param_name, param in params.items():
                    default_value = str(param.default)
                    if default_value.startswith("<") and len(default_value) > 1: ## NOTE: The > 1 logic is for cases like in ursina, where they have "start_tag = <", and thus the value will be only 1 in this instance, so we know it's not some sort of default object like "<property object at 00032234lb> " or whatever"
                        output += f"      > {param_name}\n"
                    else:
                        output += f"      > {param_name} = {default_value}\n"
            else:
                output += "            None\n"
            output += vars_title
            for name in func.__code__.co_varnames:
                if not name.startswith("__"):
                    output += f"      > {name}\n"
                    
        if inspect.isclass(passed_obj):
            output += class_title
            output += class_vars_title
            for name, value in passed_obj.__dict__.items():
                value_str = str(value)
                if not name.startswith("__") and not inspect.isfunction(value):
                    if value_str.startswith('<') and len(value_str) > 1: ## NOTE: The > 1 logic is for cases like in ursina, where they have "start_tag = <", and thus the value will be only 1 in this instance, so we know it's not some sort of default object like "<property object at 00032234lb> " or whatever"
                        output += f"      > {name}\n"
                    else:
                        output += f"      > {name} = {value_str}\n"
            for name, value in passed_obj.__dict__.items():
                if inspect.isfunction(value):
                    output += f"  {C.t1}> {name}{C.er}\n"
                    process_function(value)

        elif inspect.isfunction(passed_obj):
            output += function_title
            process_function(passed_obj)

        else:
            output += f"Error: The passed object is neither a class nor a function.\n"
            output += f"> Try using pt() or pass a function or\n"
            output += f"> class to pt.props() instead.\n"

        print(output)

    def p(
        what_key=None,
        str_front=None,
        str_back="",
        loops_2_activate=None,
        disable_this_after_pause=False,
        print_always=False,
        print_originating_code=True,
        _line_no=None,
    ):
        """Paused until a key is pressed (any key unless otherwise stated)"""
        if pt.print_pauses == False and print_always != True:
            return
        if disable_this_after_pause == True and pt.pause_completed > 0:
            return
        if loops_2_activate != None:
            if pt.loops_through_pause == loops_2_activate - 1:
                pt.loops_through_pause = 0
            else:
                pt.loops_through_pause += 1
                return

        key = None
        key_str = str(what_key)
        if what_key is not None:
            if (
                len(key_str) > 1
            ):  ## Can't count a key if it's more than one character, so instead set the multiple characters as the str_front
                str_front = key_str
                key_str = key_str.lstrip()
                key = key_str[0]
                key_str = key
            else:
                key = key_str
        if what_key is None or what_key == "":
            key_str = "Any"

        my_string, filler = UTI._custom_str(str_front)

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


        if print_originating_code == True:
            print(
                f"{C.t2}>>>Paused<<< {C.er}{my_string}\n"
                f"{C.t2}>>>Press{C.er} {C.t4}{C.eb}{key_str}{C.er} key to continue, "
                f"or press {C.t4}{C.eb}Esc{C.er} to Exit - pt.p({C.t2}{formatted_args}{C.er}): "
                f"(Line :{line_no}, {func_name_fmt}{file_name}) - {C.t1}{str_back}{C.er}"
            )
        else:
            print(
                f"{C.t2}>>>Paused<<< {C.er}{my_string}\n"
                f"{C.t2}>>>Press{C.er} {C.t4}{C.eb}{key_str}{C.er} key to continue, "
                f"or press {C.t4}{C.eb}Esc{C.er} to Exit {C.t2}<<<{C.er}"
            )

        global linux_Mac
        if linux_Mac is True:
            # tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            while True:
                try:
                    tty.setraw(sys.stdin.fileno())
                    kp = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(
                        fd, termios.TCSADRAIN, old_settings
                    )  ### This line might not be necessary
                if what_key is None:
                    key = kp

                if kp == r"\x1":
                    pt.exit_app()
                if kp == key:
                    print(f"{C.t2}>>>Continued{C.er}")
                    pt.pause_completed = 1
                    break
        else:
            # import msvcrt
            while True:
                kp = str(msvcrt.getch()).replace("b'", "").replace("'", "")
                if what_key is None or what_key == "":
                    key = kp

                if kp == r"\x1":
                    pt.exit_app(print_originating_code=False)
                if kp == key:
                    print(f"{C.t2}>>>Continued{C.er}")
                    pt.pause_completed = 1
                    break
        return

        # TODO Rename this here and in `p`

    def prefs(
        color_strings="",
        color_vars="",
        color_values="",
        color_specialty="",
        print_always=False,
        _line_no=None,
    ):
        if pt.print_prefs == False and print_always != True:
            return
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


        # args_only = re.compile(r'\((.*?)\).*$').search(code).groups()[0]

        # print('pt.prefs('+ C.t2 +args_only+C.er+'): '+
        # ' - (Line :'+str(line_no)+', @'+func_name+', ' +'\\'+file_name+')')

        print(
            f"pt.prefs({C.t2}{args_only}{C.er}): - (Line :{str(line_no)}, {func_name_fmt}{file_name})"
        )

        # try:
        ### Theme Colors (Print tricks color scheme)

        if color_strings != "":
            C.t1 = color_strings  ### Strings
        if color_vars != "":
            C.t2 = color_vars  ### Variables
        if color_values != "":
            C.t3 = color_values  ### Values
        if color_specialty != "":
            C.t4 = color_specialty  ### Specialty (keys, errors etc.)

        string_to_color = "New color preferences successfully set"
        letters_colored = ""
        colors = (C.fr, C.fg, C.fy, C.fb, C.fp, C.fc, C.fw)
        for letter in string_to_color:
            color = ra.choice(colors)
            letters_colored += color + letter
        print(letters_colored)

        # except Exception:
        #     pt.e()
        #     print('New color preferences Failure: Setting some or all colors have failed . Ensure that you are typing in the correct color codes')
        # end def prefs

    def r(
        loops=None,
        seconds=None,
        running_loops=None,
        running_seconds=None,
        reactivate_in_loops=None,
        reactivate_in_seconds=None,
        print_always=False,
        _line_no=None,
    ):
        """release / enable main
        - Allows for any mixes of conditions to be used (seconds + loops) etc

        """
        # ... ###db('inside r()')

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        this_r_key = f"{file_name}_{line_no}_{code}"

        ## Bypass the entire check, if all requirements have been met to perma-unlock this.
        if this_r_key + "_Always_Return_True" in pt.release_enable:
            # pt.c('ART')
            return True

        (
            done_loops,
            done_seconds,
            done_running_loops,
            done_running_seconds,
            done_reactivate_in_loops,
            done_reactivate_in_seconds,
        ) = (True, True, True, True, True, True)

        if this_r_key not in pt.release_enable:
            """RIS = Reactivate in Seconds"""
            pt.release_enable[this_r_key] = {
                "loop_num": 0,
                "seconds_num": time.time(),
                "activated_runs": 0,
                "num_count_ril": 0,
                "sec_count_ris": time.time(),
                "seconds_since_reactivate": time.time(),
                "was_on_now_off": False,
            }

        re_dict = pt.release_enable[this_r_key]

        re_dict["loop_num"] += 1
        loop_num = re_dict["loop_num"]

        seconds_passed = time.time() - re_dict["seconds_num"]
        seconds_since_reactivate = time.time() - re_dict["seconds_since_reactivate"]

        if loops is not None:
            done_loops = True if loop_num >= loops else False
            # ... ###db(f'loop_num: {loop_num}', f'loops: {loops}', f'done_loops: {done_loops}')

        if seconds is not None:
            done_seconds = True if seconds_passed >= seconds else False
            # ... ###db(f'seconds_passed {seconds_passed}, seconds: {seconds}')

        if running_loops is not None:
            # done_running_loops = False if re_dict['activated_runs'] >= running_loops else True
            if re_dict["activated_runs"] < running_loops:
                # re_dict['activated_runs'] = 0 ## Reset this cycle of runs (only used if reactivate_in_loops/seconds is being passed as arg)
                done_running_loops = True
            else:
                done_running_loops = False
                re_dict["was_on_now_off"] = True

        if running_seconds is not None:
            # done_running_seconds = True if seconds_passed < running_seconds else False
            # ... ###db(f'running_seconds: {running_seconds}')

            if seconds_passed < running_seconds:
                done_running_seconds = True
            else:
                done_running_seconds = False
                re_dict["was_on_now_off"] = True
                re_dict["sec_count_ris"] = time.time()

        if reactivate_in_loops is not None:
            if (
                loops is None
                and seconds is None
                and running_loops is None
                and running_seconds is None
            ):
                done_reactivate_in_loops = (
                    True if loop_num % reactivate_in_loops == 0 else False
                )

            elif re_dict["was_on_now_off"] == True:
                re_dict["num_count_ril"] += 1
                if re_dict["num_count_ril"] % reactivate_in_loops == 0:
                    re_dict["loop_num"] = 0
                    re_dict["activated_runs"] = 0
                    re_dict["was_on_now_off"] = False

        if reactivate_in_seconds is not None and (
                        loops is None
                        and seconds is None
                        and running_loops is None
                        and running_seconds is None
                    ):
            if seconds_since_reactivate >= reactivate_in_seconds:
                # ... ###db(1)
                done_reactivate_in_seconds = True
                re_dict[
                    "seconds_since_reactivate"
                ] = (
                    time.time()
                )  # I moved this to the end of the function for more accuracy on time management between runs.
        
            ## if first run, run this as True by default, then disable until number of "reactivate in seconds" has passed
            elif re_dict["loop_num"] == 1:
                done_reactivate_in_seconds = True
        
            else:
                # ... ###db(2)
                done_reactivate_in_seconds = False

        doneList = [
            done_loops,
            done_seconds,
            done_running_loops,
            done_running_seconds,
            done_reactivate_in_loops,
            done_reactivate_in_seconds,
        ]

        ### Checks Bypass:
        ### if everything is None then shortcut to make this run without all the checks.
        if (
            loops is None
            and seconds is None
            and running_loops is None
            and running_seconds is None
            and reactivate_in_loops is None
            and reactivate_in_seconds is None
        ):
            pt.release_enable[this_r_key + "_Always_Return_True"] = 1
            # ... ###db(1)
        ### if everything is None (but disregarding anything pro or con the starting loops and seconds, because they don't matter), then shortcut to make this run without all the checks.)
        elif (
            done_loops == True
            and seconds is None
            and running_loops is None
            and running_seconds is None
            and reactivate_in_loops is None
            and reactivate_in_seconds is None
        ):
            pt.release_enable[this_r_key + "_Always_Return_True"] = 1
            # ... ###db(2)
        elif (
            done_seconds == True
            and loops is None
            and running_loops is None
            and running_seconds is None
            and reactivate_in_loops is None
            and reactivate_in_seconds is None
        ):
            pt.release_enable[this_r_key + "_Always_Return_True"] = 1
            # ... ###db(3)

        ### Final returns to see if this is true/false and therefore if the rest of the user's code can be unlocked.
        # ... ###db(all(doneList))
        if all(doneList):
            ar = re_dict["activated_runs"]
            ar += 1
            re_dict["activated_runs"] = ar

            return True
        else:
            return False
        # end def r

    def r_old2(
        loops=0,
        seconds=0,
        running_loops=0,
        running_seconds=0,
        reactivate_in_loops=0,
        reactivate_in_seconds=0,
        print_always=False,
        _line_no=None,
    ):
        """release / enable main
        - Allows for any mixes of conditions to be used (seconds + loops) etc



        """
        # ... ###db('inside r()')
        seconds_passed = 0.0
        loop_num = 1
        seconds_num = 0

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        this_r_key = f"{file_name}_{line_no}_{code}"

        ## Bypass the entire check, if all requirements have been met to perma-unlock this.
        if this_r_key + "_Always_Return_True" in pt.release_enable:
            # pt.c('ART')
            return True

        # run_until_loop = running_loops + loops -1 ## -1 BECAUSE we are already adding loop_num += 1 before this line.
        run_until_loop = (
            running_loops + loops
        )  ## -1 BECAUSE we are already adding loop_num += 1 before this line.
        run_until_sec = running_seconds + seconds

        ##NOTE ... a hack to get test 4 to work check correctly.. I'm not sure if
        ## there is a better way to do this..? Maybe keep this but ONLY if the other
        ## tests that follow this will work. And they will have to have conditions
        ## for combinations of loops and seconds.
        if loops == 0:
            loop_num = 1
            run_until_loop = 2

        if loops == 1:
            run_until_loop += 1

        ## create dict of all of these, or get their data if already created.
        if this_r_key not in pt.release_enable:
            pt.release_enable[this_r_key] = {"loop_num": 1, "seconds_num": time.time()}
            return False
        else:
            re_dict = pt.release_enable[this_r_key]

            if loops != 0:
                loop_num = re_dict["loop_num"]
                loop_num += 1
                re_dict["loop_num"] = loop_num

            if seconds != 0:
                seconds_num = re_dict["seconds_num"]
                nowTime = time.time()
                seconds_passed = nowTime - seconds_num
                re_dict["seconds_num"] = seconds_num

        if loop_num == 998:
            ... ###db(loops, loop_num, run_until_loop, seconds, seconds_passed, run_until_sec)

        # ... ###db(loops, loop_num, run_until_loop, seconds, seconds_passed, run_until_sec)
        if loop_num >= loops and seconds_passed >= seconds:
            if running_loops == 0 and running_seconds == 0:
                pt.release_enable[this_r_key + "_Always_Return_True"] = ()
                # pt.c('Aa')
                return True
            if loop_num < run_until_loop and seconds_passed <= run_until_sec:
                # pt.c('Bb')
                return True
            # if se
            # else:
            #     pt.c('Ff')
            #     pt.ex()
            #     return False
        # else:
        #     pt.c('z false')

        # ... ###db(loops, loop_num, run_until_loop, seconds, seconds_passed, run_until_sec)
        # time.sleep(.1)##TODO TODO delete this after testing

    def r_old1(
        loops=0,
        seconds=0,
        running_loops=0,
        running_seconds=0,
        reactivate_in_loops=0,
        reactivate_in_seconds=0,
        print_always=False,
        _line_no=None,
    ):
        """release / enable main
        - Allows for any mixes of conditions to be used (seconds + loops) etc

        - Shortcuts test:
            - if str(file_name_line_no_code_'COMPLETED') in dict:
                - This has met the requirements for completely being unlocked, so skip the rest of the checks,
                and just return true.
        - Super fast _simple_trace data:
            (for possibly all pt() and pt.* statements:)
            - Take all passed vars, and append all of them into a string. Check if that string is
            in a dict of pt statements used so far.
            - NOTE: I don't think this willa actally work. The idea of appending a str check with
            "completed" (the above idea) could theoretically work because we are already getting the
            _simple_trace data for line no etc. But this idea is trying to bypass the _simple_trace, and I
            don't know how to do it without my previous ideas of using AST to document the entire
            file or some equivalent like that.

        """
        # ... ###db('inside r()')
        seconds_passed = 0.0
        loop_num = 1
        seconds_num = 0

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        this_r_key = f"{file_name}_{line_no}_{code}"

        ## Bypass the entire check, if all requirements have been met to perma-unlock this.
        if this_r_key + "_Always_Return_True" in pt.release_enable:
            # pt.c('ART')
            return True

        # run_until_loop = running_loops + loops -1 ## -1 BECAUSE we are already adding loop_num += 1 before this line.
        run_until_loop = (
            running_loops + loops
        )  ## -1 BECAUSE we are already adding loop_num += 1 before this line.
        run_until_sec = running_seconds + seconds

        ##NOTE ... a hack to get test 4 to work check correctly.. I'm not sure if
        ## there is a better way to do this..? Maybe keep this but ONLY if the other
        ## tests that follow this will work. And they will have to have conditions
        ## for combinations of loops and seconds.
        if loops == 0:
            loop_num = 1
            run_until_loop = 2

        if loops == 1:
            run_until_loop += 1

        # if run_until_loop < 0:
        #     run_until_loop = 0
        # if run_until_sec < 0:
        #     run_until_sec = 0

        ## create dict of all of these, or get their data if already created.
        if this_r_key not in pt.release_enable:
            pt.release_enable[this_r_key] = {"loop_num": 1, "seconds_num": time.time()}
            return False
        else:
            re_dict = pt.release_enable[this_r_key]

            # if re_dict['loops_2_activate'] is not None:
            if loops != 0:
                loop_num = re_dict["loop_num"]
                loop_num += 1
                re_dict["loop_num"] = loop_num

            # if re_dict['seconds_2_activate'] is not None:
            if seconds != 0:
                seconds_num = re_dict["seconds_num"]
                nowTime = time.time()
                seconds_passed = nowTime - seconds_num
                # seconds_num = time.time()
                re_dict["seconds_num"] = seconds_num

        ... ###db(loops, loop_num, run_until_loop, seconds, seconds_passed, run_until_sec)
        if loop_num >= loops and seconds_passed >= seconds:
            if running_loops == 0 and running_seconds == 0:
                pt.release_enable[this_r_key + "_Always_Return_True"] = ()
                # pt.c('Aa')
                return True
            if loop_num < run_until_loop and seconds_passed <= run_until_sec:
                # pt.c('Bb')
                return True
            # if se
            # else:
            #     pt.c('Ff')
            #     pt.ex()
            #     return False
        # else:
        #     pt.c('z false')

        # ... ###db(loops, loop_num, run_until_loop, seconds, seconds_passed, run_until_sec)
        # time.sleep(.1)##TODO TODO delete this after testing

        ...
    
    def after(loops=None, seconds=None, id=None, print_this=False, debug_this=False):
        '''TODO: 
            - Add print_this check and do a print when its unlocked
            - add a debug_this check and that will do a print on 
            every check (so you can see the values), and when its
            unlocked.
            - add ID check (to change which loop/seconds we are tracking), 
            however, this might be unecessary in revised print tricks because
            we are using instatiated classes....?
            '''
        if loops:
            pt.after_count += 1
            if pt.after_count >= loops:
                
                if not seconds:
                    return True
            else:
                return False
        
        if seconds:
            if time.time() - pt.after_seconds_start >= seconds:
                return True
            else:
                return False

    def every(loops=None, seconds=None, id=None, print_this=False, debug_this=False):
        '''
            Can pass an int (loops), or seconds, or both.
            - If pass both, then both must be true to proceed. 
        
        TODO
            - Add print_this check and do a print when its unlocked
            - add a debug_this check and that will do a print on 
            every check (so you can see the values), and when its
            unlocked.
            - add ID check (to change which loop/seconds we are tracking), 
            however, this might be unecessary in revised print tricks because
            we are using instatiated classes....?
        '''
        if loops:
            pt.every_count += 1
            
            if pt.every_count >= loops:
                pt.every_count = 0
                
                if not seconds:
                    return True
            else:
                return False
            
        if seconds:
            if time.time() - pt.every_seconds_start >= seconds:
                pt.every_seconds_start = time.time()
                return True
            else:
                return False



    def rc(
        cpu="i5_5500",
        cores="3",
        cpu_power="50%",
        gpu="gtx_1060",
        gpu_power="99%",
        ram_amount="10gb",
        ram_speed="3200mhz",
    ):
        """Resource Control aka Simulate Hardware. Allows you to control the resources
        that your code has access to, in order to simulate various environments, or just ensure
        that the app is taking the amount of resources specified

        How to:
        - Calculates current power of current PC.
        - Calculates power of hardware you want to use instead.
        - Uses the pt.slow_mo function to control the speed of the app
            and slow down the hardware parameters (cpu/graphics processes)

        """

    def search_file(file_name, start_dir, stop_event, result_queue):
        ... ###db(file_name)
        ... ###db(start_dir)
        # ... ###db.ex()
        # while not stop_event.is_set():
        while UTI.interupt_thread is False:
            for root, dirs, files in os.walk(start_dir):
                # if ... ###db.r(loops=10):
                #     ... ###db.p()
                if stop_event.is_set():
                    break

                ## Ignore non-user Python directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'dist', 'build', '.eggs', 'Program Files (x86)']]

                print(f"Searching in directory: {root}")  # Print current directory
                # ... ###db(files)
                for file in files:
                    if file == file_name:
                        # ... ###db(file)
                        # ... ###db.ex()
                        file_path = os.path.join(root, file)
                        print(f"File found at: {file_path}")
                        # stop_event.set()
                        # result_queue.put(file_path)
                        return file_path
                # If the file is not found in the current directory and its subdirectories, move up one level
                parent_dir = os.path.dirname(start_dir)
                if parent_dir == start_dir:  # If we reached the root directory, stop searching
                    break
                # start_dir = parent_dir
                # ... ###db.ex()

        stop_event.set()  # Set the stop_event before printing "File not found"
        print("File not found")
        return

    def input_thread(stop_event):
        while not stop_event.is_set():
            ... ###db('input thread')
            input("Press ENTER key to stop the search...")
            stop_event.set()
            # UTI.interupt_thread = True
        # else:
        #     return

    def print_threaded_msg(stop_event):
        while not stop_event.is_set():
        # while UTI.interupt_thread is False:
            time.sleep(1)
            print("It's been 1 seconds")
        return

    def profile_time():
        '''
            AKA, "pt.profiler" that I've written about elsewhere. 
            
            - It's meant to profile your entire app (I think) so you can see where the time is spent,
            so similar to, but I think a bit different than both pt.t() and pt.timeall() 
            
        '''
        
        pass
    def profile_resources(
        num_instances = 1,         
        str_front=None,
        str_back="",
        print_this=True,
        print_always=False):
        
        import psutil, GPUtil

        if (
            print_this is False
            or pt.print_pt_statements is False
            and print_always is False
        ):
            return
        
        my_string, filler = UTI._custom_str(str_front)
        
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no
        
        process = psutil.Process()
        memory_info = process.memory_info()
        total_system_memory = psutil.virtual_memory().total
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # print_str += f"{C.t3}{var_as_str}{C.er} - {var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt}{file_name}) - {str_back}"

        print(  
                f"\n{NAM.inst_nam}.profile_resources({formatted_args}): "
                f"(Line :{line_no}, {func_name_fmt}{file_name})\n"
                
                ## Memory / Ram
                f"   - Memory:"
                f"\n      {memory_info.rss / (1024 * 1024):,.2f} MB / "
                f"{total_system_memory / (1024 * 1024 * 1024):,.2f} GB = "
                f"{memory_info.rss / total_system_memory * 100:,.2f}% of Total system memory "
                f"({memory_info.rss / num_instances:,.0f} bytes per instance of {num_instances:,} instance)"
                
                ## CPU
                f"\n   - CPU:"
                f"\n      {cpu_percent} %")

        ## GPU 
        gpus = GPUtil.getGPUs()
        if gpus:
            for gpu in gpus:
                print(  f"   - GPU:"
                        f"\n      {gpu.id=}: {gpu.name}"
                        f"\n      Load: {gpu.load*100:.1f} % "
                        f"\n      GPU Memory: {gpu.memoryUsed:,.0f} MB / {gpu.memoryTotal:,.0f} MB ({gpu.memoryFree:,.0f} MB free)"
                )

        else:
            print("No GPU found.")
    
    def run(file_to_run: str) -> None:
        
        """
        Explanation:
            - A utility class for executing Python scripts with added features like file searching and success/failure reporting.
            - Uses `subprocess.run()` to execute scripts and handles cases where the file isn't found by searching parent directories.
            - Provides feedback on whether the run was successful and manages threads for user input during execution.
            
        """
        
        
        successful_run = False
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        
        start_dir = os.path.split(file_path)[0]
        full_file_path = f'{start_dir}\\{file_to_run}'
        file_name_only = os.path.basename(file_to_run)
        ... ###db(file_to_run, start_dir, full_file_path, file_name_only)
        # ... ###db.ex()
        if os.path.isfile(file_to_run):
            # subprocess.run(["python", file_to_run]) ## old, deprecated usage for my circumstances. Testing with suprocess.popopen instead
            subprocess.Popen([sys.executable, file_to_run, '--subprocess'])
        elif os.path.isfile(full_file_path):
            # subprocess.run(["python", full_file_path]) ## old, deprecated usage for my purposes now. Testing with subprocess.popopen instead. 
            subprocess.Popen([sys.executable, full_file_path, '--subprocess'])
            successful_run = True
        else:
            stop_event = threading.Event()
            result_queue = queue.Queue()
            # search_thread = threading.Thread(target=pt.search_file, args=(file_name_only, start_dir, stop_event, result_queue))
            input_thread = threading.Thread(target=pt.input_thread, args=(stop_event,))
            # message_thread = threading.Thread(target=pt.print_threaded_msg, args=(stop_event,))
            
            ... ###db(1)
            input_thread.start()
            # message_thread.start()
            file_path = pt.search_file(file_name_only, start_dir, stop_event, result_queue)
            stop_event.set()
            ... ###db(2)
            # message_thread.join()
            ... ###db(2.5)
            input_thread.join()
            ... ###db(2.8)
            # search_thread.join()
            
            ... ###db(3)
            # file_path = result_queue.get()
            ... ###db(file_path)
            ... ###db.ex()
            if file_path:
                successful_run = True
                
        if successful_run is True:
            print(f"pt.run({formatted_args}) - {C.t2}Successful run: {C.t3}{full_file_path}{C.er} - (Line :{str(line_no)}, {func_name_fmt}{file_name})")
        else:
            print(f"pt.run({formatted_args}) - {C.t2}File not found: {C.t3}{full_file_path}{C.er} - (Line :{str(line_no)}, {func_name_fmt}{file_name})")
        
        # UTI.interupt_thread = False
        ... ###db.ex()
    def s(_line_no=None):
        pt.h("main")
        gg = pt.hr(pt.slowMo)
        return

    def size(varObject, print_sources=False, print_sources_count=False, _line_no=None):
        """
        - Currently broken:
            - Does not seem to work with ints, strings etc (reports same size for vastly different lengths)
            - Goes incredibly slow (and likely inaccurate) when using some objects (like ursina entity)
            - Reports wrong sizes, sometimes (or more often) reporting the entire size of the entire python app, 
            not just the object you are trying to check. 
            
            
            
        - Pulls fom _bytes_size_formatter to get the return of  pt._bytes_size in a nice format, based on size,
        - Then colors the results!
        """
        
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        this_bytes, sources, sources_count = UTI._bytes_size(varObject, print_sources, print_sources_count, manually_called=True)
        formatted_bytes_size = UTI._bytes_size_formatter(this_bytes, args_only, print_sources, print_sources_count, sources, sources_count)
        print(formatted_bytes_size[1])
        # end def size

    # from collections.abc import Mapping, Container
    # from sys import getsizeof
    # def deep_getsizeof(o, ids):
    #     """Find the memory footprint of a Python object
    # This is a recursive function that drills down a Python object graph
    # like a dictionary holding nested dictionaries with lists of lists
    # and tuples and sets.
    # The sys.getsizeof function does a shallow size of only. It counts each
    # object inside a container as pointer only regardless of how big it
    # really is.
    # :param o: the object
    # :param ids:
    # :return:
    # """
    #     d = deep_getsizeof
    #     if id(o) in ids:
    #         return 0
    #     r = getsizeof(o)
    #     ids.add(id(o))
    #     if isinstance(o, str) or isinstance(0, str):
    #         return r
    #     if isinstance(o, Mapping):
    #         return r + sum(d(k, ids) + d(v, ids) for k, v in o.iteritems())
    #     if isinstance(o, Container):
    #         return r + sum(d(x, ids) for x in o)
    #     return r 
    def get_pos(num, unit, _line_no=None):
        return int(abs(num) / unit) % 10

    def timeall(
        func,
        ideal_loops=500,  ## Your desired amount of loops (but will be adjusted based on estimated running time)
        exact_loops=None,  ## If set, this function will run 500 times, regardless of the dynamic function settings.
        number=None,  ## Alias for "exact_loops"
        test_time=1.0,  ## Desired test time in seconds
        user_scale="",  ## User desired time to display
        disable_all_printing=False,  ## Turns off all python printing (best for measuring true performance)
        disable_pt_prints=False,  ## Just turn off 'pt()' statements. Python prints will still work.
        disable_loops_printing=True,  ## True by default. You can turn this to false if you want to see each individual run.
        str_front=None,
        str_back="",
        print_this=True,  ## Disables pt.timeall() from printing the results (but the results still return for you)
        print_always=False,
        *args,
        **kwargs,
    ):
        """
        - Note: pt.t() is used within pt.timeall() and accounts for its own run time,
        so it's very precise, at less than a millionth of a second, just like time.perf_counter().
        - It's recommended to use 'disable_all_printing=True' when timing the performance
        of your code to ensure that python's print statements and print_tricks printing aren't
        slowing down your code.
        - It's recommended to keep "disable_loops_printing=True". But.. if you want to see
        the performance of each loop, one after the other, you can turn this on.
        """

        print_pt_t = not disable_loops_printing
        if disable_all_printing:
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")
        if disable_pt_prints is True:
            pt.disable("pt", print_this=True)

        ### SETTING NUM LOOPS.
        loops = ideal_loops
        estimated_time = 0.0
        use_exact_loops = False

        ### ESTIMATING TIME TO COMPLETE
        pt.t_infinite(f"TIMING_TEST - {func.__name__}", print_this=False)
        result = func(*args, **kwargs)
        one_loop_time = pt.t_infinite(f"TIMING_TEST - {func.__name__}", print_this=False)
        est_loops_in_test_time_seconds = int(test_time / one_loop_time)
        estimated_time = loops * one_loop_time
        ... ###db(estimated_time)

        ### SETTING Loops to max exact_loops or number (if passed)
        if exact_loops is not None or number is not None:
            use_exact_loops = True
            if isinstance(exact_loops, (int, float)) and isinstance(
                number, (int, float)
            ):
                loops = max(exact_loops, number)
            elif isinstance(exact_loops, (int, float)):
                loops = exact_loops
            elif isinstance(number, (int, float)):
                loops = number

        else:  ## SETTING DYNAMIC LOOPS
            ## Setting the smaller/faster of ideal_loops or estimated loops in desired test_time
            loops = (
                ideal_loops
                if ideal_loops < est_loops_in_test_time_seconds
                else est_loops_in_test_time_seconds
            )
            ## Setting minimum loops to 7
            loops = 7 if loops < 7 else loops

        ### PT.T() RECORDING ITERATIONS
        visual_progress_bar = True if estimated_time > 2.0 else False
        loading_bar_mark = loops // 7
        half_loading_bar = loops // 2
        ... ###db(loops, loading_bar_mark, half_loading_bar)
        # ... ###db.t('actual time', print_this=False)
        print(f"Running Loops: ", end="")
        for i in range(
            loops
        ):  ## -1 to account for the final pt.t(sum=True) to show the total time.
            pt.t_infinite(func.__name__, print_this=print_pt_t, _line_no="timeall")
            result = func(*args, **kwargs)
            if visual_progress_bar:
                if i % half_loading_bar == 0:
                    pt.c(f"{i/loops*100:g}% ", end="", flush=True)
                if i % loading_bar_mark == 0:
                    print(f"\u2588", end="", flush=True)
        pt.c("100%")
        # ... ###db.t('actual time')

        ### CLEANUP
        if disable_all_printing:
            sys.stdout.close()
            sys.stdout = original_stdout

        ### PRINTING
        if print_this == True:
            (
                file_name,
                file_path,
                line_no,
                func_name,
                func_name_fmt,
                code,
                args_with_specials,
                args_only,
                formatted_args,
                fmt_args_list,
            ) = UTI._simple_trace()
            line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

            my_string, filler = UTI._custom_str(str_front)
            pbi = (
                C.Fore_PURPLE + C.Effect_BOLD + C.Effect_ITALICS
            )  ## sdf = seconds_display_format

            magnitude_ns, length, seq_orig_num = pt.t_infinite(
                func.__name__, sum=True, get_timeall_data=True, print_this=print_pt_t
            )
            (
                magnitude_ns_str,
                magnitude_specific_str,
                specific_format,
                magnitude_user_formatted_str,
            ) = UTI._get_relative_magnitude_ns_and_format(
                magnitude_ns, user_scale, pbi
            )
            
            avg_run = magnitude_ns / loops
            
            (
                avg_seconds_str,
                avg_specific_str,
                avg_specific_format,
                avg_user_formatted_str,
            ) = UTI._get_relative_magnitude_ns_and_format(avg_run, user_scale, pbi)
            print(
                f"{C.t1}{my_string}{C.er}{filler}pt.timeall({formatted_args}): "
                f"{pbi}{magnitude_ns_str}{C.t1} s{C.er} / "
                f"{pbi}{magnitude_specific_str}{C.t1} {specific_format}{C.er} "
                f"{magnitude_user_formatted_str}({0 if magnitude_ns == 0 else 1/(magnitude_ns/1_000_000_000):,.1f} FPS): "
                f"Time between {C.t2}{func.__name__} {C.t1}#{seq_orig_num}{C.er} & {C.t2}{func.__name__} {C.t1}#{length}{C.er} "
                f"(Line :{line_no}, {func_name_fmt}{file_name})"
                f"\n\t > Average per run: "
                f"{pbi}{avg_seconds_str}{C.t1} s{C.er} / "
                f"{pbi}{avg_specific_str}{C.t1} {avg_specific_format}{C.er} "
                f"{avg_user_formatted_str}({0 if avg_run == 0 else 1/(avg_run/1_000_000_000):,.1f} FPS) "                # f'(Line :{line_no}, {func_name_fmt}{file_name})'
            )
        pt.enable("pt", print_this=False)
        return result, magnitude_ns
        # end def timeall

    def timeall_versus(
        functions,
        loops=500,
        user_scale="",
        disable_all_printing=False,
        disable_pt_prints=False,
        disable_loops_printing=True,
        str_front=None,
        str_back="",
        print_this=True,
        print_always=False,
        *args,
        **kwargs,
    ):
        """
        - Note: pt.t() is used within pt.timeall() and accounts for its own run time,
        so it's very precise, at less than a millionth of a second, just like time.perf_counter().
        - It's recommended to use 'disable_all_printing=True' when timing the performance
        of your code to ensure that python's print statements and print_tricks printing aren't
        slowing down your code.
        - It's recommended to keep "disable_loops_printing=True", but if you want to see
        the performance of each loop, one after the other, you can turn this on.
        """

        """
        - We accept *funcs_and_args as first param.
        - You can either:
            A - pass a singular func and all of it's args, one after the other with comma's,
                - Then you say the first element is the function and the rest of the elements are the *args to pass into the func()
            B - pass a single list with the first element being your function, and the proceeding ones being your args. 
            C -  you can pass two or more lists, with the lists being separated by commas. And in each list will be commas separated
            values, Starting item is the function, further ones are its arguments. 
        - We then check to see what was passed and how it was passed:
            - if *funcs_and_args is more than one element, and first element is a list: Multi-function 
            - if *f is one element, and that is a list: One function with args, that user passed as a list .
            - if *f first element is a function, then it's a single function + args. 
            - if *f first elemement is not a function or not a list (with a function as first element in that list):
                - return error message.  
        - 
        """
        # ... ###db(functions)
        # pt.ex()

        len_functions = len(functions)
        # if len_functions > 1:
        # for function in fu

        print_pt_t = not disable_loops_printing
        if disable_all_printing:
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")
        if disable_pt_prints is True:
            pt.disable("pt", print_this=True)

        # func_name = func.__name__
        for i in range(
            loops - 1
        ):  ## -1 to account for the final pt.t(sum=True) to show the total time.
            for count, func in enumerate(functions):
                pt.t_infinite(func.__name__, print_this=print_pt_t)
                result = func(*args, **kwargs)

        if disable_all_printing:
            sys.stdout.close()
            sys.stdout = original_stdout

        if print_this == True:
            (
                file_name,
                file_path,
                line_no,
                func_name,
                func_name_fmt,
                code,
                args_with_specials,
                args_only,
                formatted_args,
                fmt_args_list,
            ) = UTI._simple_trace()
            line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

            my_string, filler = UTI._custom_str(str_front)
            pbi = (
                C.Fore_PURPLE + C.Effect_BOLD + C.Effect_ITALICS
            )  ## sdf = seconds_display_format

            # if len(functions) > 1:
            for count, func in enumerate(functions):
                magnitude_ns, length, seq_orig_num = pt.t_infinite(
                    func.__name__, sum=True, get_timeall_data=True, print_this=print_pt_t
                )
                (
                    magnitude_ns_str,
                    magnitude_specific_str,
                    specific_format,
                    magnitude_user_formatted_str,
                ) = UTI._get_relative_magnitude_ns_and_format(
                    magnitude_ns, user_scale, pbi
                )

                avg_run = magnitude_ns / loops
                (
                    avg_seconds_str,
                    avg_specific_str,
                    avg_specific_format,
                    avg_user_formatted_str,
                ) = UTI._get_relative_magnitude_ns_and_format(
                    avg_run, user_scale, pbi
                )
                print(
                    f"{C.t1}{my_string}{C.er}{filler}pt.timeall({formatted_args}): "
                    f"{pbi}{magnitude_ns_str}{C.t1} s{C.er} / "
                    f"{pbi}{magnitude_specific_str}{C.t1} {specific_format}{C.er} "
                    f"{magnitude_user_formatted_str}({1/magnitude_ns:,.2f} FPS): "
                    f"Time between {C.t2}{func.__name__} {C.t1}#{seq_orig_num}{C.er} & {C.t2}{func.__name__} {C.t1}#{length}{C.er} "
                    f"(Line :{line_no}, {func_name_fmt}{file_name})"
                    f"\n\t > Average per run: "
                    f"{pbi}{avg_seconds_str}{C.t1} s{C.er} / "
                    f"{pbi}{avg_specific_str}{C.t1} {avg_specific_format}{C.er} "
                    f"{avg_user_formatted_str}({1/avg_run:,.2f} FPS) "
                    # f'(Line :{line_no}, {func_name_fmt}{file_name})'
                )
        pt.enable("pt", print_this=False)
        return result, magnitude_ns
        # end def timeall_versus
    def t(
        *sequences,
        user_scale="",
        sum=False,
        str_front=None,
        str_back="",
        get_timeall_data=False,
        print_always=False,
        print_this=True,
        garbage_collector=True,
        _line_no=None,
    ):
        """
        A simplified version of pt.t() where we only track between the first and second instance that pops up.
        This is very helpful for a loop, where the time within the loop needs to be tracked, but the time outside
        of the loop can be disregarded. The timer resets every 2 calls, always measuring pairs.
        """

        timeNow = time.perf_counter_ns()

        if pt.print_timers == False and print_always != True:
            return
        ## optionally turn off garbage collection for this pt statement, and only until the next pt statement (cannot stay off)
        ## for multiple pt.t statements in a row unless I end up scanning the whole file for pt.t() statements with the same sequence.)
        ## before setting to false, record it's current state that the user set before we got here and then return to that off/on state after we finish.
        if garbage_collector == False:
            pt.orig_garb_collect_state = gc.isenabled()
            # ... ###db(1, pt.orig_garb_collect_state, gc.isenabled())
            gc.disable()
            # ... ###db(2, pt.orig_garb_collect_state, gc.isenabled())

        my_string, filler = UTI._custom_str(str_front)
        pbi = (
            C.Fore_PURPLE + C.Effect_BOLD + C.Effect_ITALICS
        )  ## sdf = seconds_display_format

        user_scale = str(user_scale).lower()

        ## if sequences is blank tuple, set it to a list of one item, making the default sequence 'pt.t()'
        if sequences == ():
            sequences = (f"{NAM.inst_nam}.t()",)
        len_sequences = len(sequences)

        magnitude_ns = 0.0
        for sequence in sequences:
            sequence = str(sequence)

            ##### Check if we need to reset the sequence (when we have 2 entries, reset for next pair)
            if sequence in pt.sequences_dict and len(pt.sequences_dict[sequence]) >= 2:
                # Update counter before resetting
                if sequence not in pt.sequence_counters:
                    pt.sequence_counters[sequence] = 2  # Start at 2 since we're about to reset after pair 0,1
                else:
                    pt.sequence_counters[sequence] += 2
                # Reset the sequence completely to start a new pair
                del pt.sequences_dict[sequence]

            ##### If this key (sequence) hasn't existed yet for this program running, create the key and assign it
            if sequence not in pt.sequences_dict:
                (
                    file_name,
                    file_path,
                    line_no,
                    func_name,
                    func_name_fmt,
                    code,
                    args_with_specials,
                    args_only,
                    formatted_args,
                    fmt_args_list,
                ) = UTI._simple_trace()
                line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

                if _line_no is not None:
                    pt.line_no_dict[_line_no] = [
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ]

                if len_sequences == 1:
                    if print_this == True:
                        print(
                            f"{C.t1}{my_string}{C.er}{filler}{NAM.inst_nam}.t({formatted_args}): "
                            f"{C.t2}Timer Started{C.er} "
                            f"(Line :{line_no}, {func_name_fmt}{file_name})"
                            f"- {C.t1}{str_back}{C.er}"
                        )
                else:
                    if print_this == True:
                        print(
                            f"{C.t1}{my_string}{C.er}{filler}{NAM.inst_nam}.t({formatted_args}): "
                            f'{C.t1}"{sequence}"{C.t2} Timer Started{C.er} '
                            f"(Line :{line_no}, {func_name_fmt}{file_name})"
                            f"- {C.t1}{str_back}{C.er}"
                        )

                original_statement_line_no = line_no

                pt.sequence_args_dict[sequence] = [
                    user_scale,
                    str_front,
                    str_back,
                    print_always,
                    original_statement_line_no,
                ]

                ## Start tracking the time, ignoring the time taken above, on all previous lines!!!
                ## Records the perf_counter time and the time since the last call on this sequence (magnitude_ns)
                ##                       ## [[current time    , Time since last call, time of this function]]
                pt.sequences_dict[sequence] = [[time.perf_counter_ns(), 0.0, 0.0]]

                return None
            else:
                # This is the second call in the pair - calculate and display timing
                ## Check to see if they specified arguments on the secondary/tertiary pt.t() statements. If so, send a message that this is not allowed, and to pass all arguments
                ## to the originating statement.
                if _line_no is not None:
                    (
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ) = pt.line_no_dict.get(_line_no)
                else:
                    (
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ) = UTI._simple_trace()
                    line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

                if (
                    user_scale != ""
                    or str_front is not None
                    or str_back != ""
                    or print_always is not False
                ):
                    pt.c(
                        f"{C.t2}<<<Error>>: {C.er}You cannot pass arguments on line {line_no}: {NAM.inst_nam}.t({C.t2}{formatted_args}) ({func_name_fmt}{file_name}). \n"
                        f"    <<<Please specify all of your arguments on the first instance of this \n"
                        f"    <<<{NAM.inst_nam}.t({C.t2}'{sequence}'{C.er}) statement on line {pt.sequence_args_dict[sequence][4]}. "
                    )

                ## recover the arguments from the first instance of this pt.t(), so that we don't have match it at the end.
                user_scale = pt.sequence_args_dict.get(sequence)[0]
                str_front = pt.sequence_args_dict.get(sequence)[1]
                str_back = pt.sequence_args_dict.get(sequence)[2]
                print_always = pt.sequence_args_dict.get(sequence)[3]

                ### - Accounting for the extra pt.t() processing time.
                ### - I basically see how long it takes to process a dictionary lookup a few times because all of my time is accounted for using my code except for dictionary lookups (x2) and a function call and function return.
                del_start = time.perf_counter_ns()
                time_taken_last_function = pt.sequences_dict.get(sequence)[-1][2]
                startTime = pt.sequences_dict.get(sequence)[-1][0]
                # ... ###db(UTI.accumulated_print_tricks_time)
                
                delTime = (time.perf_counter_ns() - del_start) * pt.FUNC_AND_DICT_NUM
                # delTime = 0
                
                # delTime2 = ((time.perf_counter_ns() - del_start) * pt.FUNC_AND_DICT_NUM * (len(UTI.startup_print_tricks_times)+1))
                # ... ###db(delTime, delTime2, delTime2-delTime, len(UTI.startup_print_tricks_times))

                # seconds = timeNow - startTime - time_taken_last_function - delTime - UTI.accumulated_print_tricks_time
                seconds = abs(
                    timeNow
                    - startTime
                    - time_taken_last_function
                    - delTime
                    - UTI.accumulated_print_tricks_time
                )
                UTI.accumulated_print_tricks_time = 0.0

                ## If sum, we need to print out both the last call to this, as well as
                ##   the total (sum) time, to this point, so we add the last recorded seconds
                ##   to the mag_last_n_total_seconds list, then append the final sum amount as well.
                ##   Now that we have the list, we can print each of the two lines in order.
                ##   if sum is False, we iterate the list of 1 item (seconds).
                mag_last_n_total_seconds = [seconds]
                if (
                    sum == True
                ):  ## KEEP this as == and not "sum is True" or I can't do shortcuts like 'pt.t(sum=1)'
                    tot_time = 0.0
                    for i in range(len(pt.sequences_dict.get(sequence))):
                        tot_time += pt.sequences_dict.get(sequence)[i][1]
                    tot_seconds = tot_time + seconds
                    mag_last_n_total_seconds.append(tot_seconds)
                    
                for i, magnitude_ns in enumerate(mag_last_n_total_seconds):
                    (
                        magnitude_seconds_str,
                        magnitude_specific_str,
                        specific_format,
                        magnitude_user_formatted_str,
                    ) = UTI._get_relative_magnitude_ns_and_format(
                        magnitude_ns, user_scale, pbi
                    )

                    # Always show as #0 & #1 since we reset every pair
                    counter_base = pt.sequence_counters.get(sequence, 0)
                    seq_num = counter_base
                    length = counter_base + 1

                    first_line_str = (
                        f"{C.t1}{my_string}{C.er}{filler}{NAM.inst_nam}.t({formatted_args}): "
                    )
                    if sum and i == 1:
                        seq_orig_num = "0"
                        first_line_str = (
                            f"{C.t1}{my_string}{C.er}{filler}      >>> sum = "
                        )

                    if print_this == True:
                        print(
                            f"{first_line_str}"
                            f"{pbi}{magnitude_seconds_str}{C.t1} s{C.er} / "
                            f"{pbi}{magnitude_specific_str}{C.t1} {specific_format}{C.er} "
                            f"{magnitude_user_formatted_str}({0 if magnitude_ns == 0 else 1/(magnitude_ns/1_000_000_000):,.1f} FPS): "
                            f"Time between {C.t2}{sequence} {C.t1}#{seq_num}{C.er} & {C.t2}{sequence} {C.t1}#{length}{C.er} "
                            f"(Line :{line_no}, {func_name_fmt}{file_name})"
                        )

                    ### return to previous garbage collection state, regardless of what we did in this function.
                    if pt.orig_garb_collect_state:
                        gc.enable()
                        pt.orig_garb_collect_state = gc.isenabled()
                    # ... ###db(4, pt.orig_garb_collect_state, gc.isenabled())

            ### returns the value in seconds of any key, either in the keys yet to be created, or the ones that are already established.
            ## Prep data for sending to the timeall function(if there is a timeall calling this)
            pt.sequences_dict[sequence].append(
                [timeNow, magnitude_ns, time.perf_counter_ns() - timeNow]
            )
        return_multi = [
            pt.sequences_dict.get(str(key))[-1][1] for key in sequences
        ]  # I have to convert the key to a string so that I can account for integers. Example 'pt.t(5)' will save as a string, but not count for one here unless I convert it to one.
        if get_timeall_data:
            return magnitude_ns, length, seq_orig_num
        if len_sequences == 1:
            return magnitude_ns
        else:
            return return_multi        
        
    def t_infinite(
        *sequences,
        user_scale="",
        sum=False,
        str_front=None,
        str_back="",
        get_timeall_data=False,
        print_always=False,
        print_this=True,
        garbage_collector=True,
        _line_no=None,
    ):
        """timer:
        - for counting time anywhere and between anything in your code.
        - print the time between any number of statements with the same name. This is the "Infinite" part of this. 
        - So unlike pt.t() that just records the time between two statements only, this records total time amount any number
        of statements. 
        - Matching statements can isolate their time from the others. (for example: pt.t_infinite(1) and pt.t_infinite(2) and pt.t_infinite('test') will all
            track different times).
        - Will work for you very easily if you need extremely easy, very accurate timing. But it's limited to accuracy to
            within about 1 millionth of a second (1 microsecond). 
        """
        timeNow = time.perf_counter_ns()

        if pt.print_timers == False and print_always != True:
            return
        # ... ###db('a')
        # if 'gc=False' or 'gc = False' in kwargs:
        #     ... ###db('b')
        #     garbage_collector = False

        ## optionally turn off garbage collection for this pt statement, and only until the next pt statement (cannot stay off)
        ## for multiple pt.t statements in a row unless I end up scanning the whole file for pt.t_infinite() statements with the same sequence.)
        ## before setting to false, record it's current state that the user set before we got here and then return to that off/on state after we finish.
        if garbage_collector == False:
            pt.orig_garb_collect_state = gc.isenabled()
            # ... ###db(1, pt.orig_garb_collect_state, gc.isenabled())
            gc.disable()
            # ... ###db(2, pt.orig_garb_collect_state, gc.isenabled())

        my_string, filler = UTI._custom_str(str_front)
        pbi = (
            C.Fore_PURPLE + C.Effect_BOLD + C.Effect_ITALICS
        )  ## sdf = seconds_display_format

        user_scale = str(user_scale).lower()

        ## if sequences is blank tuple, set it to a list of one item, making the default sequence 'pt.t()'
        if sequences == ():
            sequences = (f"{NAM.inst_nam}.t_infinite()",)
        len_sequences = len(sequences)

        magnitude_ns = 0.0
        for sequence in sequences:
            sequence = str(sequence)

            ##### If this key (sequence) hasn't existed yet for this program running, create the key and assign it
            if sequence not in pt.sequences_dict:
                (
                    file_name,
                    file_path,
                    line_no,
                    func_name,
                    func_name_fmt,
                    code,
                    args_with_specials,
                    args_only,
                    formatted_args,
                    fmt_args_list,
                ) = UTI._simple_trace()
                line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

                if _line_no is not None:
                    pt.line_no_dict[_line_no] = [
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ]

                if len_sequences == 1:
                    if print_this == True:
                        print(
                            f"{C.t1}{my_string}{C.er}{filler}{NAM.inst_nam}.t_infinite({formatted_args}): "
                            f"{C.t2}Timer Started{C.er} "
                            f"(Line :{line_no}, {func_name_fmt}{file_name})"
                            f"- {C.t1}{str_back}{C.er}"
                        )
                else:
                    if print_this == True:
                        print(
                            f"{C.t1}{my_string}{C.er}{filler}{NAM.inst_nam}.t_infinite({formatted_args}): "
                            f'{C.t1}"{sequence}"{C.t2} Timer Started{C.er} '
                            f"(Line :{line_no}, {func_name_fmt}{file_name})"
                            f"- {C.t1}{str_back}{C.er}"
                        )

                original_statement_line_no = line_no

                pt.sequence_args_dict[sequence] = [
                    user_scale,
                    str_front,
                    str_back,
                    print_always,
                    original_statement_line_no,
                ]

                ## Start tracking the time, ignoring the time taken above, on all previous lines!!!
                ## Records the perf_counter time and the time since the last call on this sequence (magnitude_ns)
                ##                       ## [[current time    , Time since last call, time of this function]]
                pt.sequences_dict[sequence] = [[time.perf_counter_ns(), 0.0, 0.0]]

                return None
            else:
                # if len(pt.sequences_dict[sequence]) >= 2:
                #     pt.sequences_dict[sequence].pop(0)
                ## Check to see if they specified arguments on the secondary/tertiary pt.t_infinite() statements. If so, send a message that this is not allowed, and to pass all arguments
                ## to the originating statement.
                if _line_no is not None:
                    (
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ) = pt.line_no_dict.get(_line_no)
                else:
                    (
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ) = UTI._simple_trace()
                    line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


                if (
                    user_scale != ""
                    or str_front is not None
                    or str_back != ""
                    or print_always is not False
                ):
                    pt.c(
                        f"{C.t2}<<<Error>>: {C.er}You cannot pass arguments on line {line_no}: {NAM.inst_nam}.t_infinite({C.t2}{formatted_args}) ({func_name_fmt}{file_name}). \n"
                        f"    <<<Please specify all of your arguments on the first instance of this \n"
                        f"    <<<{NAM.inst_nam}.t({C.t2}'{sequence}'{C.er}) statement on line {pt.sequence_args_dict[sequence][4]}. "
                    )

                ## recover the arguments from the first instance of this pt.t_infinite(), so that we don't have match it at the end.
                user_scale = pt.sequence_args_dict.get(sequence)[0]
                str_front = pt.sequence_args_dict.get(sequence)[1]
                str_back = pt.sequence_args_dict.get(sequence)[2]
                print_always = pt.sequence_args_dict.get(sequence)[3]

                ### - Accounting for the extra pt.t_infinite() processing time.
                ### - I basically see how long it takes to process a dictionary lookup a few times because all of my time is accounted for using my code except for dictionary lookups (x2) and a function call and function return.
                del_start = time.perf_counter_ns()
                time_taken_last_function = pt.sequences_dict.get(sequence)[-1][2]
                startTime = pt.sequences_dict.get(sequence)[-1][0]
                # ... ###db(UTI.accumulated_print_tricks_time)
                
                
                delTime = (time.perf_counter_ns() - del_start) * pt.FUNC_AND_DICT_NUM
                # delTime = 0
                
                
                # delTime2 = ((time.perf_counter_ns() - del_start) * pt.FUNC_AND_DICT_NUM * (len(UTI.startup_print_tricks_times)+1))
                # ... ###db(delTime, delTime2, delTime2-delTime, len(UTI.startup_print_tricks_times))

                # seconds = timeNow - startTime - time_taken_last_function - delTime - UTI.accumulated_print_tricks_time
                seconds = abs(
                    timeNow
                    - startTime
                    - time_taken_last_function
                    - delTime
                    - UTI.accumulated_print_tricks_time
                )
                UTI.accumulated_print_tricks_time = 0.0

                ## If sum, we need to print out both the last call to this, as well as
                ##   the total (sum) time, to this point, so we add the last recorded seconds
                ##   to the mag_last_n_total_seconds list, then append the final sum amount as well.
                ##   Now that we have the list, we can print each of the two lines in order.
                ##   if sum is False, we iterate the list of 1 item (seconds).
                mag_last_n_total_seconds = [seconds]
                if (
                    sum == True
                ):  ## KEEP this as == and not "sum is True" or I can't do shortcuts like 'pt.t(sum=1)'
                    tot_time = 0.0
                    for i in range(len(pt.sequences_dict.get(sequence))):
                        tot_time += pt.sequences_dict.get(sequence)[i][1]
                    tot_seconds = tot_time + seconds
                    mag_last_n_total_seconds.append(tot_seconds)
                    
                for i, magnitude_ns in enumerate(mag_last_n_total_seconds):
                    (
                        magnitude_seconds_str,
                        magnitude_specific_str,
                        specific_format,
                        magnitude_user_formatted_str,
                    ) = UTI._get_relative_magnitude_ns_and_format(
                        magnitude_ns, user_scale, pbi
                    )

                    # length = len(pt.sequences_dict.get(sequence)) + 1 ## we are adding 1 to account for the sequences append that we are going to do at the bottom of this function to account for the time of this function
                    length = len(pt.sequences_dict.get(sequence))
                    seq_orig_num = length - 1

                    first_line_str = (
                        f"{C.t1}{my_string}{C.er}{filler}{NAM.inst_nam}.t_infinite({formatted_args}): "
                    )
                    if sum and i == 1:
                        seq_orig_num = "0"
                        first_line_str = (
                            f"{C.t1}{my_string}{C.er}{filler}      >>> sum = "
                        )

                    if print_this == True:
                        print(
                            f"{first_line_str}"
                            f"{pbi}{magnitude_seconds_str}{C.t1} s{C.er} / "
                            f"{pbi}{magnitude_specific_str}{C.t1} {specific_format}{C.er} "
                            f"{magnitude_user_formatted_str}({0 if magnitude_ns == 0 else 1/(magnitude_ns/1_000_000_000):,.1f} FPS): "
                            f"Time between {C.t2}{sequence} {C.t1}#{seq_orig_num}{C.er} & {C.t2}{sequence} {C.t1}#{length}{C.er} "
                            f"(Line :{line_no}, {func_name_fmt}{file_name})"
                        )

                    ### return to previous garbage collection state, regardless of what we did in this function.
                    if pt.orig_garb_collect_state:
                        gc.enable()
                        pt.orig_garb_collect_state = gc.isenabled()
                    # ... ###db(4, pt.orig_garb_collect_state, gc.isenabled())

            ### returns the value in seconds of any key, either in the keys yet to be created, or the ones that are already established.
            ## Prep data for sending to the timeall function(if there is a timeall calling this)
            pt.sequences_dict[sequence].append(
                [timeNow, magnitude_ns, time.perf_counter_ns() - timeNow]
            )
        return_multi = [
            pt.sequences_dict.get(str(key))[-1][1] for key in sequences
        ]  # I have to convert the key to a string so that I can account for integers. Example 'pt.t_infinite(5)' will save as a string, but not count for one here unless I convert it to one.
        if get_timeall_data:
            return magnitude_ns, length, seq_orig_num
        if len_sequences == 1:
            return magnitude_ns
        else:
            return return_multi
        # end def t

    def tut(_line_no=None):
        return

    def use():
        ...
    def w(
        tag=None,
        sleepTime=None,
        str_front=None,
        str_back="",
        print_always=False,
        _line_no=None,
    ):
        """Custom wait/time.sleep function, that allows for the first sleep pt.w() event to specify the time to wait for all of the following wait functions with the identical tag. Blank tags will recieve a default tag. An intelligent and simple save system for your time.sleep waiting events."""
        # ... ###db(1)
        if pt.print_waits == False:
            if print_always == True:
                pass
            else:
                return
        my_string, filler = UTI._custom_str(str_front)

        wait = 0.1
        taggedWait = 0.0
        tagStr = "Default_Tag"

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        # args_only = re.compile(r'\((.*?)\).*$').search(code).groups()[0]

        #### This sets my pt.w function to allow a single number to switch roles from a "tag" to a "sleepTime" modifier instead, so that it isn't tagged at all.
        if sleepTime == None and str_front == None:
            if type(tag) == int or type(tag) == float:
                sleepTime = tag

        #### creating a default tag so that leaving it blank, will create a basic tag, so that all blanks thereafter will inherit the "new default" which was set by the LAST(?) pt.w() function that was set with a number inside it.
        if tag == None:
            pass

        else:
            # ... ###db('Tag exists')
            if type(tag) == str:
                tagStr = tag  ## we turn this into a string regardless of whether they put it as a string or not. So they can type in Number, or a string, and it
                # ... ###db(tagStr)

            else:
                # ... ###db('a number in tag position, treating it as Sleep Time:')
                sleepTime = tag
        # ... ###db(2)
        #### Create a dictionary entry with this tag & it's time value if it doesn't already exist
        if tagStr not in pt.tag_waits_dict:
            # ... ###db('create entry for this tagstr:')
            #### if sleepTime wasn't passed, at least give it a default value for now
            if sleepTime == None:
                # ... ###db('sleeptime none')
                pt.tag_waits_dict[tagStr] = [wait]
                taggedWait = wait
                # ... ###db(pt.tag_waits_dict)
            else:
                # ... ###db('sleeptime not none')
                pt.tag_waits_dict[tagStr] = [sleepTime]
                taggedWait = sleepTime
                # ... ###db(pt.tag_waits_dict)

        #### if the entry does exist (because a previous tag already exists in the code), then set the wait time to whatever was set beforehand.
        elif tagStr in pt.tag_waits_dict:
            # ... ###db('Use already existing entry for this tagStr')
            taggedWait = pt.tag_waits_dict[tagStr][0]
            # ... ###db(taggedWait)

        #### if sleeptime wasn't marked but the tag exists (NOT tagStr because tagStr always has a value, default if none), then set the wait time to the saved wait time for that tag
        # ... ###db(3)
        if sleepTime == None:
            # ... ###db('sleeptime none (2nd)')
            if tag:
                # ... ###db('if tag')
                wait = taggedWait
                # ... ###db(taggedWait)
                # ... ###db(wait)
            else:
                # ... ###db('not tag')
                wait = pt.tag_waits_dict[tagStr][0]

        ####if sleepTime DOES EXIST, and TAG also exists, then we are modifying the sleeptime for this tag from here after, so change the dictionary entry for this tag!
        else:
            if tag:
                pt.tag_waits_dict[tagStr] = [sleepTime]

            wait = sleepTime

        # print(
        #     C.t1 +my_string+ C.er+filler+
        #     C.eb+c.eu +'pt.w' + C.er+'('+
        #     C.t2 +str(wait)+ C.er+') - '+
        #     'Waiting for '+C.t3 +str(wait)+ C.er+' seconds.'+
        #     ' (Line :'+str(line_no)+', '+func_name_fmt+'\\'+file_name+') - '+C.t1+str_back+C.er
        #     )

        print(
            f"{C.t1}{my_string}{C.er}{filler}"
            f"{C.eb}{C.eu}pt.w{C.er}("
            f"{C.t2}{args_only}{C.er})"
            f" - Waiting for {C.t3}{wait}{C.er} seconds."
            f" (Line :{line_no}, {func_name_fmt}{file_name}) - {C.t1}{str_back}{C.er}"
        )
        # ... ###db(4)
        time.sleep(wait)
        # ... ###db(5)
        return
        # end def w

    def x(_line_no=None, **kwargs):
        for key, value in kwargs.items():
            print("%s == %s" % (key, value))

        # if kwargs[d1]:
        minF = 0.1  # example
        maxF = 0.5  # example
        minI = 0.1  # example
        maxI = 0.5  # example

        mFlt = ra.uniform(minF, maxF)
        mInt = ra.randint(minI, maxI)

        # RandStrings

        # newDict
        # end def x

    ############### Aliases for main pt functions. aliases #######################
    c                   = color = c
    counter             = counter = count = tracking = counter
    counter_fast        = counter_fast = count_fast = counter_fast
    ci                  = color_info = color_pt = cc = ci
    easy_testing        = easy_run = easy_run_from_here = run_here = run_from_here = run_project_here = run_project_from_here = run_this_project_here = run_this_as_main = run_this_as_main = easy_testing
    easy_imports        = easy_import = easy_imports
    e                   = error = e
    ex                  = exit_app = exit = quit = ex
    l                   = location = locations = directory = directories = cwd = l
    h                   = thread = threading = h
    hr                  = thread_result = thread_with_results = hr
    p                   = pause = p
    prefs               = preferences = config = prefs
    profile_resources   = resources = profile_cpu = profile_gpu = profile_memory = profile_resources
    props               = properties = prop = attributes = attr = attrs = props
    # funcs             = functions = funcs
    r                   = release = release_after = unlock = r
    rc                  = resource_control = simulate_hardware = sh = rc
    run                 = easy_run = easy_start_app = start_app = easy_run_script = easy_run_app = run_app = run_process = run_subprocess = run
    s                   = slowMo = slowMotion = s
    t                   = t2 = t = timer = time = t
    t_infinite          = ti = t_infinite
    w                   = wait = sleep = nap = w

    ############### Specialized functions that call main functions ################
    def release_unlocked(loops, numTimesToRun=0):
        """ """

    def enableEvery_n_loops():
        return pt.r()

    def enableAfterLoops():
        return pt.r()

    def enable_then_reenable_loops():
        return pt.r()

    def enableEvery_n_seconds():
        return pt.r()

    def enableafterSeconds():
        return pt.r()

    def enable_then_reenable_seconds():
        return pt.r()

    def pt(function_type="", print_always=False):
        if pt.print_pt_help == False:
            if print_always == True:
                pass
            else:
                return
        help_info = ""
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


        ## We create new docstrings for each pt function dynamically here, and override whatever triple quotes that they have right now in their functions. We are going to use the data contained within "Detailed _information"
        if function_type != "":
            if function_type == "e":
                pt.e.__doc__ = " hi aa299374"
                help_info = pt.e.__doc__
            elif function_type == "c":
                help_info = ""
            elif function_type == "h":
                help_info = ""
            elif function_type == "hr":
                help_info = ""
            elif function_type == "l":
                help_info = ""
            elif function_type == "w":
                help_info = ""
            elif function_type == "t":
                help_info = ""
            elif function_type == "p":
                help_info = ""
            elif function_type == "enable":
                help_info = ""
            elif function_type == "disable":
                help_info = ""
            elif function_type == "prefs":
                help_info = ""
            elif function_type == "delete":
                help_info = ""
            elif function_type == "tut":
                help_info = ""
            elif function_type == "pt" or function_type == "help":
                help_info = ""
            elif function_type == "ggkjhg":
                help_info = ""
            elif function_type == "ggkjhg":
                help_info = ""
            elif function_type == "ggkjhg":
                help_info = ""
            elif function_type == "ggkjhg":
                help_info = ""
            elif function_type == "ggkjhg":
                help_info = ""

        else:
            global ReadMe_Quick
            global ReadMe_Detailed
            global TODO
            global TODO_QUICK
            global TODO_Errors
            global TODO_LONG_TERM
            help_info = (
                ReadMe_Quick
                + ReadMe_Detailed
                + TODO_QUICK
                + TODO_Errors
                + TODO_LONG_TERM
            )

            BoldColorList = (
                "Quick Summary",
                "Print Tricks",
                "To Import Into Your Project",
                "Functions in Print Tricks Class",
                "Functions being worked on",
                "Function Details",
                "pt.pt()",
                "pt()",
                "pt.delete()",
                "pt.e()",
                "pt.h()",
                "pt.hr()",
                "pt.l()",
                "pt.p()",
                "pt.t()",
                "pt.w()",
                "pt.disable()",
                "pt.enable()",
                "pt.tut()",
                "pt.prefs()",
                "TODO",
                "Print Tricks & More -",
            )
            for topic in BoldColorList:
                topic_Edited = C.t3 + C.eb + topic + C.er
                help_info = help_info.replace(topic, topic_Edited)

            pt_newExample1 = (
                "pt("
                + C.t2
                + "my_var"
                + C.er
                + "): "
                + C.t3
                + "123"
                + C.er
                + " - int, Length: 3, (Line :75, #myFunction, my_file.py)"
            )
            help_info = help_info.replace(
                "pt(my_var): 123 - int, Length: 3, (Line :75, #myFunction, my_file.py)",
                pt_newExample1,
            )

            pt_newExample2 = (
                C.t1
                + "my_string"
                + C.er
                + " - pt("
                + C.t2
                + "my_var"
                + C.er
                + ", 'my_string'): "
                + C.t3
                + "123"
                + C.er
                + " - int, Length: 3, (Line :75, #myFunction, my_file.py)"
            )
            help_info = help_info.replace(
                "my_string - pt(my_var, 'my_string'): 123 - int, Length: 3, (Line :75, #myFunction, my_file.py)",
                pt_newExample2,
            )

        print(
            "pt.pt("
            + C.t2
            + function_type
            + C.er
            + "): "
            + ", (Line :"
            + str(line_no)
            + ", "
            + func_name_fmt
            + "\\"
            + file_name
            + ")"
            + help_info
        )
        return
        # end def pt

class p(pt):
    is_p_alias_imported = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        NAM.inst_nam = 'p'
############### Utilities Helper Class for pt ################
class UTI:
    """TODO TODO - Do the thing here that I did in PT() that allowed the function to process much faster. Will help my pt statements to run fast"""

    ############################ UTI Vars ############################

    startup_print_tricks_times = {}
    accumulated_print_tricks_time = 0.0

    interupt_thread = False
    
    
    ############################ UTI Functions ############################
    
    def _get_relative_magnitude_ns_and_format(
        magnitude_ns, user_scale, color_code=""
        ):
        ## set the magnitude scale
        specific_format = "ns" # Nanosecond (default)
        abs_magnitude_ns = abs(magnitude_ns)

        if abs_magnitude_ns >= 1e9:  # 1 second
            if abs_magnitude_ns > 31556952e9:  # 1 year
                specific_format = "years"
            elif abs_magnitude_ns > 2629800e9:  # 1 month
                specific_format = "months"
            elif abs_magnitude_ns > 604800e9:  # 1 week
                specific_format = "weeks"
            elif abs_magnitude_ns > 86400e9:  # 1 day
                specific_format = "days"
            elif abs_magnitude_ns > 3600e9:  # 1 hour
                specific_format = "hours"
            elif abs_magnitude_ns > 60e9:  # 1 minute
                specific_format = "m"
            else:
                specific_format = "s"
        elif abs_magnitude_ns < 1e9:  # less than 1 second
            if abs_magnitude_ns > 1e6:  # millisecond
                specific_format = "ms"
            elif abs_magnitude_ns > 1e3:  #microsecond
                specific_format = "µs"



        magnitude_specific = magnitude_ns
        if specific_format in pt.mag_dict_div:
            magnitude_specific = magnitude_ns / pt.mag_dict_div[specific_format]
        elif specific_format in pt.magnitude_dict_multiply:
            magnitude_specific = (
                magnitude_ns / pt.magnitude_dict_multiply[specific_format]
            )

        magnitude_user = 0.0
        if user_scale != "":
            if user_scale in pt.mag_dict_div:
                magnitude_user = magnitude_ns / pt.mag_dict_div[user_scale]
            elif user_scale in pt.magnitude_dict_multiply:
                magnitude_user = (
                    magnitude_ns / pt.magnitude_dict_multiply[user_scale]
                )

        magnitude_seconds_str = f'{magnitude_ns/1000000000:.20f}'
        magnitude_specific_str = f"{magnitude_specific:.7f}".rstrip("0")
        magnitude_user_str = f"{magnitude_user:.7f}".rstrip("0")
        # print(f"seconds: {magnitude_ns / 1000000000}, magnitude_ns: {magnitude_ns}, magnitude_specific_str: {magnitude_specific_str}")

        magnitude_specific_str = (
            magnitude_specific_str + "00"
            if magnitude_specific_str.endswith(".")
            else magnitude_specific_str
        )
        magnitude_user_str = (
            magnitude_user_str + "00"
            if magnitude_user_str.endswith(".")
            else magnitude_user_str
        )

        magnitude_user_formatted_str = ""
        if user_scale != "":
            magnitude_user_formatted_str = (
                f" / {color_code}{magnitude_user_str}{C.t1} {user_scale}{C.er}"
            )

        return (
            magnitude_seconds_str,
            magnitude_specific_str,
            specific_format,
            magnitude_user_formatted_str,
        )

    def _enable_disable_type_class_name_func_type(function_type=None):
        """Utility helper class for pt.enable and pt.disable"""
        ## replace pt. if user passed type to disable as pt.t / pt.w / pt.p etc instead of just the type 't' or 'w' or 'p'
        if "pt." in function_type:
            function_type = function_type.replace("pt.", "")

        ## set default class_name to 'pt.' for printing purposes, but if the function_type to disable is actually a generic pt() statement, then remove it from the string because we would be repeating _information.
        class_name = "pt."
        classes_to_ignore = "pt"
        if function_type in classes_to_ignore:
            class_name = ""
        return class_name, function_type

    def _allStringsQ(args):
        return True if all(map(lambda x: type(x) is str, args)) else False

    def _bytes_size(varObject, 
                    print_sources=False, 
                    print_sources_count=False, 
                    reduced_size_q=False, 
                    num_of_divisions_from_original=0,
                    manually_called=False, ## if pt.size is used, then manually_called = True. otherwise, its being called from with pt or another function. 
                    ):
        """Modified code, originally from Liran Funaro @ https://stackoverflow.com/questions/13530762/how-to-know-bytes-size-of-python-object-like-arrays-and-dictionaries-the-simp"""
        
        size = math.nan
        sources = ''
        sources_count = 0
        
        if not manually_called:
            if not isinstance(varObject, (list, dict, set, int, float, str, tuple, bytes)):
                return size, sources, sources_count
        
        size = 0
        marked = {id(varObject)}
        obj_q = [(varObject, "varObject")]
        
        while obj_q:
            obj, source = obj_q.pop(0)
            size += sys.getsizeof(obj)

            all_refr = ((id(o), o) for o in gc.get_referents(obj))

            new_refr = {
                o_id: (o, source)
                for o_id, o in all_refr
                if o_id not in marked and not isinstance(o, type)
            }

            obj_q.extend(new_refr.values())
            marked.update(new_refr.keys())


            if print_sources is True or print_sources_count is True:
                for o, src in new_refr.values():
                    sources += f"Added {sys.getsizeof(o)} bytes from {o}\n"
                sources_count += 1
        return size, sources, sources_count

    def _bytes_size_formatter(this_bytes, args_only, sources, sources_count, print_sources=False, print_sources_count=False):
        """This function prints the size of the object passed in."""
        
        # this_bytes = UTI._bytes_size(varObject)
        
        lenB = len(str(this_bytes))
        sizeType = ""
        formattedSize = 0
        if lenB <= 3:
            sizeType = "Bytes"
            size_ = f"{this_bytes} {sizeType}"
            size_colored = (
                f"pt.size({C.t2}{args_only}{C.er}): {C.t3}{this_bytes} {sizeType}{C.er}"
            )
            return (size_, size_colored)
        elif lenB <= 6:
            sizeType = "KB"
            formattedSize = this_bytes / 1024
        elif lenB <= 9:
            sizeType = "MB"
            formattedSize = this_bytes / (1024 * 1024)
        elif lenB <= 12:
            sizeType = "GB"
            formattedSize = this_bytes / (1024 * 1024 * 1024)

        formattedSize = round(formattedSize, 2)

        size_ = f"{formattedSize} {sizeType}"
        size_colored = f"pt.size({C.t2}{args_only}{C.er}): ~{C.t3}{formattedSize}{C.er} {sizeType}, or {C.t3}{this_bytes}{C.er} Bytes"
        
        if print_sources_count is True:
            size_colored += f' from {C.t3} {sources_count}{C.er} sources'
        if print_sources is True:
            size_colored += f'\n       >>> Sources: \n{sources}\n'
        return size_, size_colored

    def _readable_time(unixTime):
        time_obj = time.localtime(unixTime)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_obj)

        return time_str

    def _delete_it(my_file, delete_what, replace_with, num_instances):
        nameOfFileOnly = os.path.basename(my_file)
        backup_dir_only = pt.l("pt.delete(BackupFiles)\\")
        current_time = time.strftime("%Y-%m-%d___%H-%M-%S", time.localtime())
        backupPath = backup_dir_only + nameOfFileOnly + "_" + current_time + ".bak"        
        
        if os.path.isdir(backup_dir_only): pass
        else: os.mkdir(backup_dir_only)
        
        with Modify_This_File_Here(my_file, backup=backupPath) as file:
            for line in file:
                line = line.replace(delete_what, replace_with)
                file.write(line)
                
        print(f"{C.t2}>>>Backup file created:{C.er}\n       {backupPath}")
        print(
            f"{C.t2}>>>{C.eb}{C.eu}{num_instances}{C.er}"
            f' Instance(s) of " {C.t3}{delete_what}{C.er}" Deleted'
        )

        return

    def _turn_on_off_functions(function_type, enable_or_disable=type(str)):
        # ... ###db(function_type)
        # ... ###db(enable_or_disable)
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        # args_only = re.compile(r'\((.*?)\).*$').search(code).groups()[0]

        msg_disable_all = ""

        if enable_or_disable == "enable":
            True_or_False = True
        elif enable_or_disable == "disable":
            True_or_False = False
        if function_type == None:
            msg_disable_all = "Disabling all PT Print Tricks functions.... (to specify just one function, do this: pt.disable('t')"
            pt.print_deletes = True_or_False
            pt.print_exceptions = True_or_False
            pt.print_threads = True_or_False
            # print_infos = True_or_False ### Should change this to "print Variables".
            pt.print_locations = True_or_False
            pt.print_pauses = True_or_False
            pt.print_pt_statements = True_or_False
            pt.print_timers = True_or_False
            pt.print_waits = True_or_False
            pt.print_pt_help = True_or_False
            pt.print_colors = True_or_False
            pt.print_colors_tags = True_or_False
            pt.print_prefs = True_or_False
        elif function_type == "d":
            pt.print_deletes = True_or_False
        elif function_type == "e":
            pt.print_exceptions = True_or_False
        elif function_type == "h":
            pt.print_threads = True_or_False
        elif function_type == "l":
            pt.print_locations = True_or_False
        elif function_type == "p":
            pt.print_pauses = True_or_False
        elif function_type == "pt":
            pt.print_pt_statements = True_or_False
        elif function_type == "t":
            pt.print_timers = True_or_False
        elif function_type == "w":
            pt.print_waits = True_or_False
        elif function_type == "c":
            pt.print_colors = True_or_False
        elif function_type == "cc":
            pt.print_colors_tags = True_or_False
        elif function_type == "prefs":
            pt.print_prefs = True_or_False
        # elif function_type == '':
        #     pt.print_ = True_or_False
        # elif function_type == '':
        #     pt.print_ = True_or_False
        # elif function_type == '':
        #     pt.print_ = True_or_False

        # print('pt.'+enable_or_disable+'('+ C.t2 +args_only+C.er+'): '+
        # ' - (Line :'+str(line_no)+', '+func_name_fmt+'\\'+file_name+') - '+msg_disable_all+' - For performance measurements, Type pt.pt("disable")')

        # print(
        #     f'pt.{enable_or_disable}({C.t2}{args_only}{C.er}):'
        #     f' (Line :{line_no}, {func_name_fmt}{file_name})'
        #     f' {msg_disable_all} - Disable pt statements (and python prints) when measuring the performance of your code.'
        #     )

        return enable_or_disable

    def _custom_str(str_front):
        if str_front != None:
            str_front = f"{C.t1}{str_front}{C.er}"
            filler = f"{C.t1} - {C.er}"
        else:
            filler = ""
            str_front = ""

        return str_front, filler

    def _print_custom(
        print_str,
        str_front=None,
        str_back=None,
        print_always=False,
        end="\n",
        sep=" ",
        file=None,
        flush=False,
    ):
        """print cython printcythonprint
        - cython speedup doesn't appear to work... at least with autocompile. Try manually doing it later?
        - It was definitely speeding up the print statements earlier. So not sure what happened.
        """

        # print(print_str)
        print(print_str, end=end, sep=sep, file=file, flush=flush)

    def _info(
        simp_trace_output,
        variables_len,
        variables,
        args_only,
        file=None,
        str_front=None,
        str_back=None,
        mvl=65,
        end="\n",
        sep=" ",
        flush=False,
    ):
        """All _info needed for your variable"""
        ## def info pt main print part

        disabledColors = False

        if file is not None:
            UTI._disableColors_simple()
            disabledColors = True

        print_str = ""
        if str_front is not None:
            str_front, filler = UTI._custom_str(str_front)
        else:
            str_front = ""
            filler = ""
        if str_back is None:
            str_back = ""

        # file_name, file_path, line_no, func_name, func_name_fmt, code, args_with_specials, args_only, formatted_args, fmt_args_list  = UTI._simple_trace(argsLen)
        file_name = simp_trace_output[0]
        file_path = simp_trace_output[1]
        line_no = simp_trace_output[2]
        func_name = simp_trace_output[3]
        func_name_fmt = simp_trace_output[4]
        code = simp_trace_output[5]
        formatted_args = simp_trace_output[8]
        fmt_args_list = simp_trace_output[9]
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no
        
        C.t3 = (
            C.Fore_BLUE
        )  ## Reset the color to default because the following print_str needs to be the default.
        ## TODO TODO: need to change this to reset to user preferences, not to a specific color like fore_BLUE
        ## Sets up the print_str for the multi-variables (will reset it inside if only single values).
        print_str = f"{str_front}{filler}{NAM.inst_nam}({formatted_args}) Length: {C.eu}{C.t3}{variables_len} variables{C.er} (Line :{line_no}, {func_name_fmt}{file_name}) - {str_back}"

        for v in range(variables_len):
            ### TODO TODO: This may iterate over everything in a string or a list that is really just a made up list of 1 unit for some reason. do a ... ###db(fmt_args_list) and then see what this does. Note: The v in here is just a counter, nothing more.
            num = v + 1
            # ... ###db(fmt_args_list)
            # ... ###db(variables)
            variable = variables[v]
            varType = type(variable)
            var_type_as_str = varType.__name__
            if varType is int:
                if args_only.lower().startswith("0o"):
                    var_type_as_str = "octal/int"
                elif args_only.lower().startswith("0x"):
                    var_type_as_str = "hexadecimal/int"
                elif args_only.lower().startswith("0b"):
                    var_type_as_str = "binary/int"
                    
                    
                    
                    
            ### Get optional length_var
            try:
                ## TODO arg = fmt_args_list[v] doesn't really do anything.... somehow converts it, but probs a better way. 
                ##        I'm pretty sure formatted_args returns the same thing??? But these get sent to length_var which is supposed
                ##        to be just one arg so... not entirely sure what to do with it. 
                arg = fmt_args_list[v] ## get optional arg, to send to get length_var. Used for detecting number of values in a bool in UTI._getVarLength
                # ... ###db(fmt_args_list, arg, formatted_args)
            except:
                arg = '_unknown_'
                ... ###db('--- Warning, there are no args listed, traceback.extract_stack must not be getting access to the stack. Is this a child process? - Check the variable "new_trace_level" \n')
            length_var = UTI._getVarLength(variable, varType, arg)

            
            
        
            
            UTI._setVarColor(
                varType
            )  ## sets Var color by re-assigning the C.t3 string escape code.

            try:
                var_as_str = str(variable)
            except TypeError as e:
                var_as_str = f'pt() - Python is Unable to retrieve variable due to {e}.'
            
            if callable(
                variable
            ):  ## according to XerCis @ https://stackoverflow.com/questions/624926/how-do-i-detect-whether-a-python-variable-is-a-function,
                ## the fastest way that also guarantees a positive check on whether something is a function is to check if it is callable....

                ## inspect.getsource is placed in try/catch in case whatever was passed was not a known data type.
                ## This protects from someone trying to print out something like MyDict.keys, when they should have done MyDict.keys().
                ## Now, instead of crashing, it'll skip this part and simply print correctly.
                try:
                    inspected_var = inspect.getsource(variable)
                    var_as_str = str(inspected_var)
                    # print('varasstring: ', var_as_str)
                except:
                    pass

                var_as_str = f"{C.er} {C.t3}".join(var_as_str.split("\n"))
                var_as_str = f" ".join(var_as_str.split())

            ####### Gets size of variable (so can determine how to make the print statement more readable)
            (
                variable,
                reduced_size_q,
                num_of_divisions_from_original,
            ) = UTI._process_large_vars(variable, varType, length_var)

            ### Appending some spacing onto the str_front so that if it exists, it'll print, but if the str_front is blank, it won't print)
            _bytes_size = 0
            try:
                _bytes_size, _, _ = UTI._bytes_size(
                    variable, args_only)
                if reduced_size_q == True:
                    _bytes_size = int(
                        (float(_bytes_size) * num_of_divisions_from_original)
                    )

            except Exception:
                pt.e()
                _bytes_size = 0

            #### creating the print statement ####
            # terminal_width = os.get_terminal_size().columns
            terminal_size = shutil.get_terminal_size((80, 20))  # pass fallback values
            terminal_width = terminal_size.columns
            if variables_len == 1:

                print_str = f"{str_front}{filler}{NAM.inst_nam}({formatted_args}): "  ## Reset the print_str to accomdate for the singular values.
                tot_len_str = (
                    len(print_str) + len(var_as_str) + len(str_back) + len(str_front)
                )

                if _bytes_size < 800 or tot_len_str < terminal_width:
                    if tot_len_str < terminal_width:
                        ## if it'll fit on one line:
                        print_str += f"{C.t3}{var_as_str}{C.er} - {var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt}{file_name}) - {str_back}"
                        
                    else:
                        ## if it's too long for one line
                        var_as_str = textwrap.fill(
                            var_as_str,
                            width=terminal_width,
                            initial_indent=f"{C.er}    >    {C.t3}",
                            subsequent_indent=f"{C.er}    >    {C.t3}",
                        )  ## We are wrapping the maximum length of the var_as_str to be controlled and orderly.
                        # var_as_str = print_str
                        
                        print_str += (
                            f"{var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt} {file_name}) - {str_back}\n"
                            f"{C.t3}{var_as_str}{C.er}"
                        )

                else:
                    ## if it's a huge byte size

                    this_bytes, sources, sources_count = UTI._bytes_size(variable, args_only)
                    bytes_size_formatted = UTI._bytes_size_formatter(this_bytes, args_only, sources, sources_count)[0]

                    if reduced_size_q == True:
                        bytes_size_formatted += " (estimated)"
                    var_as_str = textwrap.fill(
                        var_as_str,
                        width=terminal_width,
                        initial_indent=f"{C.er}    >    {C.t3}",
                        subsequent_indent=f"{C.er}    >    {C.t3}",
                        max_lines=mvl,
                    )  ## We are wrapping the maximum length of the var_as_str to be controlled and orderly.

                    print_str += (
                        f"{C.t3}({C.er}{length_var} elements below{C.t3}){C.er} {NAM.inst_nam}.size = {bytes_size_formatted} - {var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt}{file_name})\n"
                        f"{C.t3}{var_as_str}{C.er}\n"  ### These lines are already indented due to the 'var_as_str = textrap.fill() command above
                        f"\t    ^ ^ ^ {NAM.inst_nam}({C.t2}{formatted_args}{C.er}): {C.t3}({C.er}{length_var} elements above this{C.t3}){C.er} {NAM.inst_nam}.size = {bytes_size_formatted} - {var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt}{file_name})"
                    )

            else:
                ## multi-variables
                tot_len_str = len(var_as_str) + len(str_back) + len(str_front)

                if _bytes_size < 800 or tot_len_str < terminal_width:
                    if tot_len_str < terminal_width:
                        ## multi-variables - if it'll fit on one line:
                        try:
                            print_str += f"\n    >{num}>  {C.t2}{fmt_args_list[v]}{C.er}: {C.t3}{var_as_str}{C.er} - {var_type_as_str}, Length: {length_var}"
                        
                        except Exception as e:
                            print('-- ! Error with the following print message. Error: {e}. \nMessage:')
                            print_str += f"\n    >{num}>  {C.t2}Unknown Var{C.er}: {C.t3}{var_as_str}{C.er} - {var_type_as_str}, Length: {length_var}"

                    else:
                        ## multi-variables - if it's too long for one line
                        var_as_str = textwrap.fill(
                            var_as_str,
                            width=terminal_width,
                            initial_indent=f"{C.er}       >  {C.t3}",
                            subsequent_indent=f"{C.er}       >  {C.t3}",
                        )  ## We are wrapping the maximum length of the var_as_str to be controlled and orderly.
                        
                        
                        try:
                            print_str += (
                            f"\n    >{num}>  {C.t2}{fmt_args_list[v]}{C.er}: {C.t3}({C.er}{length_var} elements below{C.t3}){C.er} - {var_type_as_str}, Length: {length_var}\n"
                            f"{C.t3}{var_as_str}{C.er}"
                        )
                        except Exception as e:
                            print('-- ! Error with the following print message. Error: {e}. Message:')
                            print_str += f"\n    >{num}>  {C.t2}Unknown Var{C.er}: {C.t3}{var_as_str}{C.er} - {var_type_as_str}, Length: {length_var}"

                # Assuming the rest of the code is unchanged and focusing on the problematic section
                else:
                    # Multi variables - if it's a huge byte size
                    this_bytes, sources, sources_count = UTI._bytes_size(variable, args_only)
                    bytes_size_formatted = UTI._bytes_size_formatter(this_bytes, args_only, sources, sources_count)[0]
                    
                    if reduced_size_q == True:
                        bytes_size_formatted += " (estimated)"
                    
                    # Wrap var_as_str to fit within the terminal width
                    var_as_str_wrapped = textwrap.fill(
                        var_as_str,
                        width=terminal_width,
                        initial_indent=f"{C.er}       >  {C.t3}",
                        subsequent_indent=f"{C.er}       >  {C.t3}",
                        max_lines=mvl,
                    )
                    
                    try:
                        # Construct the top and bottom strings without additional wrapping
                        end_top_str = f"\n    >{num}>  {C.t2}{fmt_args_list[v]}{C.er}: {C.t3}({C.er}{length_var} elements below{C.t3}){C.er} pt.size = {bytes_size_formatted} - {var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt}{file_name})\n"
                        bot_end_str = f"\n    ^ ^ ^ pt({C.t2}{fmt_args_list[v]}{C.er}): {C.t3}({C.er}{length_var} elements above this{C.t3}){C.er} pt.size = {bytes_size_formatted} - {var_type_as_str}, Length: {length_var}, (Line :{line_no}, {func_name_fmt}{file_name})"
                    except Exception as e:
                        print('Error {e} with the following message...')
                        print_str += f"\n    >{num}>  {C.t2}Unknown Var{C.er}: {C.t3}{var_as_str}{C.er} - {var_type_as_str}, Length: {length_var}"

                    # Concatenate all parts together
                    print_str += end_top_str + var_as_str_wrapped + bot_end_str
        
        
        # ... ###db('--test start--', print_str, '--- test over')
        print(print_str, end=end, sep=sep, file=file, flush=flush)

        # sys.stdout.write(print_str)
        C.er  ## we reset the color here as a catch-all to ensure that it gets reset.
        C.t3 = (
            C.Fore_BLUE
        )  ## Reset the color to default because the following print_str needs to be the default.
        ## TODO TODO: Change this to user preferences color for C.t3, note just Fore_blue

        if disabledColors == True:
            UTI._enableColors_simple()
            disabledColors = False
        UTI.accumulated_print_tricks_time += (
            time.perf_counter() - UTI.startup_print_tricks_times["pt()__init__"]
        )
        # ... ###db(UTI.accumulated_print_tricks_time, time.perf_counter(), UTI.startup_print_tricks_times['pt()__init__'], time.perf_counter() - UTI.startup_print_tricks_times['pt()__init__'])

        # # console.dir(arr, {'maxArrayLength': null});
        # pt.num_pt_count += 1
        # print(pt.num_pt_count)
        # # print('print_str: \n', print_str)
        # pt.rapid_pt_bulk_print_block += print_str+'\n'
        # pt.bulk_print_list.append(print_str)
        # # print('bulk: \n', pt.rapid_pt_bulk_print_block)

        # # print('num_pt_count', ': ', pt.num_pt_count)

        # if thisTime >= pt.time_to_print:
        #     pt.time_to_print = thisTime + 1.
        #     print('if')
        #     # print(str(pt.bulk_print_list))
        #     # print('len bulk print list: ', len(pt.bulk_print_list))
        #     # finalString = "\n".join(pt.bulk_print_list)
        #     # print(finalString)

        # #     print('start')
        #     print('bulk: \n', pt.rapid_pt_bulk_print_block)
        #     # pt.rapid_pt_bulk_print_block = ''

        # print('after reset')
        # print(pt.rapid_pt_bulk_print_block)
        # print('end')

        #     # print(copyPrintBulk)
        #     # pt.p()
        # # else:
        # #     print('else')

        # thisTime = time.time()
        # if pt.sent_bulk_print_to_thread == False:
        #     if thisTime - last_bulk_print_time > .5:
        #         threading.Thread(target=UTI._check_for_bulk_print_time, args=(pt.rapid_pt_bulk_print_block,)).start()

        # print(len(pt.rapid_pt_bulk_print_block));print(' aaa')
        # if pt.sent_bulk_print_to_thread == False:
        #     pt.sent_bulk_print_to_thread = True
        #     # pt.rapid_pt_bulk_print_block = ''
        #     # pt.rapid_pt_bulk_print_block += print_str+'\n'

        #     print('sending to print thread')
        #     # threading.Thread(target=UTI._check_for_bulk_print_time, args=()).start()
        #     gg = ThreadWithResult(target=UTI._threadedTimer)
        #     print(gg)
        #     if gg == True:
        #         print('success')
        #     print(print_str)
        # # # pt.rapid_pt_bulk_print_block += print_str+'\n'

        # return

        # # print(len(pt.rapid_pt_bulk_print_block));print(' aaa')
        # if pt.sent_bulk_print_to_thread == False:
        #     pt.sent_bulk_print_to_thread = True
        #     # pt.rapid_pt_bulk_print_block = ''
        #     # pt.rapid_pt_bulk_print_block += print_str+'\n'

        #     print('sending to print thread')
        #     # threading.Thread(target=UTI._check_for_bulk_print_time, args=()).start()

        # # # pt.rapid_pt_bulk_print_block += print_str+'\n'

        # return

    # g = 0
    # def rapid_pt_bulk_print_block(prstr):
    ## Set g to the number of print statements in the code (but not including the loops???)
    ## NOTE: if i set g to an absurd number, far beyond my print statements, it still prints faster than normal prints because the loops of counting +=1 on g,  are actually pretty quick.
    # if g == 990:
    #     print(prstr)
    # else:
    #     g+=1
    def _simple_trace_new(argsLen=1):
        """simple trace 1"""
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = ("", "", "", "", "", "", "", "", "", "")

        ### new test 2:
        fi = sys._getframe(2)
        line_no = fi.f_line_no
        func_name = fi.f_code.co_name
        file_path = fi.f_code.co_file_name

        f = open(file_path)
        all_lines = f.readlines()
        code = all_lines[line_no - 1]

        # print('----------',  '\ncode: ', code, '\nline: ', line_no, '\nname: ', func_name, '\nfile_path: ', file_path)

        # sys.exit()

        try:
            while True:
                # print('inside code: ', code)
                # file_path, line_no, func_name, code = traceB[pt.new_trace_level]
                fi = sys._getframe(2)
                file_path, line_no, func_name = (
                    fi.f_code.co_file_name,
                    fi.f_line_no,
                    fi.f_code.co_name,
                )
                func_name = func_name + ", "
                code = all_lines[line_no - 1]
                code = all_lines[line_no - 1]
                # f.close()

                # print('1 - line_no - code - func_name - file_path: ', line_no, code, func_name, file_path)
                if code == "":
                    ## for cases where we are looking for pt statements within eval or exec code. Traceback will show a line number, but not
                    ## any code. So in our Exec(), we must always set the pt.cur_exe_str to the code we are about to execute, just before we
                    # do it.
                    ess = (
                        pt.cur_exec_str.splitlines()
                    )  ## we are setting the cur_exec_str before we do any eval(code) / exec(code), then we re getting it's value here.
                    # print('ess: ', ess)
                    code = ess[
                        int(line_no - 1)
                    ]  # -1 because the line_no is 1-based, but our code is 0-based.

                if "UTI._simple_trace(" in code:
                    pt.new_trace_level -= 1
                    # print('found _simple_trace in code, increasing new trace level to: ', pt.new_trace_level)
                # elif 'pt(' in code or 'pt.' in code:

                # elif "pt(" in code or "pt." in code or "pts(" in code or "... ###db(" in code: ## NOTE: deleted last two checks. no longer needed I think. 
                elif "pt(" in code or "pt." in code:
                    # print('2: found in code: ', code)
                    if "<module>" in func_name:
                        func_name = ""

                    if func_name == "":
                        func_name_fmt = ""
                    else:
                        func_name_fmt = f"@{func_name}, "

                    file_name = os.path.basename(
                        file_path
                    )  ## gets just name of file, without the whole directory
                    ## Check if this is a pt type statement that is spread between multiple lines.
                    (
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ) = UTI._trace_processing(file_path, line_no, code, argsLen)

                    # print('code: ', code)
                    return (
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    )

                else:
                    # print('increasing new trace level to: ', pt.new_trace_level)
                    pt.new_trace_level -= 1

        except:
            ... ###db.e()
            return "", "", "", "", "", "", "", "", "", ""
        finally:
            pt.new_trace_level = -3

    def _simple_trace(argsLen=1):
        """simple trace 1"""
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = ("", "", "", "", "", "", "", "", "", "")

        #### Original, working version:
        # ... ###db.t()
        traceB = traceback.extract_stack()
        # ... ###db.t()
        try:
            while True:
                # print(f'{pt.new_trace_level=}')
                # print('inside code: ', code)
                file_path, line_no, func_name, code = traceB[pt.new_trace_level]

                # frame,file_path,line_no,func_name,code,index = inspect.stack()[2]

                # print('1 - line_no - code - func_name - file_path: ', line_no, code, func_name, file_path)
                if code == "":
                    ## for cases where we are looking for pt statements within eval or exec code. Traceback will show a line number, but not
                    ## any code. So in our Exec(), we must always set the pt.cur_exe_str to the code we are about to execute, just before we
                    # do it.
                    ess = (
                        pt.cur_exec_str.splitlines()
                    )  ## we are setting the cur_exec_str before we do any eval(code) / exec(code), then we re getting it's value here.
                    # print('ess: ', ess)
                    code = ess[
                        int(line_no - 1)
                    ]  # -1 because the line_no is 1-based, but our code is 0-based.
                
                # ... ###db(NAM.inst_nam)
                if "UTI._simple_trace(" in code:
                    pt.new_trace_level -= 1
                    # print('found _simple_trace in code, increasing new trace level to: ', pt.new_trace_level)
                # elif 'pt(' in code or 'pt.' in code:

                # elif "pt(" in code or "pt." in code or "pts(" in code or "... ###db(" in code: ## NOTE: deleted last two checks. no longer needed I think. 
                elif F"{NAM.inst_nam}(" in code or F"{NAM.inst_nam}." in code:                    # ... ###db(code)
                    # print('2: found in code: ', code)
                    if "<module>" in func_name:
                        func_name = ""

                    if func_name == "":
                        func_name_fmt = ""
                    else:
                        func_name_fmt = f"@{func_name}(), "

                    file_name = os.path.basename(
                        file_path
                    )  ## gets just name of file, without the whole directory
                    ## Check if this is a pt type statement that is spread between multiple lines.
                    (
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    ) = UTI._trace_processing(file_path, line_no, code, argsLen)
                    # ... ###db(line_no, argsLen)

                    # print('code: ', code)
                    
                    return (
                        file_name,
                        file_path,
                        line_no,
                        func_name,
                        func_name_fmt,
                        code,
                        args_with_specials,
                        args_only,
                        formatted_args,
                        fmt_args_list,
                    )

                else:
                    # ... ###db('increasing new trace level to: ', pt.new_trace_level)
                    pt.new_trace_level -= 1

        ## TODO: This exception has caused me all sort of problems. When it was just:
        ##        ' except:
        ##         return "", "", "", "", "", "", "", "", "", ""   '
        ##       It worked fine, except that it wouldn't stop loops from looping even
        ##       if I did sys.exit() / pt.ex() / ... ###db.ex()
        except Exception as e:
            # pt.e()
            return "", "", "", "", "", "", "", "", "", ""
        finally:
            pt.new_trace_level = pt.default_trace_level

    def _trace_processing(file_path, line_no, code, argsLen):
        ## Check if there are multiple statements on the same line (separated with a ';')
        # ... ###db(code)
        if ";" in code:
            # ... ###db("bad char in code ", code)
            count_pt = UTI._count_num_pt_statements(code)
            # ... ###db(count_pt)
            code = UTI._track_pt_on_one_line(code, count_pt)
            # ... ###db(code)
        else:
            pt.current_pt_on_multi_line = 0

        check_line = line_no
        count_a = code.count("(")
        count_b = code.count(")")

        ## Multi-line check & inner-parenthesis check:
        ##  If there is a missing ')' on this line, then this is a multi-line statement.
        ##  And if there is at least one ')' but it's count is less than '(' count, then there is an inner-parenthesis
        if count_a != count_b:  # This is a multi-line pt statement
            # print('count')
            while True:
                check_line += 1
                # nextLine = linecache.getline(file_path, check_line)
                nextLine = traceback.linecache.getline(file_path, check_line)

                test_4_comment = (
                    nextLine.strip()
                )  ## removes leading/trailing whitespaces, so I can look for a '#' at beginning of line
                if not test_4_comment.startswith("#"):  ## If '#' at beginning, skip this line!!! Else, append the next line to the code_on_muli_lines

                    if (
                        "#" in nextLine
                        or "str_front" in nextLine
                        or "str_back" in nextLine
                    ):
                        
                        nextLine, separator, removed_text = nextLine.partition(
                            "#"
                        )  ## separate out the text after a '#': Note: That apparently 
                            ## .partition is the fastest way to split a string, so consider using it in other parts of my code instead of strip(), rstrip() etc.
                        nextLine, separator, removed_text = nextLine.partition(
                            "str_front"
                        )
                        nextLine, separator, removed_text = nextLine.partition(
                            "str_back"
                        )
                    ## We now remove all heavy whiteSpace from the nextLine
                    nextLine = nextLine.strip()
                    code += f"\n{nextLine}"
                    count_a += nextLine.count(
                        "("
                    )  ## Count number of "(" and ")" in code so I can find the beginning and the end
                    count_b += nextLine.count(")")
                if count_a == count_b:
                    break

        else:  # This is a 1-line pt statement.
            # print('else')
            if "#" in code or "str_front" in code or "str_back" in code:
                code, separator, removed_text = code.partition("#")  # Remove stuff after '#'
                code, separator, removed_text = code.partition("str_front")
                code, separator, removed_text = code.partition("str_back")
                code = code.strip() # remove whitespace between code and the original separator/removed_text
                
        #############################################################
        ## NOTE OLD METHOD to remove 'pt.______' type of text from the arguments list. Leave it here so I understand what the small line is doing below. I've move the "replace_these_words" to the print tricks main class so it only runs one time.
        ## Get arguments alone, but include original formatting (newlines, tabs, etc).
        ##   NOTE: BUG PREVENTION: Make sure all letters that need to be removed are replaced before replacing the symbols. Otherwise, we will be creating new words: For example, I was removing the '(' before removing the pt. so what was happening is the code was removing the '(' first and the 'pt(self...)' was becoming 'ptsself...', which it then removed the pts, which means that the s on self was eliminated.
        ##   So: letters first:
        # replace_these_words = (
        #                         'pt.delete',
        #                         'pt.ex',
        #                         'pt.l',
        #                         'pt.prefs',
        #                         'pt.props',
        #                         'pt.properties',
        #                         'pt.p',
        #                         'pt.t',
        #                         'pt.w',
        #                         'dpt',
        #                         'pts',
        #                         'pt',
        #                         '(') ### NOTE '(' must be last and 'pt' must be 2nd to last or else it'll delete the 'pt' in front of anything else that I'm trying to replace and it'll fail to replace it. Like if i did 'pt' in front of 'pt.p', then i'd just end up with '.p' and it'd fail.

        ## NOTE: NEW METHOD to remove words that contrast with the functioning of our code: code is in UTI now.

        ### remove equal sign assignments to any of my print statements, or they would appear in the list of arguments. For example 'c = pt(5)' would become 'pt(c = 5)'
        # ... ###db(code)

        # ... ###db(code)
        # remove_equals = code[code.find('=') + 1:].strip() ## remove any equals signs and an extra white spaces.
        # ... ###db(remove_equals)
        # argsWS = remove_equals  ## NOTE: Must keep this assignment. Don't delete.

        remove_left = (
            NAM.inst_nam + code.split(NAM.inst_nam, 1)[-1]
        )  ## We are removing everything from 'pt' and to the left, then we are adding 'pt' back onto the far left so we have our function on it's own and can find it in the "replace_these_words" dict.
        # ... ###db(remove_left)
        argsWS = remove_left  ## NOTE: Must keep this assignment. Don't delete.

        # ... ###db(NAM.replace_these_words)
        for word in NAM.replace_these_words:
            argsWS = argsWS.replace(word, "", 1)

        ######################################################################

        args_with_specials = "".join(
            argsWS.rsplit(")", 1)
        )  ## remove last occurence of ')'
        # ... ###db(args_with_specials)

        ## remove extra whitespaces, newlines from the args_with_specials
        args_only = " ".join(args_with_specials.splitlines())
        # ... ###db(args_only)

        formatted_args = f"{C.t2}{args_only}{C.er}"  ## This is placed here for everytime there is just one argument
        # ... ###db(formatted_args)

        fmt_args_list = [
            formatted_args,
        ]  ## We need this to start as equal to formatted_args to be used in "for v in range(len(args))" below.
        # print('fmt_args_list: ', fmt_args_list)

        code_unformatted = code  ## not currently being used. But I might want the raw code at some point in the future.
        ## if so, can return this along with the code, args_only, args_with_specials, etc.

        if "\n" in code:
            code = " ".join(code.splitlines())

        if "," in args_only:
            formatted_args = ""
            fmt_args_list = []

            splitArgs = re.split(
                r",\s*(?![^()]*\))", args_only
            )  ## This code only splits comma's that are NOT inside of parenthesis [for cases like "pt('hello', 4*(1,2,3))" where there are two arguments, but one of them has multiple comma's inside]
            splitArgs = [x for x in splitArgs if x]
            for count, s in enumerate(splitArgs):
                # if 'str_front' not in s or 'str_back' not in s:
                s = s.removeprefix(
                    " "
                )  # note, Python 3.9+ only. Consider a backwards compatible equivalent using lambda?
                fmt_args_list.append(s)

                if (
                    count != len(splitArgs) - 1
                ):  ## if our count is NOT at the end of the length of the list, then add it in with a comma and a space afterwards. Else add it without.
                    formatted_args += f"{C.t2}{s}{C.er}, "
                else:
                    formatted_args += f"{C.t2}{s}{C.er}"
            # formatted_args = formatted_args[:-2] ## removing the last comma

        # print(f'specials: {args_with_specials} args_only: {args_only} frmArgs: {formatted_args} fmtAlist: {fmt_args_list}')
        ## --prints:
        ## specials:  'times:',  4*(1,2,3
        ## args_only:  'times:',  4*(1,2,3
        ## frmArgs: 'times:',  4*(1, 2, 3  ## But these are colored
        ## fmtAlist: ["'times:'", ' 4*(1', '2', '3']
        return code, args_with_specials, args_only, formatted_args, fmt_args_list

    def _threadedTimer():
        time.sleep(2)

    def _check_for_bulk_print_time():
        time.sleep(0.5)
        # thisBigBlock = pt.rapid_pt_bulk_print_block

        # pt.rapid_pt_bulk_print_block = ''

        # pt.sent_bulk_print_to_thread = False
        # print(thisBigBlock)

        return

    def _getVarLength(variable, varType, arg=None):
        """We are getting a dynamic length of the variable for all situations where python can't normally get a var
        length at all, or when we want a more helpful length output.

        """
        try:
            var_as_str = str(variable)
        except TypeError as e:
            return '0' ## We are returning the length as 0, because python was unable to get the variable
            

        # print('var as string: ', var_as_str)  # KEEP THESE: For an easier time when I need to add new types to this list
        # print('arg: ', arg)                   # KEEP THESE: For an easier time when I need to add new types to this list
        # print('varType: ', varType)           # KEEP THESE: For an easier time when I need to add new types to this list

        length_var = "N/A"
        if (
            (varType is list or varType is tuple)
            or (varType is set or varType is frozenset)
        ) or (varType is str or varType is dict):
            length_var = len(variable)
        elif varType is int:
            length_var = len(var_as_str)
        elif varType is float:
            wholeNumbers = var_as_str.split(".")[0]
            decimalNumbers = var_as_str.split(".")[1]

            length1 = str(len(wholeNumbers))
            if "-" in wholeNumbers:
                length1 = str((int(length1) - 1))

            if wholeNumbers == "0":
                length1 = "0"
            elif wholeNumbers == "-0":
                length1 = "0"

            if "-" in wholeNumbers:
                length1 = f"-{length1}"

            length2 = str(len(decimalNumbers))
            if decimalNumbers == "0":
                length2 = "0"

            length_var = f"({length1}:{length2})"
        elif varType is bool:
            # length_var = 1
            # if '==' in arg: ## We check the arguments, not the variable, because any number of bool checks will all return as just either true or false
            num_equal = arg.count("==")
            num_greater = arg.count(">")
            num_less = arg.count("<")
            # numChecks =
            length_var = str(
                num_equal + num_greater + num_less + 1
            )  ## + 1 because var1==var2==var3 would have 2 =='s but 3 elements. And no signs, but still a bool, means still has 1.
        elif varType == type(UTI._info) or varType == type(
            UTI
        ):  ## simple check for type "function/class". Can use any other function to test this here.
            try:
                length_var = (
                    len(inspect.getsourcelines(variable)[0]) - 1
                )  # we subtract 1 because I don't want to count the length of the function name itself.
            except:
                length_var = 0
        elif varType is memoryview:
            ## NOTE, I'm not sure the best way to "calculate" this right now... I don't know if running my
            ## pt.size() or UTI._bytes_size() on this would make sense.
            length_var = str(len(var_as_str))
        elif varType == complex:
            var_as_str = var_as_str.replace("(", "").replace(")", "")
            split_var = var_as_str.split("+")
            firstNums = split_var[0]
            secondNums = split_var[1]

            length1 = str(len(firstNums))
            if "-" in firstNums:
                length1 = str((int(length1) - 1))
            if firstNums == "0":
                length1 = "0"

            length2 = str(len(secondNums))
            if secondNums == "0":
                length2 = "0"

            length_var = f"({length1}:{length2})"

        elif varType == type(None):
            length_var = "N/A"

        elif varType == bytes:
            length_var = (
                len(var_as_str) - 3
            )  ## -3 because we don't want to count each of the quotes or the 'b'
            length_var = "~" + str(
                length_var
            )  ## NOTE I'm not sure the most accurate way to gauge these, so I'm
            ## guessing this is correct and adding the ~ to let that be known.
        elif varType == bytearray:
            length_var = (
                len(var_as_str) - 14
            )  ## -3 because we don't want to count each of the quotes or the b or the 'bytearray()'
            length_var = "~" + str(
                length_var
            )  ## NOTE I'm not sure the most accurate way to gauge these, so I'm
            ## guessing this is correct and adding the ~ to let that be known.
        else:
            ## look for datatype with a bunch of strings
            if "' " in var_as_str:
                numQuotes = var_as_str.count("' ")
                length_var = str(numQuotes + 1)
                length_var = (
                    "~" + length_var
                )  ## We get the number of [quotes with a space], to get just the last quote of each item (like in a numpy array), then ADD 1 for the last element on the list.
            ## look for dictionary-like datatype
            elif ":" in var_as_str:
                numColons = var_as_str.count(
                    ":"
                )  ## number of colons = number of dict-like elements
                length_var = str(numColons)
                length_var = "~" + length_var
            ## look for normal Numpy-like arrays
            elif " " in var_as_str:
                numSpaces = var_as_str.count(" ")
                length_var = str(numSpaces + 1)
                length_var = (
                    "~" + length_var
                )  ## We get the number of spaces, then ADD 1 to get the last element on the list
            else:
                length_var = len(var_as_str)
                length_var = "~" + str(length_var)

        ## catch-all to make all length_var's into strings. This probably isn't necessary because I am using f-strings, but I'm just trying to make everything consistent. Currently, only complex and float return strings by default, while others return ints. Of course, I could return complex/floats as a float for a length via: varFloatLen = float(f'{length1}.{length2}')
        length_var = str(length_var)
        return length_var

    def _setVarColor(varType):
        """_setVarColor - set var colors
        - Basics:

            - Color Default Assignments:

                - Colors only:
                    - arguments:     (Blue)
                    - variables:     (Yellow) - Generic vars that aren't specifically assigned a color (below)
                    - Strings:  (Pink)
                    - Integers: (red)
                    - Floats:   (green)
                    - Booleans: (white_bright)
                    - complex:  (generic var color)

                - Bold & underline and colors:
                    - bytes                 (pink, underline)
                    - bytesArray            (pink, underline, BOLD) - ## bytesarray are immutable, thus bold
                    - list:                 (white_bright, underline)
                    - tuple:                (white_bright, underline, BOLD) ## tuple are immutable, thus bold
                    - dict:                 (green, underline)
                    - set:                  (red, underline)
                    - frozenSet:            (red, underline, BOLD)  ## frozenSet are immutable, thus bold

                - Background colors only (no other text effects):
                    - Functions & classes:
                    - MemoryView Objects:

                - Dark Theme color conversions:
                    - Blue = Yellow
                    - Yellow = Blue
                    - Pink = Green
                    - Red = Cyan
                    - Green = Purple
        """

        C.t3 = (
            C.Fore_BLUE
        )  ## Resetting the color to default, generic color, in-between prints

        ## Just Colors:
        if varType is str:
            C.t3 = C.Fore_GREEN + C.Effect_BOLD
        elif varType is int:
            C.t3 = C.Fore_CYAN + C.Effect_BOLD
        elif varType is float:
            C.t3 = C.Fore_PURPLE + C.Effect_BOLD
        elif varType is bool:
            C.t3 = C.Fore_WHITE_BRIGHT

        ## Bold & Underline & Colors:
        elif varType is bytes:
            C.t3 = C.Fore_GREEN + C.Effect_UNDERLINE
        elif varType is bytearray:
            C.t3 = C.Fore_GREEN + C.Effect_UNDERLINE + C.Effect_BOLD
        elif varType is list:
            C.t3 = C.Fore_WHITE_BRIGHT + C.Effect_UNDERLINE
        elif varType is tuple:
            C.t3 = C.Fore_WHITE_BRIGHT + C.Effect_UNDERLINE + C.Effect_BOLD
        elif varType is dict:
            C.t3 = C.Fore_PURPLE + C.Effect_UNDERLINE
        elif varType is set:
            C.t3 = C.Fore_CYAN + C.Effect_UNDERLINE
        elif varType is frozenset:
            C.t3 = C.Fore_CYAN + C.Effect_UNDERLINE + C.Effect_BOLD

        ## Background Colors Only (No other text effects):
        elif varType is type(UTI._info):
            C.t3 = C.Back_PURPLE + C.Effect_UNDERLINE
        elif varType is type(UTI):
            C.t3 = C.Back_PURPLE + C.Effect_UNDERLINE
        elif varType is memoryview:
            C.t3 = C.Back_CYAN + C.Effect_UNDERLINE

    # def _evalFromOther(x=None, statement):
    def _evalFromOther(statement):
        """Goals:
            - Determine that this statement links to a function in the other file
            - Retrieve the code of the function in the other file
            - Run this code as if it was actually still in the other file.
        Secondary Goals:
        -    Return the result to the other file (if applicable).

        """
        g = eval(statement)
        ... ###db(g)
        ... ###db("inside eval")
        if callable(statement):
            variable = inspect.getsource(variable)
            var_as_str = str(variable)
            ... ###db(var_as_str)
            isCallable = True

    def _evalFromOther2(pt, statement):
        if callable(statement):
            variable = inspect.getsource(variable)
            var_as_str = str(variable)
            ... ###db(var_as_str)
            isCallable = True

    def _evalFromOther3(statement):
        pass

    def _process_large_vars(variable, varType, length_var):
        """A quick check to see if this is a very large variable.
        - If it's larger:
            - pt processes of byteSize will take longer than normal
            - python's print() statement will take SIGNIFICANTLY LONGER.
        - To correct if longer:
            - Find out how much to reduce the size by:
                - Find the average str length of the first 4 elements of the var.
                - calculate 500 lines of data (approximately 100(??) characters per line), so maybe string can be max 50,000 length.
                - Get the likely num of elements that would cover that 50,000 length.
                - This is now the "num_of_divisions_from_original"

            - We take just the first _n_ elements of the var and send those to processing.
            - We get:
                - The num_of_divisions_from_original, which is the "1000,000 / 2,000" = 500.
                - the reduced_size_q = True

        - For processing bytesize (not processed in this method):
            - "if reduced_size_q = True:
                    bytesize *= num_of_divisions_from_original"

        - If not longer:
            - Quickly exit and return:
                - the variable,
                - "reduced_size_q = False
                - num_of_divisions_from_original = 0,
        -

        """
        # if varType is int or varType is float:
        #     length_var = len(str(variable))
        # elif varType == type(UTI._info): ## simple check for type "function". Can use any other function to test this here.
        #     length_var = len(str(variable))
        # else:
        #     try:
        #         length_var = len(variable)
        #     except:
        #         # pt.e()
        #         length_var = 0

        try:
            length_var = int(length_var)
        except:
            length_var = 0
        # Default values in case no truncation is needed
        argVarShortened = variable
        wasShortened = False
        reduceBy = 0  # Default value indicating no reduction
        numItems_to_get = 10  # Example truncation length for simplicity

        # Handle different types accordingly
        if isinstance(variable, (int, float)):
            # Convert to string and truncate if necessary
            variable_str = str(variable)
            if len(variable_str) > numItems_to_get:
                argVarShortened = variable_str[:numItems_to_get] + "..."
                wasShortened = True
                reduceBy = len(variable_str) / numItems_to_get
        elif isinstance(variable, str):
            # Truncate string directly
            if len(variable) > numItems_to_get:
                argVarShortened = variable[:numItems_to_get] + "..."
                wasShortened = True
                reduceBy = len(variable) / numItems_to_get
        elif isinstance(variable, (list, dict, set, tuple)):
            # For iterables, convert to their string representation and then truncate
            variable_str = str(variable)
            if len(variable_str) > numItems_to_get:
                argVarShortened = variable_str[:numItems_to_get] + "..."
                wasShortened = True
                reduceBy = len(variable_str) / numItems_to_get

        # Add more type checks if needed for other specific types

        return argVarShortened, wasShortened, reduceBy

    def _track_pt_on_one_line(code, count_pt):
        """Track pt on one line:
        - if this has never been run before, skip it, because we will just pull out the first pt statements' argument values anyways and the rest will be ignored by default.
        - If this has been ran before, then we walk through each pt statement on each line, looking for the right one.

        """
        ## Replace semicolons that separate out statements with a unique character, because we want to get rid of any semi colons
        ##   within a variable (like in a string)
        ## first: remove from between double quotes ""
        modified_code = re.sub(r'"[^"]*"', lambda x: x.group().replace(';', '\x00'), code)
        ## second: remove from between single quotes ''
        modified_code = re.sub(r"'[^']*'", lambda x: x.group().replace(';', '\x00'), modified_code)
        # ... ###db(modified_code)

        ## Get all of the pt methods and args, everything after pt
        pattern = re.compile(fr'{NAM.inst_nam}(\s*\(\S*?\)|(?:[a-zA-Z0-9_\.\s]*\(\S*?\)))')
        filtered_code_list = pattern.findall(modified_code)
        # ... ###db(filtered_code_list)
        
        ## combine these with 'pt' to get the complete, original pt() or pt._() call. 
        statements = ["pt" + call for call in filtered_code_list]
        # ... ###db(statements)
        
        if len(statements) <=1:
            return code
        else: 
            ## First line in the multi-line statement
            if pt.is_multi_pt_in_one_line == False:
                pt.is_multi_pt_in_one_line = True
                pt.current_pt_on_multi_line = 0
                
            ## Subsequent lines in multi_line statement
            else:  
                pt.current_pt_on_multi_line += 1

            statement = statements[pt.current_pt_on_multi_line]
            statement = statement.replace('\x00', ';')
            # ... ###db(statement, count_pt, pt.current_pt_on_multi_line)

            if (
                count_pt - 1 == pt.current_pt_on_multi_line
            ):  ## we do -1 because to match up the counting of the variables and 
                    ##  our position (because position starts at 0 instead of 1).
                pt.is_multi_pt_in_one_line = False
            return statement
            
    def _count_num_pt_statements(code):
        apt = code.count("pt(")
        bpt = code.count("pt.")
        totCount = apt + bpt
        return totCount

    def _error_trace_simple():
        _error_trace_simple = traceback.format_exception(*sys.exc_info())[-2:]
        location_and_culprit = _error_trace_simple[0]
        splitThem = location_and_culprit.split("\n ")
        culprit = splitThem[1]
        culprit = culprit.strip().replace("\n", "")

        error_type = _error_trace_simple[1]
        error_type = error_type.replace("\n", "")

        return culprit, error_type

    def _error_trace_full():
        exc_info = sys.exc_info()[0]
        _error_trace_fullback = traceback.extract_stack()[:-1]

        ### if there is an exception, del this function (_error_trace_full), so it doesn't show up
        if exc_info is not None:
            del _error_trace_fullback[-1]

        tracebackStatement = "Traceback (most recent call last): \n"
        _error_trace_fullStr = tracebackStatement + "".join(
            traceback.format_list(_error_trace_fullback)
        )

        ### if there is an exception, add our full traceback statement with the _error_trace_full
        if exc_info is not None:
            _error_trace_fullStr += "  " + traceback.format_exc().lstrip(
                tracebackStatement
            )
        return _error_trace_fullStr

    def _enableColors_simple():
        """Note, I have enable/disable color functions in both UTI and C... Not sure why I want both..."""
        C.er = C.Effect_RESET
        C.t1 = C.Fore_GREEN  ### Strings
        C.t2 = C.Fore_YELLOW  ### Variables
        C.t3 = C.Fore_BLUE  ### Values
        C.t4 = C.Fore_CYAN

    def _disableColors_simple():
        """Note, I have enable/disable color functions in both UTI and C... Not sure why I want both..."""
        C.er = ""
        C.t1 = ""  ### Strings
        C.t2 = ""  ### Variables
        C.t3 = ""  ### Values
        C.t4 = ""

    def _automaticallyFixPrints():
        print("_automaticallyFixPrints")

        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no


        num_instances = 0
        with open(file_path) as f:
            for line in f:
                if "pt(" in line or "print(" in line:
                    pass
                elif "pt " in line and not line.endswith(")"):
                    print(line)
                # 'print' in line:
                # num_inst_this_line = line.count(delete_what)
                # num_instances +=num_inst_this_line ### We are saying to count how many instances show up on the line and add them to the current num_instances
        f.close()

    ##### _timerWrapped Funcs and other Code-wrapping types.
    def _timerWrapped():
        """For wrapping functions inside a pt.t statement like this: pt.t(function())
            - How to:
        - pt.t checks if it's a function.
        - if so, sends to UTI._timerWrapped()
        - _timerWrapped then:
            - calls pt.t,
            - then runs the function using eval?
            - then calls pt.t to end it
            - then prints and returns the results
        """

    def _tWrapTest(passedFunc):
        """
        - _timerWrapped (test A - exec code):
            - We write _timerWrapped(func(x)) in testFile.
                - funcX will run as normal, but then we will be inside of _timerWrapped.
                - print_tricks processing:
                    - import the file that _timerWrapped was called in.
                    - Access it's global variables for that namesspace (the imported file's namespace),
                    - Get the function definition/code of the func that timeWrapped called.
                    - Dynamically run this:
                        | pt.t('a')
                        | for i in range(numLoops)
                            exec(funcCode, importedGlobals)
                        | timeTaken = pt.t('a')
                        | return timeTaken
                    - Now we subtract the first 'a' from the last, then divide
        - New:
            - I just need to be able to set the namespace to the other module.
            Find a function online that will allow me to set the namespace or change the namespace.
                - I can then "inject" whatever code I want into the other file, at the location that I want. So basically, I'll be
                injecting my code just after their call of pt.timerWrap(func(x)), and my code will just be a copy of theirs but
                with my pt.t() statements before and after it, and a for loop, whether this is actually part of the injected code
                or this code lies just before and after the exec() statements within the def timerWrap
        - Running as a string:
            - if the user wraps their code to call their func within my pt.timerWrap() statement, then it'll run it as normal, and then
            mine will run a second time (or as many times as specified). Which means that their timing will be less accurate as their code
            is running twice now (and might have repeated print statements etc).
            - But if the user instead puts their call as a string, then my code can run indpendently of their code.... however, wouldn't
            this still take up the extra time, so I'm not sure if it's worth it. But it's probably safer overall to run it as a string, but
            I also like the idea of trying to allow it as a straight up passed function.
                - Or... what if.. I had it called just like you call threading.thread with the args passed separately from the
                assignment. So it'd look like this: pt.timerWrap(func, args=x). So now their function wouldn't be called here, but
                would rather be called inside of my timerWrap code whenever I was ready to do it.
                    - This would be very similar to the idea of just placing the "func(x)" in a string though, and I think maybe a lot more
                    straightforward. And..
                    It would also allow me to run the code just once, and still get them a return value on their code. So perhaps
                    passing as a string truly is the best approach, for easines to understand, good returns, control over the code
                    etc. NOTE: As stated above, Passing as a string should probably be the best default behavior for now.

        """
        print("\n")
        ... ###db("_tWrapTest")
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        # ... ###db(file_name)
        file_name = file_name.replace(".py", "")

        # code = f'''import {file_name}\nprint({file_name}.var_in_quick_tests);print({file_name}.x);print({file_name}.cl.func_cl.gg)'''
        # code = (f'from {file_name} import *\n'
        # f'print(var_in_quick_tests);print(x);print(cl.func_cl.gg)')
        code = f"""from {file_name} import *;... ###db(var_in_quick_tests);... ###db(x);# ... ###db(f_param);gg = 33;... ###db(gg)"""
        # pt.c("\ncode:")
        # print(code)
        # fn_globs = file_name+'__globals__'
        # print(fn_globs)
        # exec (code, file_name.globals())
        pt.c("exec: ", color=[C.t1, C.by, C.eu])
        exec(code)

    def _tWrapTest_E_wt0(passedFunc):
        """NOTE ON CALLERS INSIDE OF FUNCTIONS:
        - If the function code that I have gathered calls other functions/modules within it... how could this be handled?
            - If it had imports, I'd have to also call the imports into this namespace.
            - If it was just another function, I'd have to search for ALL code within that function code and separate out the args, get the
            func all by itself, find the vars that pass to it, and then run that code as well... So basically I'd be not only recreating the
            procedure that I used to build the first function, but do this __ number of times (automatically), but I'd basically be creating
            a customized, re-done version of their entire app/codebase (potentially).
                - Although there are likely many benefits to this (like finding optimum code, finding code that's never ran/touched),
                I doubt it'd be better than some of the other techniques I can use:
                    - Probably better methods:
                        - 1 - running an import code that analyzes the code, looking for the statements, and then builds another file on top and
                        runs that one instead
                        - 2 - Running this code but doing so in the other namespace somehow. (probably the easiest by far).
        """
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        dir_only = os.path.split(file_path)[0]
        file_name = file_name.replace(".py", "")
        # sys.path.append(dir_only)
        # ... ###db(passedFunc)

        caller_globals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_globals"]
        ... ###db(caller_globals)
        if "(" in passedFunc and ")" in passedFunc:
            args_only = re.compile(r"\((.*?)\).*$").search(passedFunc).groups()[0]
            # ... ###db(args_only)
            justFunc = passedFunc.replace(args_only, "")
            func_nameOnly = justFunc.replace("(", "").replace(")", "")
            sourceFuncCode = caller_globals[func_nameOnly]
            # ... ###db(args_only, justFunc, func_nameOnly, sourceFuncCode)
            args_only = args_only.replace("'", "").replace('"', "")
            # ... ###db(args_only)
            if callable(sourceFuncCode):
                sourceFuncCode_as_str = str(inspect.getsource(sourceFuncCode))
                # print(sourceFuncCode_as_str)

            argList = []
            if "," in args_only:
                splitArgs = args_only.split(",")
                for arg in splitArgs:
                    arg = arg.removeprefix(" ")
                    argList.append(arg)
                # ... ###db(splitArgs, argList)
            else:
                # ... ###db('else')
                argList = args_only
        # ... ###db(argList)
        varAssignments = {}
        codeStr = ""
        for arg in argList:
            # ... ###db(1)
            if arg in caller_globals:
                # ... ###db('1a')
                varAssignments[arg] = repr(caller_globals[arg])
                # ... ###db(f'{arg} = {caller_globals[arg]}')
                ... ###db(f"{varAssignments[arg]}")

            assignmentsAsString = ""
            for k, v in varAssignments.items():
                assignmentsAsString += f"{k} = {v}\n"
                codeStr = assignmentsAsString
        codeStr += sourceFuncCode_as_str
        # codeStr = sourceFuncCode.append(f'\n{justFunc}({args_only})')
        codeStr += f"\n{func_nameOnly}({args_only})"
        # ... ###db(codeStr)
        # print('codeStr:\n', codeStr)
        pt.c(
            "=-=-=-=-=-==-=-=-=-=-=-==-=-=-=--=\nEXECUTING CODE:\n=-=-=-=-=-==-=-=-=-=-=-==-=-=-=--="
        )
        pt.cur_exec_str = codeStr  ## always assign the codestring to the class var, just before executing it.
        exec(codeStr)
        pt.ex()

        # caller_locals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_locals"]
        # # ... ###db(caller_locals)

    def _tWrapTest_E_wt0_old(passedFunc):
        """NOTE ON CALLERS INSIDE OF FUNCTIONS:
        - If the function code that I have gathered calls other functions/modules within it... how could this be handled?
            - If it had imports, I'd have to also call the imports into this namespace.
            - If it was just another function, I'd have to search for ALL code within that function code and separate out the args, get the
            func all by itself, find the vars that pass to it, and then run that code as well... So basically I'd be not only recreating the
            procedure that I used to build the first function, but do this __ number of times (automatically), but I'd basically be creating
            a customized, re-done version of their entire app/codebase (potentially).
                - Although there are likely many benefits to this (like finding optimum code, finding code that's never ran/touched),
                I doubt it'd be better than some of the other techniques I can use:
                    - Probably better methods:
                        - 1 - running an import code that analyzes the code, looking for the statements, and then builds another file on top and
                        runs that one instead
                        - 2 - Running this code but doing so in the other namespace somehow. (probably the easiest by far).
        """
        (
            file_name,
            file_path,
            line_no,
            func_name,
            func_name_fmt,
            code,
            args_with_specials,
            args_only,
            formatted_args,
            fmt_args_list,
        ) = UTI._simple_trace()
        line_no = f'{line_no}.{pt.current_pt_on_multi_line + 1}' if pt.current_pt_on_multi_line != 0 else line_no

        dir_only = os.path.split(file_path)[0]
        file_name = file_name.replace(".py", "")
        # sys.path.append(dir_only)
        # ... ###db(passedFunc)

        caller_globals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_globals"]

        if "(" in passedFunc and ")" in passedFunc:
            args_only = re.compile(r"\((.*?)\).*$").search(passedFunc).groups()[0]
            justFunc = passedFunc.replace(args_only, "")
            func_nameOnly = justFunc.replace("(", "").replace(")", "")
            sourceFuncCode = caller_globals[func_nameOnly]
            args_only = args_only.replace("'", "").replace('"', "")
            # ... ###db(args_only, justFunc, func_nameOnly, sourceFuncCode)
            if callable(sourceFuncCode):
                sourceFuncCode_as_str = str(inspect.getsource(sourceFuncCode))
                # print(sourceFuncCode_as_str)

            argList = []
            if "," in args_only:
                splitArgs = args_only.split(",")
                for arg in splitArgs:
                    arg = arg.removeprefix(" ")
                    argList.append(arg)
                # ... ###db(splitArgs, argList)
            else:
                argList = args_only

        varAssignments = {}
        for arg in argList:
            if arg in caller_globals:
                varAssignments[arg] = caller_globals[arg]
                # ... ###db(f'{arg} = {caller_globals[arg]}')

        assignmentsAsString = ""
        for k, v in varAssignments.items():
            assignmentsAsString += f"{k} = '{v}'\n"
        codeStr = assignmentsAsString + sourceFuncCode_as_str
        # codeStr = sourceFuncCode.append(f'\n{justFunc}({args_only})')
        codeStr = codeStr + f"\n{func_nameOnly}({args_only})"
        # ... ###db(codeStr)
        # print('codeStr:\n', codeStr)
        pt.c(
            "=-=-=-=-=-==-=-=-=-=-=-==-=-=-=--=\nEXECUTING CODE:\n=-=-=-=-=-==-=-=-=-=-=-==-=-=-=--="
        )
        pt.cur_exec_str = codeStr  ## always assign the codestring to the class var, just before executing it.
        exec(codeStr)
        pt.ex()

        caller_locals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_locals"]
        # ... ###db(caller_locals)

    def _get_func_data_from_module_wt1(callerGlobs, passedFunc):
        pass

    ##### Random Pattern utility functions (almost all functionality found here, but the public access point is found in pt class)
    def _xpg_Pattern_gap(numSeconds=40):
        """temporary function. This should eventually merge with pt.x to generate this data dynamically, based on the values that I give to pt.x.
        but for now, just do this manually, simulating the rise and fall of coins.

        """

        seconds = [i for i in range(numSeconds)]
        valuesEachSec = []
        trendUp = False
        trendDn = False
        trendUp = True
        # trendDn = True
        trend_increment = 0.01
        trend_inc_min = 0.00001
        trend_inc_max = 0.01
        minF = -0.1
        maxF = 0.1
        # minF = 0.
        # maxF = 1.
        for i in range(numSeconds):
            # trend_inc_min = .01
            # trend_inc_max = .01
            trend_increment = ra.uniform(trend_inc_min, trend_inc_max)
            if trendUp == True:
                minF += trend_increment
                maxF += trend_increment

            elif trendDn == True:
                minF -= trend_increment
                maxF -= trend_increment

            mFlt = ra.uniform(minF, maxF)
            ... ###db(mFlt)
            mFlt = pow(7, mFlt)
            ... ###db(mFlt)
            # mFlt2 = ra.uniform(minF, maxF)
            # mFlt = (mFlt - mFlt2)*trend_increment
            valuesEachSec.append(mFlt)

        p = multiprocessing.Process(
            target=UTI._displayPlot,
            args=(
                seconds,
                valuesEachSec,
            ),
        )
        # jobs.append(p)
        p.start()
        # threading.Thread(target=UTI._displayPlot, args=(seconds, valuesEachSec,)).start()

        # UTI._displayPlot(seconds, valuesEachSec)

    def _displayPlot(x, y):
        import matplotlib.pyplot as plt

        plt.style.use("seaborn-whitegrid")
        # import numpy as np
        fig = plt.figure()
        ax = plt.axes()
        # x = np.linspace(0, 10, 1000)
        ax.plot(x, y)
        plt.show()
        # pt.p()

    def _x_generateStrings(numStrings=1, prefix="", suffix=""):
        # if suffixType == 'rand':
        listOfStrings = []
        for s in range(numStrings):
            listOfStrings.append(f"{prefix}_{s}{suffix}")
            # if suffixType == 'rand':
            #     suffix = random.randint(0, 9)
            # else:
            #     suffix += 1
        # prefix + str(random.randint(0, mid)) + suffix
        return listOfStrings

    def _x_createDict(**kwargs):
        """
        Creates a dictionary from the passed in keyword arguments.
        """

        newDict = {}
        for key, value in kwargs.items():
            newDict[key] = value
        return newDict

    def _x_type_collection(type):
        if type == "list":
            return list
        elif type == "tuple":
            return tuple
        elif type == "set":
            return set
        elif type == "dict":
            return dict
        # elif

        pass

    ##### Helper UTI funcs for Modify File Here
    def _duplicate_orig_info(from_file, to_file):
        """
        This function duplicates the stats and ownership information from the original file.
        """
        shutil.copystat(from_file, to_file)

        st = os.stat(from_file)
        if hasattr(os, "chown"):
            try:
                os.chown(to_file, st.st_uid, st.st_gid)
            except IOError:
                os.chown(to_file, -1, st.st_gid)

    def _try_delete_file(path):
        """
        Try to delete the file at ``path``.  If the file doesn't exist, do nothing;
        any other errors are propagated to the caller.
        """
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass

    def _speed_test_for_traceback():
        # fast test speed test speed fast speed
        '''
        Tests:
        - traceback extract stack, inspect stack, current_frame, and sys._getframe for speed. 
        - So I know which I can use for my frame retrieval purposes

        NOTE I stopped calling time_inspect_stack/inspect.stack() because it is 
        10x slower than traceback.extract_stack and 1000x slower than the other two. 
        It gets all of the globals, locals, and other info that take a lot of processing. 
        
        NOTE: another comparison:
            10x faster:
                'code = linecache.getline(current_file, line_number).strip()'
            10x slower:
                'code = inspect.getsource(frame)'
        
        NOTE: All functions starting with "st_" are all part of the same attempt to time
            the speed of using the settrace module, but I can't get it to print anything
            quite yet. 
            
            '''
        import timeit

        global print_data
        global num_runs
        print_data = False 
        # print_data = True
        num_runs = 1000

        def time_inspect_stack():
            ''' 10x slower than extract_stack and 1000x slower than sys.getframe etc.'''
            frame = inspect.stack()[-1]
            current_file = frame.filename
            line_number = frame.lineno
            func_name = frame.function
            # code = inspect.getsource(frame[0])
            code = linecache.getline(current_file, line_number).strip()

            global print_data 
            if print_data: 
                pt(current_file, line_number, func_name, code)
            return current_file, line_number, func_name, code

        def inspect_get_outer_frames():
            '''can't get this to work '''
            outerframes = inspect.getouterframes(inspect.currentframe())
            caller_frame = outerframes[0] 
            frame, current_file, line_number, func_name, lines, index = caller_frame
            code = lines[index].strip()
            
            global print_data 
            if print_data: 
                pt(current_file, line_number, func_name, code)
            return current_file, line_number, func_name, code
        
        def st_tracefunc(frame, event, arg):
            '''can't get this to work '''
            def trace_calls(frame, event, arg):
                if event == "call":
                    current_file = frame.f_code.co_filename
                    line_number = frame.f_lineno
                    func_name = frame.f_code.co_name
                    code = linecache.getline(current_file, line_number).strip()
                    print(f"File: {current_file}, Line: {line_number}, Function: {func_name}, Code: {code}")
                    return trace_calls
            return trace_calls

        def st_time_sys_settrace():
            print("Setting trace function...")
            sys.settrace(st_tracefunc)
            print("Calling st_function_with_calls()...")
            st_function_with_calls()
            print("Finished calling st_function_with_calls()")
            sys.settrace(None)

        def st_function_with_calls():
            st_dummy_function()
            st_another_dummy_function()

        def st_dummy_function():
            pass

        def st_another_dummy_function():
            pass
        
        def st_get_frame_info():
            caller_frame = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_back  # Adjusted to match your depth
            frame_info = inspect.getframeinfo(caller_frame)
            current_file = frame_info.filename
            line_number = frame_info.lineno
            func_name = frame_info.function
            code = frame_info.code_context[frame_info.index].strip()
            global print_data 
            if print_data: 
                pt(current_file, line_number, func_name, code)
            return current_file, line_number, func_name, code

        def time_traceback_extract_stack():
            stack = traceback.extract_stack()
            frame = stack[-7]
            current_file = frame.filename
            line_number = frame.lineno
            func_name = frame.name
            code = frame.line

            global print_data 
            if print_data: 
                pt(current_file, line_number, func_name, code)
            return current_file, line_number, func_name, code

        def time_inspect_current_frame():
            frame = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_back
            current_file = frame.f_code.co_filename
            line_number = frame.f_lineno
            func_name = frame.f_code.co_name
            # code = inspect.getsource(frame)
            code = linecache.getline(current_file, line_number).strip()

            global print_data 
            if print_data: 
                pt(current_file, line_number, func_name, code)
            return current_file, line_number, func_name, code
        
        def time_sys_getframe():
            frame = sys._getframe().f_back.f_back.f_back.f_back.f_back.f_back
            current_file = frame.f_code.co_filename
            line_number = frame.f_lineno
            func_name = frame.f_code.co_name
            # code = inspect.getsource(frame)
            code = linecache.getline(current_file, line_number).strip()

            global print_data 
            if print_data: 
                pt(current_file, line_number, func_name, code)
            return current_file, line_number, func_name, code

        def run_functions():
            global num_runs

            # inspect_stack_result = timeit.timeit(time_inspect_stack, number=num_runs) * 1000 #* 1000 for 'ms'
            # inspect_get_outer_frames_result = timeit.timeit(inspect_get_outer_frames, number=num_runs) * 1000
            # sys_settrace_result = timeit.timeit(st_time_sys_settrace, number=num_runs) * 1000
            st_get_frame_info_result = timeit.timeit(st_get_frame_info, number=num_runs) * 1000
            traceback_extract_stack_result = timeit.timeit(time_traceback_extract_stack, number=num_runs) * 1000
            inspect_current_frame_result = timeit.timeit(time_inspect_current_frame, number=num_runs) * 1000
            sys_getframe_result = timeit.timeit(time_sys_getframe, number=num_runs) * 1000
            
            fastest_function = min(
                # inspect_stack_result, 
                # inspect_get_outer_frames_result, 
                # sys_settrace_result,
                inspect_current_frame_result, 
                traceback_extract_stack_result, 
                sys_getframe_result, 
                st_get_frame_info_result, 
            )

            # ratio_inspect_stack = time_inspect_stack_result / fastest_function
            # ratio_inspect_get_outer_frames = inspect_get_outer_frames_result / fastest_function
            # ratio_sys_settrace = sys_settrace_result / fastest_function
            ratio_st_get_frame_info = st_get_frame_info_result / fastest_function
            ratio_traceback_extract_stack = traceback_extract_stack_result / fastest_function
            ratio_inspect_current_frame = inspect_current_frame_result / fastest_function
            ratio_sys_getframe = sys_getframe_result / fastest_function

            # Define the precision variables
            precision = ".7f"

            results = [
                # ("sys_settrace", f"{sys_settrace_result:{precision}}", f"{ratio_sys_settrace:{precision}}"),
                ("st_get_frame_info", f"{st_get_frame_info_result:{precision}}", f"{ratio_st_get_frame_info:{precision}}"),
                ("traceback_extract_stack", f"{traceback_extract_stack_result:{precision}}", f"{ratio_traceback_extract_stack:{precision}}"),
                ("inspect_current_frame", f"{inspect_current_frame_result:{precision}}", f"{ratio_inspect_current_frame:{precision}}"),
                ("sys_getframe", f"{sys_getframe_result:{precision}}", f"{ratio_sys_getframe:{precision}}")
            ]
            results.sort(key=lambda x: x[2])
            # results = [f"{result[0]}={result[1]}, {result[2]=}" for result in results]

            pt(results)


        run_functions()

class NAM:
    ''' NAM = "name, this is a class to specify the class names used for pt/p etc. '''
    
    inst_nam = 'pt' ## default instance name user wants to use in their apps. 
    error_start = f'{C.t2}Error: Incorrect importing of print_tricks: " {C.t1}{import_line}{C.er}\n'
    error_end =   (
        f"{C.t1}'from print_tricks import pt'{C.er} and then use\n"
        f"all lowercase for the pt statement like this:\n"
        f"{C.t1}pt()'{C.er}. This is to ensure that pt statements are\n"
        f"written as fast as possible. You can also use the\n"
        f"optional 'p' statements instead to save more typing\n"
        f"time: {C.t1}'from print_tricks import p'{C.er}... {C.t1}p(){C.er}\n")
    
    # ... ###db(import_line)
    match import_line:
        ## if importing as something else
        case line if statements[0] in line or statements[1] in line:
            inst_nam = import_line.split("as")[1].lstrip()

        ## importing as either pt or p
        case line if statements[2] in line:
            inst_nam = 'pt'
        case line if statements[3] in line:
            inst_nam = 'p'
        
        ## Any other import (give them error message)
        case line if statements[4] in line:
            print(error_start,
                "It's designed to be used like this:\n",
                error_end
            )
            raise Exception("Try importing print tricks like this: from print_tricks import pt")
        case line if statements[5] in line:
            print(error_start, 
                "It's designed to be used like this:\n",
                error_end
            )
            raise Exception("Try importing print tricks like this: from print_tricks import pt")
        case line if statements[6] in line:
            print(error_start, 
                f"You've used capital letters for 'pt'.\n",
                f"Instead use all lowercase like this:\n",
                error_end
            )
            raise Exception("Try importing print tricks like this: from print_tricks import pt")

    # ... ###db.c('===========================')
    # attributes_dict = vars(pt)
    # ... ###db(attributes_dict)
    
    # ... ###db.c('===========================')
    attributes_dict = dir(pt)
    # ... ###db(attributes_dict)
    # ... ###db.ex()
    func_keys = [key for key in attributes_dict if callable(getattr(pt, key))]
    func_keys.sort(reverse=True)

    replace_these_words = []
    for word in func_keys:
        replace_these_words.append(f'{inst_nam}.{word}(')

    # Adding more words to remove, but specifically at the end on purpose (especially 'pt' and '(' )
    replace_these_words.extend([inst_nam, "("])




############### Modify File Here  ##########################
class Modify_This_File_Here:
    """
    modify this file here modify file here

    Parameters:

        - open_as_bytes=False
            =False:
                File is opened as a string (text documents)
            ='b':
                File is opened as "Bytes" (useful for non-text data like images, audio, video,
                exe files, etc.)

        - backup=None
            Backup original file to this path (optional):

        - open_now=True
            =True:
                Open now
            =False:
                Don't open. Wait for user to open it themsevles.

        - kwargs: Additional keyword arguments to pass to `open()`
    """

    UNOPENED = 0
    OPEN = 1
    CLOSED = 2

    def __init__(
        self, name, open_as_bytes=False, backup=None, open_now=False, **kwargs
    ):
        self.name = os.fsdecode(name)
        self.open_as_bytes = open_as_bytes
        self.file_path = os.path.join(os.getcwd(), self.name)
        self.backuppath = (
            os.path.join(os.getcwd(), os.fsdecode(backup)) if backup else None
        )
        self.kwargs = kwargs
        self.input = self.output = self._tmppath = None
        self._state = self.UNOPENED
        if open_now:
            self.open()

    def __enter__(self):
        if self._state < self.OPEN:
            self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rollback() if exc_type is not None and self._state == self.OPEN else self.close()
        return False

    def _mktemp(self, file_path):
        tmppath = Path(file_path).parent / "._temp_pt-"
        return str(tmppath.resolve().with_suffix(""))

    def open(self):
        if self._state >= self.OPEN:
            raise ValueError("open() called twice on same filehandle")

        self._state = self.OPEN
        self.realpath = os.path.realpath(self.file_path)

        try:
            self._tmppath = self._mktemp(self.realpath)
            self.output = self.open_write(self._tmppath)
            UTI._duplicate_orig_info(self.realpath, self._tmppath)
            self.input = self.open_read(self.realpath)
        except Exception:
            self.rollback()
            raise

    def open_read(self, path):
        mode = "rb" if self.open_as_bytes else "r"
        return open(path, mode, **self.kwargs)

    def open_write(self, path):
        mode = "w" if not self.open_as_bytes else "wb"
        return open(path, mode, **self.kwargs)

    def _close(self):
        if self.input is not None:
            self.input.close()
            self.input = None
        if self.output is not None:
            self.output.close()
            self.output = None

    def close(self):
        if self._state == self.UNOPENED:
            raise ValueError("Cannot close unopened file")

        if self._state != self.OPEN:
            return

        self._state = self.CLOSED
        self._close()

        if self.backuppath is not None:
            os.replace(self.realpath, self.backuppath)

        os.replace(self._tmppath, self.realpath)

        if self._tmppath is not None:
            UTI._try_delete_file(self._tmppath)
            self._tmppath = None

    def rollback(self):
        if self._state == self.UNOPENED:
            raise ValueError("Cannot close unopened file")
        elif self._state == self.OPEN:
            self._state = self.CLOSED
            self._close()
            if self._tmppath is not None:  # In case of error while opening
                UTI._try_delete_file(self._tmppath)
                self._tmppath = None
        else:
            assert self._state == self.CLOSED
            raise ValueError("Cannot rollback closed file")

    @property
    def closed(self):
        return self._state != self.OPEN

    def read(self, size=-1):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        return self.input.read(size)

    def readline(self, size=-1):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        return self.input.readline(size)

    def readlines(self, sizehint=-1):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        return self.input.readlines(sizehint)

    def readinto(self, b):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        return self.input.readinto(b)

    def readall(self):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        return self.input.readall()

    def write(self, s):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        self.output.write(s)

    def writelines(self, seq):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        self.output.writelines(seq)

    def __iter__(self):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        return iter(self.input)

    def flush(self):
        if self._state != self.OPEN:
            raise ValueError("Filehandle is not currently open")
        self.output.flush()


############### Other Helper Classes for pt ################
class rm:
    """class for pt.x() random creation of variables
    Functions:
        - All types:
            - floats
            - ints
            - strings
            - lists/dicts/sets of floats/ints/strings
            - pattern: gaps
            - pattern: spikes
        - Patterns:
            - Gap trades
                - generates:
                    - n# of "coins"
                    - amount of variance between the highs and lows
                        - with exponential falloff on both ends.
                    - how often to trigger the downward/upward directions
                    - direction bias speed: (should be not perfect, but should go random up/down but in it's way towards the top. But this bias is for how much bias
                    there is to go up or down))
                    - random bias for certain coins (each coin gets assigned a random bias of high, low, frequency, speed direction bias etc)


    """

    # print('class rm')
    ## types of funcs
    def _p_gaps(n, variance, freq, speed, bias, coin):
        pass

    ## helper funcs
    def _blah():
        pass


class ThreadWithResult(threading.Thread):

    """
    This class "ThreadWithResult" has been tweaked to be integrated into print_tricks.
    Star the Repo of the original creator of this class on Github here:
        https://github.com/slow-but-steady/save-thread-result
    Read more detailed usage instructions in the non-modified file located here:
        https://github.com/slow-but-steady/save-thread-result/blob/main/python/save_thread_result/__init__.py
    """

    log_thread_status = True
    log_files = None

    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None
    ):
        def function():
            log_condition = self.log_thread_status is True or self.log_files is not None
            if log_condition:
                start = time.time()
                thread_name = "[" + threading.current_thread().name + "]"
                utc_offset = time.strftime("%z")
                now = lambda: datetime.datetime.now().isoformat() + utc_offset + " "
                message = (
                    C.t2
                    + thread_name.rjust(12)
                    + C.er
                    + " Starting thread...  At: "
                    + now()
                )
                self.__log(message)
            self.result = target(*args, **kwargs)
            if log_condition:
                end = time.time()
                message = (
                    C.t2
                    + thread_name.rjust(12)
                    + C.er
                    + " Finished thread! This thread took "
                    + C.t3
                    + str(end - start)
                    + C.er
                    + " seconds to complete. At: "
                    + now()
                )
                self.__log(message)

        super().__init__(group=group, target=function, name=name, daemon=daemon)

    def __log(self, message):
        if self.log_files is not None:
            try:
                for file in self.log_files:
                    try:
                        file.write(message + "\n")
                    except AttributeError as error_message:
                        # example exception:
                        # AttributeError: 'str' object has no attribute 'write'
                        print(
                            "ERROR! Could not write to "
                            + str(file)
                            + ". Please make sure that every object in "
                            + str(self.log_files)
                            + " supports the .write() method. The exact error was:\n"
                            + str(error_message)
                        )
            except TypeError as error_message:
                # example exception:
                # TypeError: 'int' object is not iterable
                print(
                    "ERROR! Could not write to "
                    + str(self.log_files)
                    + ". Please make sure that the log_files attribute for "
                    + str(self.__class__.name)
                    + " is an iterable object containing objects that support the .write() method. The exact error was:\n"
                    + str(error_message)
                )
        if self.log_thread_status is True:
            print(message)




############### & MORE classes / special classes
class km:
    # Class Vars
    ##Setup Vars
    # user32 = ctypes.windll.user32
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    delay = 0.01
    ## MouseaA
    left = [0x0002, 0x0004]
    right = [0x0008, 0x00010]
    middle = [0x00020, 0x00040]
    ## Letters
    a = 0x41
    b = 0x42
    c = 0x43
    d = 0x44
    e = 0x45
    f = 0x46
    g = 0x47
    h = 0x48
    i = 0x49
    j = 0x4A
    k = 0x4B
    l = 0x4C
    m = 0x4D
    n = 0x4E
    o = 0x4F
    p = 0x50
    q = 0x51
    r = 0x52
    s = 0x53
    t = 0x54
    u = 0x55
    v = 0x56
    w = 0x57
    x = 0x58
    y = 0x59
    z = 0x5
    ## Numbers
    num0 = 0x30
    num1 = 0x31
    num2 = 0x32
    num3 = 0x33
    num4 = 0x34
    num5 = 0x35
    num6 = 0x36
    num7 = 0x37
    num8 = 0x38
    num9 = 0x39
    ## Keyboard extras
    cancel = 0x03
    backspace = 0x08
    tab = 0x09
    enter = 0x0D
    shift = 0x10
    ctrl = 0x11
    alt = 0x12
    capslock = 0x14
    esc = 0x1B
    space = 0x20
    pgup = 0x21
    pgdown = 0x22
    end = 0x23
    home = 0x24
    leftarrow = 0x26
    uparrow = 0x26
    rightarrow = 0x27
    downarrow = 0x28
    select = 0x29
    print = 0x2A
    execute = 0x2B
    printscreen = 0x2C
    insert = 0x2D
    delete = 0x2E
    help = 0x2F
    leftwin = 0x5B
    rightwin = 0x5C
    leftshift = 0xA0
    rightshift = 0xA1
    leftctrl = 0xA2
    rightctrl = 0xA3
    ## Numpad
    numpad0 = 0x60
    numpad1 = 0x61
    numpad3 = 0x63
    numpad4 = 0x64
    numpad5 = 0x65
    numpad6 = 0x66
    numpad7 = 0x67
    numpad8 = 0x68
    numpad9 = 0x69
    multiply = 0x6A
    add = 0x6B
    seperator = 0x6C
    subtract = 0x6D
    decimal = 0x6E
    divide = 0x6F
    ## function keys
    F1 = f1 = 0x70
    F2 = f2 = 0x71
    F3 = f3 = 0x72
    F4 = f4 = 0x73
    F5 = f5 = 0x74
    F6 = f6 = 0x75
    F7 = f7 = 0x76
    F8 = f8 = 0x77
    F9 = f9 = 0x78
    F10 = f10 = 0x79
    F11 = f11 = 0x7A
    F12 = f12 = 0x7B
    F13 = f13 = 0x7C
    F14 = f14 = 0x7D
    F15 = f15 = 0x7E
    F16 = f16 = 0x7F
    F17 = f17 = 0x80
    F19 = f19 = 0x82
    F20 = f20 = 0x83
    F21 = f21 = 0x84
    F22 = f22 = 0x85
    F23 = f23 = 0x86
    F24 = f24 = 0x87
    numlock = 0x90
    scrolllock = 0x91
    ## Media
    apps = 0x5D
    sleep = 0x5F
    leftmenu = 0xA4
    rightmenu = 0xA5
    browserback = 0xA6
    browserforward = 0xA7
    browserrefresh = 0xA8
    browserstop = 0xA9
    browserfavorites = 0xAB
    browserhome = 0xAC
    volumemute = 0xAD
    volumedown = 0xAE
    volumeup = 0xAF
    nexttrack = 0xB0
    prevoustrack = 0xB1
    stopmedia = 0xB2
    playpause = 0xB3
    launchmail = 0xB4
    selectmedia = 0xB5
    launchapp1 = 0xB6
    launchapp2 = 0xB7
    ## symbols
    semicolon = 0xBA
    equals = 0xBB
    comma = 0xBC
    dash = 0xBD
    period = 0xBE
    slash = 0xBF
    accent = 0xC0
    openingsquarebracket = 0xDB
    backslash = 0xDC
    closingsquarebracket = 0xDD
    quote = 0xDE
    play = 0xFA
    zoom = 0xFB
    PA1 = 0xFD
    clear = 0xFE
    ## shifts vs originals
    letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    shiftSymbols = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'

    # Keyboard & Mouse functions
    def wait(waitTime=""):
        """_summary_

        Args:
        waitTime (str, optional): _description_. Defaults to ''."""
        if waitTime == "":
            waitTime = km.delay
        time.sleep(waitTime)

    def press(key, pressTime=""):
        if pressTime == "":
            pressTime = km.delay
        km.user32.keybd_event(key, 0, 0, 0)
        time.sleep(pressTime)
        km.user32.keybd_event(key, 0, 2, 0)
        time.sleep(pressTime)

        return

    def hold(key):
        km.user32.keybd_event(key, 0, 0, 0)
        # time.sleep(km.delay)

        return

    def release(key):
        km.user32.keybd_event(key, 0, 2, 0)
        time.sleep(km.delay)
        return

    def sequence(sentence):
        for letter in sentence:
            shift = letter in km.shiftSymbols
            fixedletter = "space"
            if letter == "`" or letter == "~":
                fixedletter = "accent"
            elif letter == "1" or letter == "!":
                fixedletter = "num1"
            elif letter == "2" or letter == "@":
                fixedletter = "num2"
            elif letter == "3" or letter == "#":
                fixedletter = "num3"
            elif letter == "4" or letter == "$":
                fixedletter = "num4"
            elif letter == "5" or letter == "%":
                fixedletter = "num5"
            elif letter == "6" or letter == "^":
                fixedletter = "num6"
            elif letter == "7" or letter == "&":
                fixedletter = "num7"
            elif letter == "8" or letter == "*":
                fixedletter = "num8"
            elif letter == "9" or letter == "(":
                fixedletter = "num9"
            elif letter == "0" or letter == ")":
                fixedletter = "num0"
            elif letter == "-" or letter == "_":
                fixedletter = "dash"
            elif letter == "=" or letter == "+":
                fixedletter = "equals"
            elif letter in km.letters:
                fixedletter = letter.lower()
            elif letter == "[" or letter == "{":
                fixedletter = "openingsquarebracket"
            elif letter == "]" or letter == "}":
                fixedletter = "closingsquarebracket"
            elif letter == "\\" or letter == "|":
                fixedletter == "backslash"
            elif letter == ";" or letter == ":":
                fixedletter = "semicolon"
            elif letter == "'" or letter == '"':
                fixedletter = "quote"
            elif letter == "," or letter == "<":
                fixedletter = "comma"
            elif letter == "." or letter == ">":
                fixedletter = "period"
            elif letter == "/" or letter == "?":
                fixedletter = "slash"
            elif letter == "\n":
                fixedletter = "enter"
            keytopress = eval("km." + str(fixedletter))
            if shift:
                km.hold(km.shift)
                km.press(keytopress)
                km.release(km.shift)
            else:
                km.press(keytopress)
        return

    def movemouse(x, y):
        km.user32.SetCursorPos(x, y)

        return

    def move_mouse_relative(dx, dy):
        current_pos = km.get_mousePos()
        new_x = current_pos[0]
        new_y = current_pos[1]
        km.user32.SetCursorPos(new_x, new_y)
        
    def click(button):
        km.user32.mouse_event(button[0], 0, 0, 0, 0)
        time.sleep(km.delay)
        km.user32.mouse_event(button[1], 0, 0, 0, 0)
        time.sleep(km.delay)

        return

    def holdclick(button):
        km.user32.mouse_event(button[0], 0, 0, 0, 0)
        time.sleep(km.delay)

        return

    def releaseclick(button):
        km.user32.mouse_event(button[1])
        time.sleep(km.delay)

        return

    def get_mousePos():
        """Returns the current xy coordinates of the mouse cursor as a two-integer
        tuple by calling the GetCursorPos() win32 function.

        Returns:
        (x, y) tuple of the current xy coordinates of the mouse cursor.
        """

        cursor = WhereMouseNow()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))

        return (cursor.x, cursor.y)


class WhereMouseNow(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pass


class ind:
    """indexing class"""

    # print('class ind (index)')
    dict_file_names = (
        {}
    )  ## a lookup of all files and their associated names are here. Just as a space saver in the code.
    dict_whole_index = {}  ## index of the entire file and it's contents
    dict_pt_index = {}  ## index of just 'pt(' and 'pt.' statements

    dict_structure_level = {0: "<module>"}
    func_local_num = 0  ## the "local" line number of the function. Line 0 means the "def" part. The last number would be the last line of that definition.
    func_name = ""
    spaces_for_func = ""

    in_mid_of_triplesQ = False

    def fast_trace_viability_test():
        """fast trace basic"""
        # print('fast_trace_viability_test')

        # file_path, dirName, file_name = ind.getThisfile_name()
        file_name = "blahblah.py"
        file_path = "C:\\Users\\blah\\Desktop\\" + file_name
        # print('dict: ', ind.dict_pt_index)
        line_no = list(ind.dict_pt_index.keys())[0]
        code = ind.dict_pt_index[line_no]
        func_name = "placeHolderFunc"
        return file_name, file_path, line_no, func_name, code

    def getThisfile_name():
        """Couldn't use my pt.l() module, but used this. Update later to use my own code."""

        if __name__ != "__main__":
            fullPath = ""
            for frame in inspect.stack()[2:]:
                if frame.file_name[0] != "<":
                    # print(frame.file_name)
                    fullPath = frame.file_name
            # print('fullPath: ', fullPath)
            file_name = fullPath.split("\\")[-1]
            # print('file_name;', file_name)
            dirName = os.path.split(fullPath)[0]
            # print('dirName: ', dirName)
            return fullPath, dirName, file_name

    def chop_comment(line):
        """from stackexchange.. find author.. but currently unused"""
        c_backslash = "\\"
        c_dquote = '"'
        c_quote = "'"
        c_comment = "#"
        # a little state machine with two state varaibles:
        in_quote = False  # whether we are in a quoted string right now
        backslash_escape = False  # true if we just saw a backslash

        for i, ch in enumerate(line):
            if not in_quote and ch == c_comment:
                # not in a quote, saw a '#', it's a comment.  Chop it and return!
                return line[:i]
            elif backslash_escape:
                # we must have just seen a backslash; reset that flag and continue
                backslash_escape = False
            elif in_quote and ch == c_backslash:
                # we are in a quote and we see a backslash; escape next char
                backslash_escape = True
            elif ch == c_dquote:
                in_quote = not in_quote
            # elif ch == c_quote:
            #     in_quote = not in_quote

        return line

    def ignore_All_strings(line):
        """
        - All lines with "pt(" in them come here.
        - We remove all of contents between any quotes and return the line. So any pt() that were not going to be called because they were in quotes, won't be analyzed.
        """

        # ... ###db(line)
        if '"' in line:
            char = '"'
        elif "'" in line:
            char = "'"
        # ... ###db('start')
        # ... ###db(line)
        line_parts = line.partition(
            char
        )  ## We are getting the first and last part of the tuple "line_parts" and leaving behind the quoted part.
        # ... ###db(line_parts)
        line_before_quote = line_parts[0]
        line_remainder = line_parts[2]
        line_rem_parts = line_remainder.partition(char)
        line_after_quotes = line_rem_parts[2]
        line = line_before_quote + line_after_quotes
        line = line.rstrip()  ## removing whitespace.
        # ... ###db(line)
        # ... ###db('end')
        return line

    def getfunc_name_deprecated(orig_line, line_stripped, in_a_functionQ, lnNum):
        module_base = "<module>"

        if in_a_functionQ == False:
            ... ###db(1)
            if "def " in line_stripped or "class " in line_stripped:
                ... ###db(1.1)
                if "def " in line_stripped:
                    split_word = "def "
                elif "class " in line_stripped:
                    split_word = "class "
                in_a_functionQ = True
                ind.func_name = line_stripped.split(split_word)[1].split("(")[0]
                ind.func_name = ind.func_name.strip()
                # ... ###db(ind.func_name)
                ind.func_local_num = 1  ## we aren't setting the line number for this line, as the def line is 0. But we are setting it up for what the next line number will be.
                ind.spaces_for_func = 0  ## Might make sense to set this elsewhere. This isn't saying where "class" or "def" show up, but is rather defaulting their sub-lines back to 0, before we process them.

                return ind.func_name, in_a_functionQ
            else:
                ... ###db(1.2)
                ind.func_name = module_base
                return module_base, in_a_functionQ

        elif in_a_functionQ == True:
            ... ###db(2)
            # ... ###db(ind.func_local_num)
            if ind.func_local_num == 1:
                ... ###db(2.1)
                if "def " in line_stripped or "class " in line_stripped:
                    ... ###db("2.1.1")
                    if "def " in line_stripped:
                        split_word = "def "
                    elif "class " in line_stripped:
                        split_word = "class "
                    # in_a_functionQ = True
                    ind.func_name = line_stripped.split(split_word)[1].split("(")[0]
                    ind.func_name = ind.func_name.strip()
                    return ind.func_name, in_a_functionQ
                else:
                    ... ###db("2.1.2")
                    # ... ###db(ind.func_local_num)
                    ind.func_local_num = 2
                    # ... ###db(ind.func_local_num)
                    ind.spaces_for_func = ind.get_func_horizontal_space(orig_line)
                    return ind.func_name, in_a_functionQ
            else:
                ... ###db(2.2)
                this_spaces = ind.get_func_horizontal_space(orig_line)
                # ... ###db(this_spaces)
                if this_spaces < ind.spaces_for_func:
                    ... ###db("2.2.1")
                    in_a_functionQ = False
                    ind.func_name = module_base
                    ind.spaces_for_func = (
                        0  ## this is not longer in a func, so we reset the spacing
                    )
                    return module_base, in_a_functionQ
                else:
                    ... ###db("2.2.2")
                    ... ###db(ind.func_name)
                    return ind.func_name, in_a_functionQ

    def gen_dict_of_pt_locations(file_path):
        functionName = "<module>"
        lnNum = 0  # we are starting at 0, because we have to iterate lnNum +=1 before we actually get a count. So it starts it at one.
        in_triple_quotes = False
        in_a_functionQ = False
        thisLine = ""
        with open(file_path, "r") as f:
            allLines = f.readlines()

            for orig_line in allLines:
                line_stripped = orig_line.strip()

                lnNum += 1
                if in_triple_quotes == True:
                    if "'''" in line_stripped or '"""' in line_stripped:
                        in_triple_quotes = False

                    continue

                if "'''" in line_stripped or '"""' in line_stripped:
                    triple1 = line_stripped.count('"""')
                    triple2 = line_stripped.count("'''")
                    if (
                        triple1 % 2 == 0 or triple2 % 2 == 0
                    ):  ## if the number of quotes is even, then the triple quote is ending on this line.
                        continue
                    else:
                        in_triple_quotes = True
                        continue

                ... ###db(line_stripped)
                if line_stripped == "":  ## if line is blank, continue.
                    # ... ###db('line is blank')
                    continue
                elif line_stripped[0] == "#":  ## if whole line has been commented out
                    # ... ###db('commented out whole line')
                    continue
                # line_stripped = line ## we keep a copy of the original line, before removing quotes, in order to get the original args, if needed (the args could be a string)
                functionName, in_a_functionQ = ind.getfunc_name_deprecated(
                    orig_line, line_stripped, in_a_functionQ, lnNum
                )
                if "pt(" in line_stripped or "pt." in line_stripped:
                    # ... ###db(orig_line)
                    if "#" in line_stripped:
                        line_stripped = ind.chop_comment(
                            line_stripped
                        )  ## remove / ignore commented lines.
                    elif "'" in line_stripped or '"' in line_stripped:
                        line_stripped = ind.ignore_All_strings(
                            line_stripped
                        )  ## remove / ignore pt statements within strings.
                    pt_count1 = line_stripped.count("pt(")
                    pt_count2 = line_stripped.count("pt.")
                    pt_count = pt_count1 + pt_count2
                    if pt_count == 0:
                        continue

                    lines = ""
                    if (
                        ";" in orig_line
                    ):  ## If there are multiple ';' then that means this is a multi-line statement
                        # but if there are multiple pt's without this, then we are either in a comment or a nested/embedded pt statement
                        ## TODO TODO - must support embedded pt statements such as " pt.t(pt('hi)) " But actually, why are we even counting 'pt.' anyways?
                        ## why wouldn't we just look for pt() statements ad not pt.* ? Maybe we should because eventually I'll want them to print in
                        ## the same manner as pt.t() statements.
                        lines = orig_line.split(";")
                    else:
                        lines = orig_line.split(")")  ## UNTESTED CURRENTLY
                    # ... ###db(lines, ntl=0)
                    for i in range(pt_count):
                        if pt_count == 1:
                            subNum, dot = "", ""
                            thisLine = orig_line
                        else:
                            subNum = str(i)
                            dot = "."
                            thisLine = lines[i]
                        args_only = (
                            re.compile(r"\((.*?)\).*$").search(orig_line).groups()[0]
                        )
                        argsList = args_only.split(",")
                        numArgs = len(argsList)
                        # ... ###db(line_stripped)
                        # ... ###db(args_only)
                        key = f"{lnNum}{dot}{subNum}"
                        ind.dict_pt_index[key] = (
                            key,
                            pt_count,
                            thisLine,
                            numArgs,
                            argsList,
                            args_only,
                            args_only,
                            functionName,
                        )
        return ind.dict_pt_index
        """
                        - Is Looped? 
                            - Is either the pt() statement within a loop, or is the pt statement within a function but that function call is inside a loop? 
                        - file Name
                            - or.. to save space: 
                                a number that refers to where to find this file_name in another dictionary. 
                                - So we create a file_name reference dict that stores each key (1-n), and it's value is whatever the file_name is. 
                                    - So in our dict that shows values, we will just have a 1 or something in the file_name slot, and that will lookup what the #1 key is
                                    and get it's file_name value. 
                        - last value of each of it's args. 
                            - We test the current line number, arg names and then values. 
                                - if the value hasn't changed, then we shortcut the rest of the entire code and paste the saved results.
                        - saved results from the last time this code was ran
                            - this is like the final compiled print_str or whatever. 
                            - We use this to bypass the needing to re-do the code, because if it's the same code (same call, same args, same line), and the values of those args
                            also haven't changed, then the results will be identical. 
                            """

    def gen_dict_of_pt_locations_old2(file_path):
        with open(file_path, "r") as f:
            num = 0  # we are starting at 0, because we have to iterate num +=1 before we actually get a count. So it starts it at one.
            for line in f.readlines():
                pt_count1 = line.count("pt(")
                pt_count2 = line.count("pt.")
                pt_count = pt_count1 + pt_count2
                # pt(pt_count)
                num += 1
                if pt_count > 0:
                    if pt_count == 1:
                        ind.dict_pt_index[num] = line
                    else:
                        lines = line.split(";")
                        for i in range(pt_count):
                            ind.dict_pt_index[f"{num}.{i}"] = lines[i]
        return ind.dict_pt_index

    def gen_dict_of_file(file_path):
        with open(file_path, "r") as f:
            num = 1
            for line in f.readlines():
                ind.dict_whole_index[num] = line
                num += 1

    def debug_ind_class(line_stripped, skipQ_for_debug):
        if line_stripped[0:3] == "stp":
            # pt.p()
            pt.ex()
        elif line_stripped == "ignore = True":
            return True
        elif line_stripped == "ignore = False":
            return False
        else:
            return skipQ_for_debug

    def gen_D(file_path):
        lnNum = 0
        skipQ_for_debug = False  ## just for testing purposes to ignore lines in my test, add 'ignore = True, then 'ignore = False' to turn back off.
        multipleLines = []  ## Meaning multiple lines on one line, with a ;
        with open(file_path, "r") as f:
            allLines = f.readlines()
            for line_o in allLines:  # line_o = original line
                lnNum += 1
                line_stripped = line_o.strip()

                skipQ_for_debug = ind.debug_ind_class(line_stripped, skipQ_for_debug)
                if skipQ_for_debug:
                    continue
                # ... ###db(line_stripped)
                ind.in_mid_of_triplesQ = ind.gen_d_A_tripleQuotesCheck(
                    line_stripped, ind.in_mid_of_triplesQ
                )
                ignoreLineQ = ind.gen_d_B_ignoreLine(
                    line_stripped, ind.in_mid_of_triplesQ
                )
                # ... ###db(ind.in_mid_of_triplesQ)
                # ... ###db(ignoreLineQ)
                if ignoreLineQ:
                    continue
                # Find if there is more than one line in this line, then process each separately.
                # if ';' in line_stripped:
                #     multipleLines = line_stripped.split(';')
                multipleLines = line_stripped.split(";")
                lenML = len(multipleLines)
                # ... ###db(lenML)
                for line_edit in multipleLines:
                    ... ###db(line_edit)
                    blankSpaces = ind.gen_d_C_blankSpaces(line_o)
                    ... ###db(blankSpaces)
                    # func_name = ind.gen_d_D_structureCheck(line_edit, blankSpaces, ind.dict_structure_level)
                    func_name = ind.gen_d_D_AST_structureCheck(
                        file_path, line_o, lnNum, ind.dict_structure_level
                    )

    def gen_d_D_AST_structureCheck(file_path, line_o, lnNum, d_struct_level):
        import ast

        gg = ast.parse(line_o, file_path)
        print(gg)

    #     class GetAssignments(ast.NodeVisitor):
    # def visit_Name(self, node):
    #     if isinstance(node.ctx, ast.Store):
    #         print node.id, node.line_no
    def gen_d_D_structureCheck(line_edit, blankSpaces, dictStruct_L):
        """Check what type of strucutre level we are at (module, class, function, loop, etc) and name of the structure."""

        """NOTE 
         - Problem: 
            - I need to generate the structure level after seeing :
                1st: the structure
                2nd: the next valid code line's position
        - new:
            - Use AST to get line numbers for every class and function into a dict. 
                key = line number
            - Use my code to determine the indent level of each class/funct
            - Get my 'pt('  line number and indention level. 
                - find the closest line number funct to me. 
                - check if same indention level. If not move up. 
                - Move up the list until I find the one that has the same indent level. 
            """
        struct = "<module>"
        callable_structs = (
            "class",
            "def",
        )  ## the if/elif/else are for statements like "if name == main" and other stuff that I haven't accounted for yet.
        secondary_structs = ("for", "while", "if", "elif", "else")

        if line_edit.startswith(tuple(callable_structs)):
            struct = re.compile(r"\((.*?)\).*$").search(line_edit).groups()[0]

            # ... ###db(1)
            ... ###db(struct)
        elif line_edit.startswith(tuple(secondary_structs)):
            # ... ###db(2)
            struct = line_edit
            ... ###db(struct)
        dictStruct_L[
            struct
        ] = ""  ## We are assigning this a temporary key placeholder until we can retrieve it's spacing on the next code that is under this structure.

        if blankSpaces in dictStruct_L:
            ... ###db("3 - blankspaces in dictStruct_L")
            return dictStruct_L[blankSpaces]

        # if 'def ' in line_stripped or 'class ' in line_stripped:
        #     ... ###db(1.1)
        #     if 'def ' in line_stripped:
        #         split_word = 'def '
        #     elif 'class ' in line_stripped:
        #         split_word = 'class '
        #     in_a_functionQ = True
        #     ind.func_name = line_stripped.split(split_word)[1].split('(')[0]
        #     ind.func_name = ind.func_name.strip()
        #     # ... ###db(ind.func_name)
        #     ind.func_local_num = 1 ## we aren't setting the line number for this line, as the def line is 0. But we are setting it up for what the next line number will be.
        #     ind.spaces_for_func = 0 ## Might make sense to set this elsewhere. This isn't saying where "class" or "def" show up, but is rather defaulting their sub-lines back to 0, before we process them.

        #     return ind.func_name, in_a_functionQ
        # else:
        #     ... ###db(1.2)
        #     ind.func_name = module_base
        #     return module_base, in_a_functionQ

    def gen_d_C_blankSpaces(orig_line):
        spacing = len(orig_line) - len(
            orig_line.lstrip(" ")
        )  ## Take the actual original line length, and remove the white spaces from the front only, to

        return spacing

    def gen_d_B_ignoreLine(line_stripped, in_mid_of_triplesQ):
        ignoreList = ("#", "'''", '"""')
        processList = (
            "pt(",
            "pt.",
            "while",
            "for",
            "def",
            "class",
            "if",
            "elif",
            "else",
        )

        ## if this line is commented out, then we ignore the line
        if (
            line_stripped.startswith(tuple(ignoreList)) or in_mid_of_triplesQ == True
        ) and ";" not in line_stripped:
            return True
        elif line_stripped == "":  ## blank line, ignore it
            return True

        ## After seeing if we should ignore the line, Check to see if anything we care about is in this line, if not ignore it.
        for string in processList:
            if (
                string in line_stripped
            ):  ## if what I'm looking for is in this line, then don't ignore it (return false)
                return False
        return True  ## If nothing in process list, then we return this as true to ignore this line

    def gen_d_A_tripleQuotesCheck(line_stripped, in_mid_of_triplesQ):
        if "'''" in line_stripped or '"""' in line_stripped:
            # ... ###db(line_stripped)
            # ... ###db(1)
            triple1_ct = line_stripped.count('"""')
            # ... ###db(triple1_ct)
            triple2_ct = line_stripped.count("'''")
            if in_mid_of_triplesQ:
                # ... ###db(1.1)
                triple1_ct += 1
                triple1_ct += 1
            triple_ct = max(triple1_ct, triple2_ct)
            # ... ###db(triple2_ct)
            # ... ###db(triple2_ct %2)

            if (
                triple_ct % 2 == 0
            ):  ## if we were already in a triple quote and there is another __ amount here, meanign that it's even, then we are still in a quote (for situations where someone ends a triple and starts another on same line)
                # ... ###db(1.2)
                return False
            else:
                # ... ###db(1.3)
                return True

        else:
            # ... ###db(2)
            return in_mid_of_triplesQ  ## If these ''' not in the line, then return the argument that was sent here (true or false)


class speedup:
    ...


class superspeed:
    ...



class Insert_PT_Functions_On_Every_Line:
    def __init__():
        pass







class Profiler:
    def __init__(self):
        self.calling_file = inspect.stack()[1].file_name
        self.modify_file()

    def modify_file(self):
        with open(self.calling_file, 'r') as file:
            lines = file.readlines()
        with open(self.calling_file, 'w') as file:
            start_modifying = False
            multi_line_comment = False
            for i, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    multi_line_comment = not multi_line_comment
                if 'from print_tricks import' in line:
                    start_modifying = True
                if not start_modifying or not stripped or stripped.startswith("#") or stripped.endswith(":") or multi_line_comment:
                    file.write(line)
                else:
                    code, _, comment = line.partition("#")
                    file.write(f"{code.strip()} ;pt({i})  #{comment}")







if __name__ == '__main__':
    ...
    '''
    All of the testing code has been moved to print_tricks_testing.py
    
    '''