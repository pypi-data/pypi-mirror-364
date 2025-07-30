# When to Reach for code
# 	•	Embedding: Add a console widget to GUIs or network services.
# 	•	DSLs: Provide user-facing mini-languages on top of Python.
# 	•	Debugging: Jump into a REPL on errors or specific checkpoints.

from code import InteractiveConsole, InteractiveInterpreter

interp = InteractiveInterpreter(locals={})
interp.runsource("x = 10")  # defines x in the interpreter namespace
interp.runsource("print(x * 2)")  # outputs: 20

console = InteractiveConsole(locals={"greet": lambda n: print(f"Hi, {n}!"), "PI": 3.14})
console.interact(banner="Custom REPL — type help()", exitmsg="Bye!")
