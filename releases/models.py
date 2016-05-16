from functools import reduce
from operator import xor

from docutils import nodes
from semantic_version import Version as StrictVersion, Spec
import six


class Version(StrictVersion):
    """
    Version subclass toggling ``partial=True`` by default.
    """
    def __init__(self, version_string, partial=True):
        super(Version, self).__init__(version_string, partial)


# Issue type list (keys) + color values
ISSUE_TYPES = {
    'bug': 'A04040',
    'feature': '40A056',
    'support': '4070A0',
}


class Issue(nodes.Element):
    # Technically, we just need number, but heck, you never know...
    _cmp_keys = ('type', 'number', 'backported', 'major')

    @property
    def type(self):
        return self['type_']

    @property
    def is_featurelike(self):
        if self.type == 'bug':
            return self.major
        else:
            return not self.backported

    @property
    def is_buglike(self):
        return not self.is_featurelike

    @property
    def backported(self):
        return self.get('backported', False)

    @property
    def major(self):
        return self.get('major', False)

    @property
    def number(self):
        return self.get('number', None)

    @property
    def spec(self):
        return self.get('spec', None)

    def __eq__(self, other):
        for attr in self._cmp_keys:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __hash__(self):
        return reduce(xor, [hash(getattr(self, x)) for x in self._cmp_keys])

    def minor_releases(self, manager):
        """
        Return all minor release line labels found in ``manager``.
        """
        # TODO: yea deffo need a real object for 'manager', heh. E.g. we do a
        # very similar test for "do you have any actual releases yet?"
        # elsewhere. (This may be fodder for changing how we roll up
        # pre-major-release features though...?)
        return [
            key for key, value in six.iteritems(manager)
            if any(x for x in value if not x.startswith('unreleased'))
        ]

    def default_spec(self, manager):
        """
        Given the current release-lines structure, return a default Spec.

        Specifics:

        * For feature-like issues, only the highest major release is used, so
          given a ``manager`` with top level keys of ``[1, 2]``, this would
          return ``Spec(">=2")``.

            * When ``releases_always_forwardport_features`` is ``True``, that
              behavior is nullified, and this function always returns the empty
              ``Spec`` (which matches any and all versions/lines).

        * For bugfix-like issues, we only consider major release families which
          have actual releases already.

            * Thus the core difference here is that features are 'consumed' by
              upcoming major releases, and bugfixes are not.

        * When the ``unstable_prehistory`` setting is ``True``, the default
          spec starts at the oldest non-zero release line. (Otherwise, issues
          posted after prehistory ends would try being added to the 0.x part of
          the tree, which makes no sense in unstable-prehistory mode.)
        """
        # TODO: I feel like this + the surrounding bits in add_to_manager()
        # could be consolidated & simplified...
        specstr = ""
        # Make sure truly-default spec skips 0.x if prehistory was unstable.
        stable_families = manager.stable_families
        if manager.config.releases_unstable_prehistory and stable_families:
            specstr = ">={0}".format(min(stable_families))
        if self.is_featurelike:
            # TODO: if app->config-><releases_always_forwardport_features or
            # w/e
            if True:
                specstr = ">={0}".format(max(manager.keys()))
        else:
            # Can only meaningfully limit to minor release buckets if they
            # actually exist yet.
            buckets = self.minor_releases(manager)
            if buckets:
                specstr = ">={0}".format(max(buckets))
        return Spec(specstr) if specstr else Spec()

    def add_to_manager(self, manager):
        """
        Given a 'manager' structure, add self to one or more of its 'buckets'.
        """
        # Derive version spec allowing us to filter against major/minor buckets
        spec = self.spec or self.default_spec(manager)
        # Only look in appropriate major version/family; if self is an issue
        # declared as living in e.g. >=2, this means we don't even bother
        # looking in the 1.x family.
        families = [Version(str(x)) for x in manager]
        versions = list(spec.filter(families))
        for version in versions:
            family = version.major
            # Within each family, we further limit which bugfix lines match up
            # to what self cares about (ignoring 'unreleased' until later)
            candidates = [
                Version(x)
                for x in manager[family]
                if not x.startswith('unreleased')
            ]
            # Select matching release lines (& stringify)
            buckets = []
            bugfix_buckets = [str(x) for x in spec.filter(candidates)]
            # Add back in unreleased_* as appropriate
            # TODO: probably leverage Issue subclasses for this eventually?
            if self.is_buglike:
                buckets.extend(bugfix_buckets)
                # Don't put into JUST unreleased_bugfix; it implies that this
                # major release/family hasn't actually seen any releases yet
                # and only exists for features to go into.
                if bugfix_buckets:
                    buckets.append('unreleased_bugfix')
            # Obtain list of minor releases to check for "haven't had ANY
            # releases yet" corner case, in which case ALL issues get thrown in
            # unreleased_feature for the first release to consume.
            # NOTE: assumes first release is a minor or major one,
            # but...really? why would your first release be a bugfix one??
            no_releases = not self.minor_releases(manager)
            if self.is_featurelike or self.backported or no_releases:
                buckets.append('unreleased_feature')
            # Now that we know which buckets are appropriate, add ourself to
            # all of them. TODO: or just...do it above...instead...
            for bucket in buckets:
                manager[family][bucket].append(self)

    def __repr__(self):
        flag = ''
        if self.backported:
            flag = 'backported'
        elif self.major:
            flag = 'major'
        elif self.spec:
            flag = self.spec
        if flag:
            flag = ' ({0})'.format(flag)
        return '<{issue.type} #{issue.number}{flag}>'.format(issue=self,
                                                             flag=flag)


class Release(nodes.Element):
    @property
    def number(self):
        return self['number']

    @property
    def minor(self):
        # TODO: use Version
        return '.'.join(self.number.split('.')[:-1])

    @property
    def family(self):
        # TODO: use Version.major
        # TODO: and probs just rename to .major, 'family' is dumb tbh
        return int(self.number.split('.')[0])

    def __repr__(self):
        return '<release {0}>'.format(self.number)
