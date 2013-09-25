import re

from docutils.parsers.rst import roles
from docutils import nodes, utils


# Issue type list (keys) + color values
issue_types = {
    'bug': 'A04040',
    'feature': '40A056',
    'support': '4070A0',
}

def issues_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Use: :issue|bug|feature|support:`ticket_number`

    When invoked as :issue:, turns into just a "#NN" hyperlink to Github.

    When invoked otherwise, turns into "[Type] <#NN hyperlink>: ".

    May give a 'ticket number' of '<number> backported' to indicate a
    backported feature or support ticket. This extra info will be stripped out
    prior to parsing. May also give 'major' in the same vein, implying the bug
    was a major bug released in a feature release.
    """
    #from ipdb import set_trace; set_trace()
    # Old-style 'just the issue link' behavior
    issue_no, _, ported = utils.unescape(text).partition(' ')
    # Lol @ access back to Sphinx
    config = inliner.document.settings.env.app.config
    ref = config.releases_issue_uri % issue_no
    link = nodes.reference(rawtext, '#' + issue_no, refuri=ref, **options)
    # Additional 'new-style changelog' stuff
    if name in issue_types:
        which = '[<span style="color: #%s;">%s</span>]' % (
            issue_types[name], name.capitalize()
        )
        nodelist = [
            nodes.raw(text=which, format='html'),
            nodes.inline(text=" "),
            link,
            nodes.inline(text=":")
        ]
        # Sanity check
        if ported not in ('backported', 'major', ''):
            raise ValueError("Gave unknown issue metadata '%s' for issue no. %s" % (ported, issue_no))
        # Create temporary node w/ data & final nodes to publish
        node = issue(
            number=issue_no,
            type_=name,
            nodelist=nodelist,
            backported=(ported == 'backported'),
            major=(ported == 'major'),
        )
        return [node], []
    # Return old style info for 'issue' for older changelog entries
    else:
        return [link], []


def release_nodes(text, slug, date, config):
    my_nodes = [
        nodes.reference(
            text=text,
            refuri=config.releases_release_uri % slug,
        ),
    ]
    if date:
        my_nodes.extend([
            nodes.inline(text=' '),
            nodes.raw(text='<span style="font-size: 75%%;">%s</span>' % date, format='html'),
        ])
    return nodes.section('',
        nodes.title('', '', *my_nodes),
        ids=[text]
    )


year_arg_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)

def release_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Invoked as :release:`N.N.N <YYYY-MM-DD>`.

    Turns into useful release header + link to GH tree for the tag.
    """
    # Make sure year has been specified
    match = year_arg_re.match(text)
    if not match:
        msg = inliner.reporter.error("Must specify release date!")
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    number, date = match.group(1), match.group(2)
    # Lol @ access back to Sphinx
    config = inliner.document.settings.env.app.config
    nodelist = [release_nodes(number, number, date, config)]
    # Return intermediate node
    node = release(number=number, date=date, nodelist=nodelist)
    return [node], []


class issue(nodes.Element):
    @property
    def type(self):
        return self['type_']

    @property
    def backported(self):
        return self['backported']

    @property
    def major(self):
        return self['major']

    @property
    def number(self):
        return self.get('number', None)

class release(nodes.Element):
    @property
    def number(self):
        return self['number']


def get_line(obj):
    # 1.2.7 -> 1.2
    return '.'.join(obj.number.split('.')[:-1])

def construct_releases(entries, app):
    # Walk from back to front, consuming entries & copying them into
    # per-release buckets as releases are encountered. Store releases in order.
    releases = []
    lines = {'unreleased': []}
    for obj in reversed(entries):
        # The 'actual' intermediate object we want to focus on is wrapped first
        # in a LI, then a P.
        focus, rest = obj[0][0], obj[0][1:]
        # Releases 'eat' the entries in their line's list and get added to the
        # final data structure. They also inform new release-line 'buffers'.
        # Release lines should have an empty 'rest' so it's ignored.
        if isinstance(focus, release):
            line = get_line(focus)
            # New release line/branch detected. Create it & dump unreleased into
            # this new release. Skip non-major bugs.
            if line not in lines:
                lines[line] = []
                releases.append({
                    'obj': focus,
                    'entries': [
                        x
                        for x in lines['unreleased'] 
                        if x.type in ('feature', 'support') or x.major
                    ]
                })
                lines['unreleased'] = []
            # Existing line -> empty out its bucket into new release.
            # Skip 'major' bugs as those "belong" to the next release.
            else:
                releases.append({
                    'obj': focus,
                    'entries': [x for x in lines[line] if not x.major],
                })
                lines[line] = []
        # Entries get copied into release line buckets as follows:
        # * Everything goes into 'unreleased' so it can be used in new lines.
        # * Bugfixes (but not support or feature entries) go into all release
        # lines, not just 'unreleased'.
        # * However, support/feature entries marked as 'backported' go into all
        # release lines as well, on the assumption that they were released to
        # all active branches.
        # * The 'rest' variable (which here is the bug description, vitally
        # important!) is preserved by stuffing it into the focus (issue)
        # object.
        else:
            # Handle rare-but-valid non-issue-attached line items, which are
            # always bugs. (They are their own description.)
            if not isinstance(focus, issue):
                focus = issue(type_='bug', nodelist=[focus], backported=False, major=False, description=[])
            else:
                focus.attributes['description'] = rest
            if focus.type == 'bug':
                # Regular bugs go into per-line buckets only.
                if not focus.major:
                    for line in [x for x in lines if x != 'unreleased']:
                        lines[line].append(focus)
                # Major bugs go into feature release bucket only.
                else:
                    lines['unreleased'].append(focus)
            else:
                # Backported feature/support items go into all lines.
                if focus.backported:
                    for line in lines:
                        lines[line].append(focus)
                # Non-backported feature/support items go into feature releases
                # only.
                else:
                    lines['unreleased'].append(focus)

    # Entries not yet released get special 'release' entries (that lack an
    # actual release object).
    nodelist = [release_nodes("Unreleased", "master", None, app.config)]
    releases.append({
        'obj': release(number='unreleased', date=None, nodelist=nodelist),
        'entries': lines['unreleased']
    })
    return releases


def construct_nodes(releases):
    result = []
    # Reverse the list again so the final display is newest on top
    for d in reversed(releases):
        if not d['entries']:
            continue
        obj = d['obj']
        entries = []
        for entry in d['entries']:
            # Use nodes.Node.deepcopy to deepcopy the description
            # nodes.  If this is not done, multiple references to the same
            # object (e.g. a reference object in the description of #649, which
            # is then copied into 2 different release lists) will end up in the
            # doctree, which makes subsequent parse steps very angry (index()
            # errors).
            desc = list(map(lambda x: x.deepcopy(), entry['description']))
            # Additionally, expand any other issue roles found in the
            # description paragraph - sometimes we refer to related issues
            # inline. (They can't be left as issue() objects at render time
            # since that's undefined.)
            for i, node in enumerate(desc[:]): # Copy to avoid self-mutation during loop
                if isinstance(node, issue):
                    desc[i:i+1] = node['nodelist']
            # Tack on to end of this entry's own nodelist (which is the link +
            # etc)
            entries.append(
                nodes.list_item('',
                    nodes.paragraph('', '', *entry['nodelist'] + desc)
                )
            )
        # Entry list
        list_ = nodes.bullet_list('', *entries)
        # Insert list into release nodelist (as it's a section)
        obj['nodelist'][0].extend(list_)
        # Release header
        header = nodes.paragraph('', '', *obj['nodelist'])
        result.extend(header)
    return result


def generate_changelog(app, doctree):
    # This seems to be the cleanest way to tell what a not-fully-parsed
    # document's 'name' is. Also lol @ not fully implementing dict protocol.
    source = doctree.children[0]
    if 'changelog' not in source.get('names', []):
        return
    # Second item inside main document is the 'modern' changelog bullet-list
    # object, whose children are the nodes we care about.
    changelog = source.children.pop(1)
    # Walk + parse into release mapping
    releases = construct_releases(changelog.children, app)
    # Construct new set of nodes to replace the old, and we're done
    source.children[1:1] = construct_nodes(releases)


def setup(app):
    # Issue base URI setting: releases_issue_uri
    # E.g. 'https://github.com/fabric/fabric/issues/'
    app.add_config_value(name='releases_issue_uri', default=None,
        rebuild='html')
    # Release-tag base URI setting: releases_release_uri
    # E.g. 'https://github.com/fabric/fabric/tree/'
    app.add_config_value(name='releases_release_uri', default=None,
        rebuild='html')
    # Register intermediate roles
    for x in list(issue_types) + ['issue']:
        app.add_role(x, issues_role)
    app.add_role('release', release_role)
    # Hook in our changelog transmutation at appropriate step
    app.connect('doctree-read', generate_changelog)
