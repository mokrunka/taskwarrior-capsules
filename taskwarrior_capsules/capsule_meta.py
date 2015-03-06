import os

from configobj import ConfigObj


class CapsuleMeta(object):
    def __init__(self):
        try:
            os.mkdir(self.metadata_folder)
        except OSError:
            pass

    @property
    def metadata_folder(self):
        return os.path.expanduser('~/.taskwarrior-capsules')

    def get_metadata_path(self, *args):
        return os.path.join(
            self.metadata_folder,
            *args
        )

    @property
    def configuration(self):
        if not hasattr(self, '_config'):
            self._config = ConfigObj(
                self.get_metadata_path(
                    'capsules.conf'
                )
            )
        return self._config
