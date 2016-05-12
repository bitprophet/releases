# TODO: un-subclass dict in favor of something more explicit, once all regular
# dict-like access has been factored out into methods
class LineManager(dict):
    """
    Manages multiple release lines/families as well as related config state.
    """
    def __init__(self, app):
        """
        Initialize new line manager dict.

        :param app: The core Sphinx app object. Mostly used for config.
        """
        super(LineManager, self).__init__()
        self.app = app

    @property
    def config(self):
        """
        Return Sphinx config object.
        """
        return self.app.config

    def add_family(self, major_number):
        """
        Expand to a new release line with given ``major_number``.

        This will flesh out mandatory buckets like ``unreleased_bugfix`` and do
        other necessary bookkeeping.
        """
        self[major_number] = {
            'unreleased_bugfix': [],
            'unreleased_feature': [],
        }
