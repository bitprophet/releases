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
        # Normally, we have separate buckets for bugfixes vs features
        keys = ['unreleased_bugfix', 'unreleased_feature']
        # But unstable prehistorical releases roll all up into just
        # 'unreleased'
        if major_number == 0 and self.config.releases_unstable_prehistory:
            keys = ['unreleased']
        # Either way, the buckets default to an empty list
        empty = {}
        for key in keys:
            empty[key] = []
        self[major_number] = empty

    @property
    def unstable_prehistory(self):
        """
        Returns True if 'unstable prehistory' behavior should be applied.

        Specifically, checks config & whether any non-0.x releases exist.
        """
        return (
            self.config.releases_unstable_prehistory
            and not self.has_stable_releases
        )

    @property
    def stable_families(self):
        """
        Returns release family numbers which aren't 0 (i.e. prehistory).
        """
        return [x for x in self if x != 0]

    @property
    def has_stable_releases(self):
        """
        Returns whether stable (post-0.x) releases seem to exist.
        """
        nonzeroes = self.stable_families
        # Nothing but 0.x releases -> yup we're prehistory
        if not nonzeroes:
            return False
        # Presumably, if there's >1 major family besides 0.x, we're at least
        # one release into the 1.0 (or w/e) line.
        if len(nonzeroes) > 1:
            return True
        # If there's only one, we may still be in the space before its N.0.0 as
        # well; we can check by testing for existence of bugfix buckets
        return any(
            x for x in self[nonzeroes[0]] if not x.startswith('unreleased')
        )
