from docutils import nodes
from semantic_version import Version as StrictVersion, Spec


class Version(StrictVersion):
    """
    Version subclass toggling ``partial=True`` by default.
    """
    def __init__(self, version_string, partial=True):
        super(Version, self).__init__(version_string, partial)


def default_spec(lines):
    """
    Given iterable of line identifiers, return the default Spec for issues.

    Specifically:

    * By default, only the latest major version family is used in default
      Specs, so if something calling this has "seen" a 2.0.x release pass by,
      it will return a Spec like ``>=2.0``.
    * When ``releases_always_forwardport`` is ``True``, that behavior is
      nullified, and this function always returns the empty ``Spec`` (which
      matches any and all versions/lines).
    """
    # TODO: actually support always_forwardport or w/e we end up calling it
    return Spec()


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

    def filter_lines(self, lines):
        """
        Given iterable of lines like "1.2", return those this issue belongs in.

        The lines may include 'unreleased' labels like 'unreleased_bugfix' and
        these will be considered correctly (e.g. regular bugs will filter into
        'unreleased_bugfix', features into 'unreleased_feature', etc.)
        """
        # NOTE: 'Blank' Spec objects match all versions/lines.
        # TODO: update this to implement 'default to latest major' behavior, by
        # testing what the latest major version is within 'lines', then
        # treating blank 'line' issues as if they were Spec('>=<that line>')
        # instead of Spec(). (Keeping Spec() if that setting is false.)

        # Strip out unreleased_* as they're not real versions
        candidates = [x for x in lines if not x.startswith('unreleased')]
        if self.line:
            spec = Spec(">={0}".format(self.line))
        else:
            spec = default_spec(candidates)
        # Select matching release lines (& stringify)
        bug_lines = map(str, spec.filter(Version(x) for x in candidates))
        # Add back in unreleased_bugfix
        # TODO: make this work for features too...
        bug_lines.append('unreleased_bugfix')
        return bug_lines

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

    def __repr__(self):
        return '<release {0}>'.format(self.number)
