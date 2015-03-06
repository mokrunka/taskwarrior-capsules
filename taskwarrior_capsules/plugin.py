import json

from verlib import NormalizedVersion

from . import __version__
from .exceptions import CapsuleProgrammingError


class PluginError(Exception):
    pass


class PluginValidationError(PluginError):
    pass


class PluginOperationError(PluginError):
    pass


class TaskwarriorCapsuleBase(object):
    def validate(self, **kwargs):
        if not self.MIN_VERSION or not self.MAX_VERSION:
            raise PluginValidationError(
                "Minimum and maximum version numbers not specified."
            )

        min_version = NormalizedVersion(self.MIN_VERSION)
        max_version = NormalizedVersion(self.MAX_VERSION)
        curr_version = NormalizedVersion(__version__)
        if not min_version <= curr_version <= max_version:
            raise PluginValidationError(
                "Plugin '%s' is not compatible with version %s of "
                "taskwarrior-capsules; "
                "minimum version: %s; "
                "maximum version %s.",
                (
                    self.plugin_name,
                    __version__,
                    self.MIN_VERSION,
                    self.MAX_VERSION,
                ),
            )

        return True


class Capsule(TaskwarriorCapsuleBase):
    MIN_VERSION = None
    MAX_VERSION = None

    def __init__(self, meta, plugin_name, **kwargs):
        self.meta = meta
        self.plugin_name = plugin_name

    @property
    def metadata_filename(self):
        return self.meta.get_metadata_path(
            'plugin_meta',
            '%s.json' % self.plugin_name,
        )

    def get_configuration(self):
        return self.meta.configuration[self.plugin_name]

    def get_metadata(self):
        try:
            with open(self.metadata_filename, 'r') as _in:
                return json.loads(_in.read())
        except (IOError, OSError):
            return {}

    def set_metadata(self, data):
        with open(self.metadata_filename, 'w') as out:
            out.write(
                json.dumps(
                    data,
                    indent=4,
                    sort_keys=True,
                )
            )


class CommandCapsule(Capsule):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_description(self):
        try:
            return self.__doc__.strip()
        except AttributeError:
            raise None

    def add_arguments(self, parser):
        pass

    def parse_arguments(self, parser, extra_args):
        return parser.parse_args(extra_args)

    @classmethod
    def execute(
        cls, variant, filter_args, extra_args, command_name, **kwargs
    ):
        cmd = cls(plugin_name=command_name)
        cmd.validate(**kwargs)

        command_name_map = {
            'preprocessor': 'preprocess',
            'command': 'handle',
            'postprocessor': 'postprocess',
        }

        if hasattr(cls, command_name_map.get(variant)):
            return getattr(
                cls,
                command_name_map[variant]
            )(
                filter_args,
                extra_args,
                command_name,
                **kwargs
            )

        raise CapsuleProgrammingError(
            "%s was called as a %s but the %s method is not implemented!" % (
                cls.__name__,
                variant,
                command_name_map[variant],
            )
        )

    def handle(self, folder, args, **kwargs):
        raise NotImplementedError()
