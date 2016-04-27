from docutils import nodes
from semantic_version import Version as StrictVersion, Spec


class Version(StrictVersion):
    """
    Version subclass toggling ``partial=True`` by default.
    """
    def __init__(self, version_string, partial=True):
        super(Version, self).__init__(version_string, partial)


def default_spec(families):
    """
    Given iterable of major release numbers, return a default Spec for issues.

    Specifically:

    * Normally, only the highest major release is used, so given ``[1, 2]``
      this will simply return something like ``Spec(">=2")``.
    * When ``releases_always_forwardport`` is ``True``, that behavior is
      nullified, and this function always returns the empty ``Spec`` (which
      matches any and all versions/lines).
    """
    default = Spec()
    if True: # TODO: if app->config-><releases_always_forwardport or w/e
        default = Spec(">={0}".format(max(families)))
    return default


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
    def backported(self):
        return self.get('backported', False)

    @property
    def major(self):
        return self.get('major', False)

    @property
    def number(self):
        return self.get('number', None)

    @property
    def line(self):
        return self.get('line', None)

    def add_to_lines(self, lines):
        """
        Given a 'lines' structure, add self to one or more of its 'buckets'.
        """
        # Derive version spec allowing us to filter against major/minor buckets
        if self.line:
            spec = Spec(">={0}".format(self.line))
        else:
            spec = default_spec(lines.keys())
        # Only look in appropriate major version/family; if self is an issue
        # declared as living in e.g. >=2, this means we don't even bother
        # looking in the 1.x family.
        families = [Version(str(x)) for x in lines]
        for version in spec.filter(families):
            family = version.major
            # Within each family, we further limit which bugfix lines match up
            # to what self cares about (ignoring 'unreleased' until later)
            candidates = [
                Version(x)
                for x in lines[family]
                if not x.startswith('unreleased')
            ]
            # TODO: handle actual spec-like bits, self.line currently is only
            # looking for the '+' format...
            # Select matching release lines (& stringify)
            buckets = []
            bugfix_buckets = [str(x) for x in spec.filter(candidates)]
            # Add back in unreleased_* as appropriate
            # TODO: probably leverage Issue subclasses for this eventually?
            if self.type == 'bug' or self.backported:
                buckets.extend(bugfix_buckets)
                buckets.append('unreleased_bugfix')
            if self.type != 'bug' or self.major:
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
        elif self.line:
            flag = self.line + '+'
        if flag:
            flag = ' ({0})'.format(flag)
        return '<{issue.type} #{issue.number}{flag}>'.format(issue=self,
                                                             flag=flag)


class Release(nodes.Element):
    @property
    def number(self):
        return self['number']

    @property
    def line(self):
        # TODO: use Version
        return '.'.join(self.number.split('.')[:-1])

    @property
    def family(self):
        # TODO: use Version.major
        # TODO: and probs just rename to .major, 'family' is dumb tbh
        return int(self.number.split('.')[0])

    def __repr__(self):
        return '<release {0}>'.format(self.number)
