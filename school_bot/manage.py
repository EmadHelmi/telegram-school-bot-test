import os
import sys
from inspect import isclass

command_files = [command.split("/")[-1].split(".")[0] for command in filter(
    lambda command: not command.startswith("__"), os.listdir("commands"))]

commands = {}
for command_file in command_files:
    objects = __import__("commands.%s" % command_file, fromlist=["objects"])
    classes = [obj for obj in dir(objects) if isclass(getattr(objects, obj))]
    command_class = list(filter(lambda cls: cls.endswith(
        "Command") and cls != "Command", classes))
    if len(command_class) > 1:
        raise ImportError(
            "There are more than one command class in %s" %
            "commands.%s" % command_file
        )
    commands[command_file] = getattr(objects, command_class[0])

if __name__ == "__main__":
    command = sys.argv[1]
    commands[command].run()
