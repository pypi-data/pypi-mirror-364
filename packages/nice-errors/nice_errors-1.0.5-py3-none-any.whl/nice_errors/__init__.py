# friendly_errors.py

import sys
import traceback
from colorama import Fore, Style, init
# Initialize colorama
init(autoreset=True)

# === Configuration ===
CONFIG = {
    "SHOW_TRACEBACK": True  # Toggle technical tracebacks
}

# Friendly error explanations
ERROR_MESSAGES = {
    "NameError": {
        "title": "❌ Oops! That Name Doesn’t Exist",
        "explanation": "Python saw a name it didn’t recognize. Maybe a typo or you forgot to define it?",
        "fix": "Make sure you spelled it right and created it before using it.",
        "emoji": "🔍"
    },
    "SyntaxError": {
        "title": "📝 Syntax Trouble!",
        "explanation": "Something in your code looks off — like a missing colon or quote.",
        "fix": "Check your brackets, colons, and quotation marks. They need to match!",
        "emoji": "✏️"
    },
    "TypeError": {
        "title": "🔢 Uh-oh, Types Don't Match",
        "explanation": "You tried to do something like add a number to a word — and Python got confused.",
        "fix": "Make sure you're working with the right types. You can convert them if needed!",
        "emoji": "🔁"
    },
    "IndexError": {
        "title": "📦 List Index Out of Bounds",
        "explanation": "You asked for a list item that’s too far — it doesn’t exist!",
        "fix": "Try using 'len()' to check the size before accessing by index.",
        "emoji": "📏"
    },
    "KeyError": {
        "title": "🔑 Key Not Found!",
        "explanation": "That key you tried to use in a dictionary isn’t there.",
        "fix": "Use '.get()' or check with 'in' before accessing the key.",
        "emoji": "🗝️"
    },
    "ValueError": {
        "title": "❗ Weird Value Detected",
        "explanation": "Python got a value that looked okay... but wasn’t quite right.",
        "fix": "Double-check the input values — they may need tweaking!",
        "emoji": "📉"
    },
    "AttributeError": {
        "title": "🔍 Missing Something!",
        "explanation": "Python expected your object to have a function or property — but it doesn’t.",
        "fix": "Use 'dir()' to see what your object can actually do.",
        "emoji": "🧱"
    },
    "ZeroDivisionError": {
        "title": "🚫 Can’t Divide by Zero",
        "explanation": "Nice try, but dividing by 0 isn’t allowed in math or Python!",
        "fix": "Before dividing, check that the bottom number isn’t zero.",
        "emoji": "➗"
    },
    "ImportError": {
        "title": "📦 Couldn’t Import Something",
        "explanation": "Python had trouble importing a piece of code or library.",
        "fix": "Make sure the name is correct and it’s installed properly.",
        "emoji": "📚"
    },
    "ModuleNotFoundError": {
        "title": "🔍 Module Not Found",
        "explanation": "Python couldn’t find that library or module.",
        "fix": "Try running 'pip install' to add it, or check the spelling.",
        "emoji": "📦"
    },
    "IndentationError": {
        "title": "📐 Indentation Mix-Up",
        "explanation": "Python is picky about spaces and tabs. Something’s not lined up right.",
        "fix": "Stick with either spaces or tabs — don’t mix them!",
        "emoji": "📏"
    },
    "FileNotFoundError": {
        "title": "📄 File Not Found",
        "explanation": "The file you tried to open doesn't exist — or the path is wrong.",
        "fix": "Double-check the file name and location.",
        "emoji": "🗂️"
    },
    "PermissionError": {
        "title": "🔒 No Permission!",
        "explanation": "Python tried to open something, but it doesn’t have permission.",
        "fix": "Try running with more access or changing file permissions.",
        "emoji": "🚷"
    },
    "RecursionError": {
        "title": "🔁 Too Much Recursion!",
        "explanation": "Your function is calling itself too many times and didn’t stop.",
        "fix": "Make sure you have a base case that ends the loop.",
        "emoji": "🌀"
    },
    "MemoryError": {
        "title": "💥 Out of Memory",
        "explanation": "Python ran out of memory to keep going.",
        "fix": "Try using smaller data chunks or loops instead of big lists.",
        "emoji": "💾"
    },
    "OverflowError": {
        "title": "📈 Number Got Too Big",
        "explanation": "A number went beyond what Python can handle!",
        "fix": "Use smaller numbers, or use special number types like 'decimal' if needed.",
        "emoji": "🔺"
    },
    "StopIteration": {
        "title": "🛑 Nothing Left to Loop",
        "explanation": "You're trying to loop through something that’s finished.",
        "fix": "Make sure you're not using 'next()' too many times.",
        "emoji": "⏹️"
    },
    "AssertionError": {
        "title": "⚠️ Assertion Failed",
        "explanation": "An assert statement expected something to be true — but it wasn’t.",
        "fix": "Check what you're testing. Maybe it’s not quite what you think.",
        "emoji": "🔍"
    },
    "Generic": {
        "title": "❓ Something Went Wrong",
        "explanation": "An error happened, but I’m not sure which one!",
        "fix": "Check the code and traceback to learn more.",
        "emoji": "🤷"
    }
}

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_type = exc_type.__name__
    msg = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["Generic"])

    tb = traceback.extract_tb(exc_traceback)
    if tb:
        tb_last = tb[-1]
        filename = tb_last.filename
        lineno = tb_last.lineno
        code_line = tb_last.line.strip() if tb_last.line else "N/A"
    else:
        filename = "<unknown>"
        lineno = "?"
        code_line = "?"

    print(Fore.RED + Style.BRIGHT + "\n🚨 Uh-oh! A Python Error Happened!\n")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{msg['emoji']} {msg['title']}")
    print(Fore.WHITE + f"\n{msg['explanation']}")
    print(Fore.GREEN + f"💡 Tip: {msg['fix']}")
    print(Fore.CYAN + "\n📍 Where it happened:")
    print(f"{Fore.WHITE}  File: {Fore.MAGENTA}{filename}")
    print(f"{Fore.WHITE}  Line: {Fore.MAGENTA}{lineno}")
    print(f"{Fore.WHITE}  Code: {Fore.MAGENTA}{code_line}")

    if CONFIG["SHOW_TRACEBACK"]:
        print(Fore.LIGHTBLACK_EX + "\n🛠️ Technical Details (if you're curious):")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

# Automatically install the handler
sys.excepthook = handle_exception
