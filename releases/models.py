from docutils import nodes
from semantic_version import Version as StrictVersion, Spec


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
        spec = Spec(">={0}".format(self.line)) if self.line else Spec()
        # Strip out unreleased_* as they're not real versions
        candidates = [x for x in lines if not x.startswith('unreleased')]
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
