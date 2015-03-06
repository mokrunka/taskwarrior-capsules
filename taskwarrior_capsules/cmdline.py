import pkg_resources
import subprocess
import sys

from blessings import Terminal

from .exceptions import CapsuleError
from .plugin import CommandCapsule


def get_installed_capsules(variant='command'):
    groupmap = {
        'command': 'taskwarrior_capsules',
        'preprocessor': 'taskwarrior_preprocessor_capsules',
        'postprocessor': 'taskwarrior_postprocessor_capsules',
    }

    possible_commands = {}
    for entry_point in (
        pkg_resources.iter_entry_points(group=groupmap[variant])
    ):
        try:
            loaded_class = entry_point.load()
        except ImportError:
            continue
        if not issubclass(loaded_class, CommandCapsule):
            continue
        possible_commands[entry_point.name] = loaded_class

    return possible_commands


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    term = Terminal()
    commands = get_installed_capsules('command')
    preprocessors = get_installed_capsules('preprocessor')
    postprocessors = get_installed_capsules('postprocessor')

    command = None
    filter_args = None
    extra_args = None
    for idx, arg in enumerate(args):
        if arg in commands:
            command = commands[arg]
            filter_args = args[0:idx]
            extra_args = args[idx+1:]

    for processor in preprocessors:
        filter_args, extra_args, command = processor.execute(
            'preprocessor', filter_args, extra_args, command,
        )

    if command:
        command_name = args.command[0]
        cmd_class = commands[command_name]

        try:
            result = cmd_class.execute(
                'command', filter_args, extra_args, command_name
            )
        except CapsuleError as e:
            print(
                "{t.red}The {capsule_name} taskwarrior capsule "
                "encountered an error processing your request: "
                "{t.normal}{t.red}{t.bold}{error}{t.normal}".format(
                    capsule_name=command_name,
                    t=term,
                    error=str(e)
                )
            )
            sys.exit(90)
    else:
        # Run this as a normal command
        task_args = ['task'] + args
        result = subprocess.call(task_args)

    for processor in postprocessors:
        filter_args, extra_args, command = processor.execute(
            'postprocessor', filter_args, extra_args, command,
            result=result
        )

    sys.exit(result)
