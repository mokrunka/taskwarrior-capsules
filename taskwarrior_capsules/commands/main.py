from taskwarrior_capsules import __version__
from taskwarrior_capsules.capsule import CommandCapsule
from taskwarrior_capsules.cmdline import get_installed_capsules
from taskwarrior_capsules.exceptions import CapsuleError


class Capsules(CommandCapsule):
    """ Capsule management utility """
    TASKWARRIOR_VERSION_CHECK_NECESSARY = False
    MIN_VERSION = __version__
    MAX_VERSION = __version__

    def handle(self, filter_args, extra_args, terminal=None, **kwargs):
        try:
            first_arg = extra_args[0].lower()
        except IndexError:
            raise CapsuleError("No context command specified")

        if first_arg == 'list':
            search_list = {
                'Installed Preprocessors': 'preprocessor',
                'Installed Commands': 'command',
                'Installed Postprocessors': 'postprocessor',
            }

            for headline, variant in search_list.items():
                print "{t.bold}{t.blue}{headline}{t.normal}:".format(
                    headline=headline,
                    t=terminal
                )
                for name, module in get_installed_capsules(variant).items():
                    summary = module.get_summary()
                    print "- {t.bold}{name}{t.normal}: {docstring}".format(
                        name=name,
                        t=terminal,
                        docstring=summary if summary else '(No docstring)'
                    )
                print ""
        else:
            raise CapsuleError("Command '%s' is not defined." % first_arg)
