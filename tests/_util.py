from docutils.nodes import (
    list_item, paragraph,
)
from mock import Mock
from spec import eq_, ok_
import six

from releases import (
    Issue,
    issues_role,
    Release,
    release_role,
    construct_releases,
)
from releases.util import make_app, changelog2dict


def inliner(app=None):
    app = app or make_app()
    return Mock(document=Mock(settings=Mock(env=Mock(app=app))))

# Obtain issue() object w/o wrapping all parse steps
def issue(type_, number, **kwargs):
    text = str(number)
    if kwargs.get('backported', False):
        text += " backported"
    if kwargs.get('major', False):
        text += " major"
    if kwargs.get('spec', None):
        text += " (%s)" % kwargs['spec']
    app = kwargs.get('app', None)
    return issues_role(
        name=type_,
        rawtext='',
        text=text,
        lineno=None,
        inliner=inliner(app=app),
    )[0][0]

# Even shorter shorthand!
def b(number, **kwargs):
    return issue('bug', str(number), **kwargs)

def f(number, **kwargs):
    return issue('feature', str(number), **kwargs)

def s(number, **kwargs):
    return issue('support', str(number), **kwargs)

def entry(i):
    """
    Easy wrapper for issue/release objects.

    Default is to give eg an issue/release object that gets wrapped in a LI->P.

    May give your own (non-issue/release) object to skip auto wrapping. (Useful
    since entry() is often called a few levels deep.)
    """
    if not isinstance(i, (Issue, Release)):
        return i
    return list_item('', paragraph('', '', i))

def release(number, **kwargs):
    app = kwargs.get('app', None)
    nodes = release_role(
        name=None,
        rawtext='',
        text='%s <2013-11-20>' % number,
        lineno=None,
        inliner=inliner(app=app),
    )[0]
    return list_item('', paragraph('', '', *nodes))

def release_list(*entries, **kwargs):
    skip_initial = kwargs.pop('skip_initial', False)
    entries = list(entries) # lol tuples
    # Translate simple objs into changelog-friendly ones
    for index, item in enumerate(entries):
        if isinstance(item, six.string_types):
            entries[index] = release(item)
        else:
            entries[index] = entry(item)
    # Insert initial/empty 1st release to start timeline
    if not skip_initial:
        entries.append(release('1.0.0'))
    return entries

def releases(*entries, **kwargs):
    app = kwargs.pop('app', None) or make_app()
    return construct_releases(release_list(*entries, **kwargs), app)[0]

def setup_issues(self):
    self.f = f(12)
    self.s = s(5)
    self.b = b(15)
    self.mb = b(200, major=True)
    self.bf = f(27, backported=True)
    self.bs = s(29, backported=True)

def expect_releases(entries, release_map, skip_initial=False, app=None):
    kwargs = {'skip_initial': skip_initial}
    # Let high level tests tickle config settings via make_app()
    if app is not None:
        kwargs['app'] = app
    changelog = changelog2dict(releases(*entries, **kwargs))
    snapshot = dict(changelog)
    err = "Got unexpected contents for {}: wanted {}, got {}"
    err += "\nFull changelog: {!r}\n"
    for rel, issues in six.iteritems(release_map):
        found = changelog.pop(rel)
        eq_(set(found), set(issues), err.format(rel, issues, found, snapshot))
    # Sanity: ensure no leftover issue lists exist (empty ones are OK)
    for key in list(changelog.keys()):
        if not changelog[key]:
            del changelog[key]
    ok_(not changelog, "Found leftovers: {}".format(changelog))
