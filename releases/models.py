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

    def default_spec(self, lines):
        """
        Given the current release-lines structure, return a default Spec.

        Specifics:

        * For feature-like issues, only the highest major release is used, so
          given a ``lines`` with top level keys of ``[1, 2]``, this would
          return ``Spec(">=2")``.

            * When ``releases_always_forwardport_features`` is ``True``, that
              behavior is nullified, and this function always returns the empty
              ``Spec`` (which matches any and all versions/lines).

        * For bugfix-like issues, we only consider major release families which
          have actual releases already.

            * Thus the core difference here is that features are 'consumed' by
              upcoming major releases, and bugfixes are not.
        """
        # TODO: I feel like this + the surrounding bits in add_to_lines() could
        # be consolidated & simplified...
        default = Spec()
        if self.is_featurelike:
            # TODO: if app->config-><releases_always_forwardport_features or w/e
            if True:
                default = Spec(">={0}".format(max(lines.keys())))
        else:
            # TODO: yea deffo need a real object for 'lines', heh
            default = Spec(">={0}".format(max(
                key for key, value in six.iteritems(lines)
                if any(x for x in value if not x.startswith('unreleased'))
            )))
        return default

    def add_to_lines(self, lines):
        """
        Given a 'lines' structure, add self to one or more of its 'buckets'.
        """
        # Derive version spec allowing us to filter against major/minor buckets
        spec = self.spec or self.default_spec(lines)
        # Only look in appropriate major version/family; if self is an issue
        # declared as living in e.g. >=2, this means we don't even bother
        # looking in the 1.x family.
        families = [Version(str(x)) for x in lines]
        versions = list(spec.filter(families))
        for version in versions:
            family = version.major
            # Within each family, we further limit which bugfix lines match up
            # to what self cares about (ignoring 'unreleased' until later)
            candidates = [
                Version(x)
                for x in lines[family]
                if not x.startswith('unreleased')
            ]
            # Select matching release lines (& stringify)
            buckets = []
            bugfix_buckets = [str(x) for x in spec.filter(candidates)]
            # Add back in unreleased_* as appropriate
            # TODO: probably leverage Issue subclasses for this eventually?
            if self.is_buglike:
                buckets.extend(bugfix_buckets)
                buckets.append('unreleased_bugfix')
            else:
                buckets.append('unreleased_feature')
            # Now that we know which buckets are appropriate, add ourself to
            # all of them. TODO: or just...do it above...instead...
            for bucket in buckets:
                lines[family][bucket].append(self)

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
