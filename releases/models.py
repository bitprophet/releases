from docutils import nodes


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

    @line.setter
    def line(self, value):
        self['line'] = value
        
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
