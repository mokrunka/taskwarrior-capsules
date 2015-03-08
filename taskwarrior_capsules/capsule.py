import datetime
import subprocess
import warnings

from configobj import ConfigObj
import pytz
from verlib import NormalizedVersion

from . import __version__
from .exceptions import CapsuleProgrammingError


class TaskwarriorCapsuleBase(object):
    def get_taskwarrior_version(self):
        taskwarrior_version = subprocess.Popen(
            ['task', '--version'],
            stdout=subprocess.PIPE
        ).communicate()[0]
        return NormalizedVersion(taskwarrior_version)

    def get_taskwarrior_capsules_version(self):
        return NormalizedVersion(__version__)

    def validate(self, **kwargs):
        if not (self.MIN_VERSION and self.MAX_VERSION):
            warnings.warn(
                "Capsule '%s' does not specify compatible which "
                "taskwarrior-capsule versions it is compatible with; you may "
                "encounter compatibility problems. " % (
                    self.command_name
                )
            )
        else:
            curr_version = self.get_taskwarrior_capsules_version()
            min_version = NormalizedVersion(self.MIN_VERSION)
            max_version = NormalizedVersion(self.MAX_VERSION)

            if not min_version <= curr_version <= max_version:
                warnings.warn(
                    "Capsule '%s' is not compatible with version %s of "
                    "taskwarrior-capsules; "
                    "minimum version: %s; "
                    "maximum version %s." % (
                        self.command_name,
                        __version__,
                        min_version,
                        max_version,
                    ),
                )

        if not self.TASKWARRIOR_VERSION_CHECK_NECESSARY:
            # Let's just continue on without checking taskwarrior
            # version compatibility.
            pass
        elif not (
            self.MAX_TASKWARRIOR_VERSION and self.MIN_TASKWARRIOR_VERSION
        ):
            warnings.warn(
                "Capsule '%s' does not specify which taskwarrior versions it "
                "is compatible with; you may encounter compatibility "
                "problems. " % (
                    self.command_name
                )
            )
        else:
            tw_version = self.get_taskwarrior_version()
            min_tw_version = NormalizedVersion(self.MIN_TASKWARRIOR_VERSION)
            max_tw_version = NormalizedVersion(self.MAX_TASKWARRIOR_VERSION)

            if not min_tw_version <= tw_version <= max_tw_version:
                warnings.warn(
                    "Capsule '%s' is not compatible with version %s of "
                    "taskwarrior; "
                    "minimum version: %s; "
                    "maximum version %s." % (
                        self.command_name,
                        tw_version,
                        min_tw_version,
                        max_tw_version,
                    ),
                )

        return True


class CommandCapsule(TaskwarriorCapsuleBase):
    MIN_VERSION = None
    MAX_VERSION = None

    TASKWARRIOR_VERSION_CHECK_NECESSARY = True
    MIN_TASKWARRIOR_VERSION = None
    MAX_TASKWARRIOR_VERSION = None

    def __init__(self, meta, capsule_name, client, **kwargs):
        self.meta = meta
        self.capsule_name = capsule_name
        self.client = client
        super(CommandCapsule, self).__init__()

    @classmethod
    def get_summary(cls):
        doc = cls.__doc__ if cls.__doc__ else ''
        return doc.strip().split('\n')[0].strip()

    @property
    def configuration_filename(self):
        return self.meta.get_metadata_path(
            '%s.ini' % self.capsule_name,
        )

    @property
    def global_configuration(self):
        return self.meta.configuration

    @property
    def configuration(self):
        if not hasattr(self, '_config'):
            self._config = ConfigObj(self.configuration_filename)
        return self._config

    def get_description(self):
        try:
            return self.__doc__.strip()
        except AttributeError:
            raise None

    def get_matching_tasks(self, filter_args):
        filter_command = filter_args + ['status:pending', 'export']
        results = self.client._get_json(*filter_command)

        tasks = []
        for result in results:
            _, task = self.client.get_task(
                uuid=result['uuid']
            )
            tasks.append(task)

        return tasks

    def get_tasks_changed_since(self, since):
        """ Returns a list of tasks that were changed recently."""
        changed_tasks = []

        for task in self.client.filter_tasks({'status': 'pending'}):
            if task.get(
                'modified',
                task.get(
                    'entry',
                    datetime.datetime(2000, 1, 1).replace(tzinfo=pytz.utc)
                )
            ) >= since:
                changed_tasks.append(task)

        return changed_tasks

    def execute(
        self, variant, command_name, filter_args, extra_args, **kwargs
    ):
        self.validate(**kwargs)

        command_name_map = {
            'preprocessor': 'preprocess',
            'command': 'handle',
            'postprocessor': 'postprocess',
        }

        if hasattr(self, command_name_map.get(variant)):
            return getattr(
                self,
                command_name_map[variant]
            )(
                filter_args,
                extra_args,
                command_name=command_name,
                **kwargs
            )

        raise CapsuleProgrammingError(
            "%s was called as a %s but the %s method is not implemented!" % (
                self.__class__.__name__,
                variant,
                command_name_map[variant],
            )
        )

    def handle(self, filter_args, extra_args, **kwargs):
        raise NotImplementedError()
