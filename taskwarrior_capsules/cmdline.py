import pkg_resources
import subprocess
import sys

from blessings import Terminal

from .exceptions import CapsuleError
from .capsule import CommandCapsule
from .capsule_meta import CapsuleMeta
from .data import BUILT_IN_COMMANDS


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
    meta = CapsuleMeta()

    command = None
    command_name = ''
    filter_args = []
    extra_args = []
    for idx, arg in enumerate(args):
        if arg in commands or arg in BUILT_IN_COMMANDS:
            command_name = arg
            if arg in commands:
                command = commands[arg]
            filter_args = args[0:idx]
            extra_args = args[idx+1:]
    if not command_name:
        extra_args = args[0:]

    for processor_name, processor in preprocessors.items():
        filter_args, extra_args, command_name = processor.execute(
            'preprocessor', meta, command_name, filter_args, extra_args,
            terminal=term,
        )

    if command:
        try:
            result = command.execute(
                'command', meta, command_name, filter_args, extra_args,
                terminal=term,
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
        task_args = ['task'] + filter_args
        if command_name:
            task_args.append(command_name)
        task_args = task_args + extra_args
        result = subprocess.call(task_args)

    for processor_name, processor in postprocessors.items():
        processor.execute(
            'postprocessor', meta, command_name, filter_args, extra_args,
            terminal=term,
            result=result
        )

    sys.exit(result)
