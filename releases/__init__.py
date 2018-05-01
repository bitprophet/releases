import itertools
import re
import sys
from functools import partial

from docutils import nodes, utils
from docutils.parsers.rst import roles
import six

from .models import Issue, ISSUE_TYPES, Release, Version, Spec
from .line_manager import LineManager
from ._version import __version__


def _log(txt, config):
    """
    Log debug output if debug setting is on.

    Intended to be partial'd w/ config at top of functions. Meh.
    """
    if config.releases_debug:
        sys.stderr.write(str(txt) + "\n")
        sys.stderr.flush()


def issue_nodelist(name, identifier=None):
    which = '[<span style="color: #%s;">%s</span>]' % (
        ISSUE_TYPES[name], name.capitalize()
    )
    signifier = [nodes.raw(text=which, format='html')]
    id_nodelist = [nodes.inline(text=" "), identifier] if identifier else []
    trail = [] if identifier else [nodes.inline(text=" ")]
    return signifier + id_nodelist + [nodes.inline(text=":")] + trail


release_line_re = re.compile(r'^(\d+\.\d+)\+$') # e.g. '1.2+'

def scan_for_spec(keyword):
    """
    Attempt to return some sort of Spec from given keyword value.

    Returns None if one could not be derived.
    """
    # Both 'spec' formats are wrapped in parens, discard
    keyword = keyword.lstrip('(').rstrip(')')
    # First, test for intermediate '1.2+' style
    matches = release_line_re.findall(keyword)
    if matches:
        return Spec(">={}".format(matches[0]))
    # Failing that, see if Spec can make sense of it
    try:
        return Spec(keyword)
    # I've only ever seen Spec fail with ValueError.
    except ValueError:
        return None


def issues_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Use: :issue|bug|feature|support:`ticket_number`

    When invoked as :issue:, turns into just a "#NN" hyperlink to
    `releases_issue_uri`.

    When invoked otherwise, turns into "[Type] <#NN hyperlink>: ".

    Spaces present in the "ticket number" are used as fields for keywords
    (major, backported) and/or specs (e.g. '>=1.0'). This data is removed &
    used when constructing the object.

    May give a 'ticket number' of ``-`` or ``0`` to generate no hyperlink.
    """
    parts = utils.unescape(text).split()
    issue_no = parts.pop(0)
    # Lol @ access back to Sphinx
    config = inliner.document.settings.env.app.config
    if issue_no not in ('-', '0'):
        ref = None
        if config.releases_issue_uri:
            # TODO: deal with % vs .format()
            ref = config.releases_issue_uri % issue_no
        elif config.releases_github_path:
            ref = "https://github.com/{}/issues/{}".format(
                config.releases_github_path, issue_no)
        # Only generate a reference/link if we were able to make a URI
        if ref:
            identifier = nodes.reference(
                rawtext, '#' + issue_no, refuri=ref, **options
            )
        # Otherwise, just make it regular text
        else:
            identifier = nodes.raw(
                rawtext=rawtext, text='#' + issue_no, format='html',
                **options
            )
    else:
        identifier = None
        issue_no = None # So it doesn't gum up dupe detection later
    # Additional 'new-style changelog' stuff
    if name in ISSUE_TYPES:
        nodelist = issue_nodelist(name, identifier)
        spec = None
        keyword = None
        # TODO: sanity checks re: e.g. >2 parts, >1 instance of keywords, >1
        # instance of specs, etc.
        for part in parts:
            maybe_spec = scan_for_spec(part)
            if maybe_spec:
                spec = maybe_spec
            else:
                if part in ('backported', 'major'):
                    keyword = part
                else:
                    err = "Gave unknown keyword {!r} for issue no. {}"
                    raise ValueError(err.format(keyword, issue_no))
        # Create temporary node w/ data & final nodes to publish
        node = Issue(
            number=issue_no,
            type_=name,
            nodelist=nodelist,
            backported=(keyword == 'backported'),
            major=(keyword == 'major'),
            spec=spec,
        )
        return [node], []
    # Return old style info for 'issue' for older changelog entries
    else:
        return [identifier], []


def release_nodes(text, slug, date, config):
    # Doesn't seem possible to do this "cleanly" (i.e. just say "make me a
    # title and give it these HTML attributes during render time) so...fuckit.
    # We were already doing fully raw elements elsewhere anyway. And who cares
    # about a PDF of a changelog? :x
    uri = None
    if config.releases_release_uri:
        # TODO: % vs .format()
        uri = config.releases_release_uri % slug
    elif config.releases_github_path:
        uri = "https://github.com/{}/tree/{}".format(
            config.releases_github_path, slug)
    # Only construct link tag if user actually configured release URIs somehow
    if uri:
        link = '<a class="reference external" href="{}">{}</a>'.format(
            uri, text,
        )
    else:
        link = text
    datespan = ''
    if date:
        datespan = ' <span style="font-size: 75%;">{}</span>'.format(date)
    header = '<h2 style="margin-bottom: 0.3em;">{}{}</h2>'.format(
        link, datespan)
    return nodes.section('',
        nodes.raw(rawtext='', text=header, format='html'),
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
    node = Release(number=number, date=date, nodelist=nodelist)
    return [node], []


def generate_unreleased_entry(header, line, issues, manager, app):
    log = partial(_log, config=app.config)
    nodelist = [release_nodes(
        header,
        # TODO: should link to master for newest family and...what
        # exactly, for the others? Expectation isn't necessarily to
        # have a branch per family? Or is there? Maybe there must be..
        'master',
        None,
        app.config
    )]
    log("Creating {!r} faux-release with {!r}".format(line, issues))
    return {
        'obj': Release(number=line, date=None, nodelist=nodelist),
        'entries': issues,
    }


def append_unreleased_entries(app, manager, releases):
    """
    Generate new abstract 'releases' for unreleased issues.

    There's one for each combination of bug-vs-feature & major release line.

    When only one major release line exists, that dimension is ignored.
    """
    for family, lines in six.iteritems(manager):
        for type_ in ('bugfix', 'feature'):
            bucket = 'unreleased_{}'.format(type_)
            if bucket not in lines: # Implies unstable prehistory + 0.x fam
                continue
            issues = lines[bucket]
            fam_prefix = "{}.x ".format(family) if len(manager) > 1 else ""
            header = "Next {}{} release".format(fam_prefix, type_)
            line = "unreleased_{}.x_{}".format(family, type_)
            releases.append(
                generate_unreleased_entry(header, line, issues, manager, app)
            )


def reorder_release_entries(releases):
    """
    Mutate ``releases`` so the entrylist in each is ordered by feature/bug/etc.
    """
    order = {'feature': 0, 'bug': 1, 'support': 2}
    for release in releases:
        entries = release['entries'][:]
        release['entries'] = sorted(entries, key=lambda x: order[x.type])


def construct_entry_with_release(focus, issues, manager, log, releases, rest):
    """
    Releases 'eat' the entries in their line's list and get added to the
    final data structure. They also inform new release-line 'buffers'.
    Release lines, once the release obj is removed, should be empty or a
    comma-separated list of issue numbers.
    """
    log("release for line %r" % focus.minor)
    # Check for explicitly listed issues first
    explicit = None
    if rest[0].children:
        explicit = [x.strip() for x in rest[0][0].split(',')]
    # Do those by themselves since they override all other logic
    if explicit:
        log("Explicit issues requested: %r" % (explicit,))
        # First scan global issue dict, dying if not found
        missing = [i for i in explicit if i not in issues]
        if missing:
            raise ValueError(
                "Couldn't find issue(s) #{} in the changelog!".format(
                    ', '.join(missing)))
        # Obtain the explicitly named issues from global list
        entries = []
        for i in explicit:
            for flattened_issue_item in itertools.chain(issues[i]):
                entries.append(flattened_issue_item)
        # Create release
        log("entries in this release: %r" % (entries,))
        releases.append({
            'obj': focus,
            'entries': entries,
        })
        # Introspect these entries to determine which buckets they should get
        # removed from (it's not "all of them"!)
        for obj in entries:
            if obj.type == 'bug':
                # Major bugfix: remove from unreleased_feature
                if obj.major:
                    log("Removing #%s from unreleased" % obj.number)
                    # TODO: consider making a LineManager method somehow
                    manager[focus.family]['unreleased_feature'].remove(obj)
                # Regular bugfix: remove from bucket for this release's
                # line + unreleased_bugfix
                else:
                    if obj in manager[focus.family]['unreleased_bugfix']:
                        log("Removing #%s from unreleased" % obj.number)
                        manager[focus.family]['unreleased_bugfix'].remove(obj)
                    if obj in manager[focus.family][focus.minor]:
                        log("Removing #%s from %s" % (obj.number, focus.minor))
                        manager[focus.family][focus.minor].remove(obj)
            # Regular feature/support: remove from unreleased_feature
            # Backported feature/support: remove from bucket for this
            # release's line (if applicable) + unreleased_feature
            else:
                log("Removing #%s from unreleased" % obj.number)
                manager[focus.family]['unreleased_feature'].remove(obj)
                if obj in manager[focus.family].get(focus.minor, []):
                    manager[focus.family][focus.minor].remove(obj)

    # Implicit behavior otherwise
    else:
        # Unstable prehistory -> just dump 'unreleased' and continue
        if manager.unstable_prehistory:
            # TODO: need to continue making LineManager actually OO, i.e. do
            # away with the subdicts + keys, move to sub-objects with methods
            # answering questions like "what should I give you for a release"
            # or whatever
            log("in unstable prehistory, dumping 'unreleased'")
            releases.append({
                'obj': focus,
                # NOTE: explicitly dumping 0, not focus.family, since this
                # might be the last pre-historical release and thus not 0.x
                'entries': manager[0]['unreleased'][:],
            })
            manager[0]['unreleased'] = []
            # If this isn't a 0.x release, it signals end of prehistory, make a
            # new release bucket (as is also done below in regular behavior).
            # Also acts like a sentinel that prehistory is over.
            if focus.family != 0:
                manager[focus.family][focus.minor] = []
        # Regular behavior from here
        else:
            # New release line/branch detected. Create it & dump unreleased
            # features.
            if focus.minor not in manager[focus.family]:
                log("not seen prior, making feature release & bugfix bucket")
                manager[focus.family][focus.minor] = []
                # TODO: this used to explicitly say "go over everything in
                # unreleased_feature and dump if it's feature, support or major
                # bug". But what the hell else would BE in unreleased_feature?
                # Why not just dump the whole thing??
                #
                # Dump only the items in the bucket whose family this release
                # object belongs to, i.e. 1.5.0 should only nab the 1.0
                # family's unreleased feature items.
                releases.append({
                    'obj': focus,
                    'entries': manager[focus.family]['unreleased_feature'][:],
                })
                manager[focus.family]['unreleased_feature'] = []

            # Existing line -> empty out its bucket into new release.
            # Skip 'major' bugs as those "belong" to the next release (and will
            # also be in 'unreleased_feature' - so safe to nuke the entire
            # line)
            else:
                log("pre-existing, making bugfix release")
                # TODO: as in other branch, I don't get why this wasn't just
                # dumping the whole thing - why would major bugs be in the
                # regular bugfix buckets?
                entries = manager[focus.family][focus.minor][:]
                releases.append({'obj': focus, 'entries': entries})
                manager[focus.family][focus.minor] = []
                # Clean out the items we just released from
                # 'unreleased_bugfix'.  (Can't nuke it because there might
                # be some unreleased bugs for other release lines.)
                for x in entries:
                    if x in manager[focus.family]['unreleased_bugfix']:
                        manager[focus.family]['unreleased_bugfix'].remove(x)


def construct_entry_without_release(focus, issues, manager, log, rest):
    # Handle rare-but-valid non-issue-attached line items, which are
    # always bugs. (They are their own description.)
    if not isinstance(focus, Issue):
        # First, sanity check for potential mistakes resulting in an issue node
        # being buried within something else.
        buried = focus.traverse(Issue)
        if buried:
            msg = """
Found issue node ({!r}) buried inside another node:

{}

Please double-check your ReST syntax! There is probably text in the above
output that will show you which part of your changelog to look at.

For example, indentation problems can accidentally generate nested definition
lists.
"""
            raise ValueError(msg.format(buried[0], str(buried[0].parent)))
        # OK, it looks legit - make it a bug.
        log("Found line item w/ no real issue object, creating bug")
        nodelist = issue_nodelist('bug')
        # Skip nodelist entirely if we're in unstable prehistory -
        # classification doesn't matter there.
        if manager.unstable_prehistory:
            nodelist = []
        # Undo the 'pop' from outer scope. TODO: rework things so we don't have
        # to do this dumb shit uggggh
        rest[0].insert(0, focus)
        focus = Issue(
            type_='bug',
            nodelist=nodelist,
            description=rest,
        )
    else:
        focus.attributes['description'] = rest

    # Add to global list (for use by explicit releases) or die trying
    issues[focus.number] = issues.get(focus.number, []) + [focus]

    # Add to per-release bugfix lines and/or unreleased bug/feature buckets, as
    # necessary.
    # TODO: suspect all of add_to_manager can now live in the manager; most of
    # Release's methods should probably go that way
    if manager.unstable_prehistory:
        log("Unstable prehistory -> adding to 0.x unreleased bucket")
        manager[0]['unreleased'].append(focus)
    else:
        log("Adding to release line manager")
        focus.add_to_manager(manager)


def handle_upcoming_major_release(entries, manager):
    # Short-circuit if the future holds nothing for us
    if not entries:
        return
    # Short-circuit if we're in the middle of a block of releases, only the
    # last release before a bunch of issues, should be taking any action.
    if isinstance(entries[0], Release):
        return
    # Iterate through entries til we find the next Release or set of Releases
    next_releases = []
    for index, obj in enumerate(entries):
        if isinstance(obj, Release):
            next_releases.append(obj)
        # Non-empty next_releases + encountered a non-release = done w/ release
        # block.
        elif next_releases:
            break
    # Examine result: is a major release present? If so, add its major number
    # to the line manager!
    for obj in next_releases:
        # TODO: update when Release gets tied closer w/ Version
        version = Version(obj.number)
        if version.minor == 0 and version.patch == 0:
            manager.add_family(obj.family)


def handle_first_release_line(entries, manager):
    """
    Set up initial line-manager entry for first encountered release line.

    To be called at start of overall process; afterwards, subsequent major
    lines are generated by `handle_upcoming_major_release`.
    """
    # It's remotely possible the changelog is totally empty...
    if not entries:
        return
    # Obtain (short-circuiting) first Release obj.
    first_release = None
    for obj in entries:
        if isinstance(obj, Release):
            first_release = obj
            break
    # It's also possible it's non-empty but has no releases yet.
    if first_release:
        manager.add_family(obj.family)
    # If God did not exist, man would be forced to invent him.
    else:
        manager.add_family(0)


def construct_releases(entries, app):
    log = partial(_log, config=app.config)
    # Walk from back to front, consuming entries & copying them into
    # per-release buckets as releases are encountered. Store releases in order.
    releases = []
    # Release lines, to be organized by major releases, then by major+minor,
    # alongside per-major-release 'unreleased' bugfix/feature buckets.
    # NOTE: With exception of unstable_prehistory=True, which triggers use of a
    # separate, undifferentiated 'unreleased' bucket (albeit still within the
    # '0' major line family).
    manager = LineManager(app)
    # Also keep a master hash of issues by number to detect duplicates & assist
    # in explicitly defined release lists.
    issues = {}

    reversed_entries = list(reversed(entries))
    # For the lookahead, so we're not doing this stripping O(n) times.
    # TODO: probs just merge the two into e.g. a list of 2-tuples of "actual
    # entry obj + rest"?
    stripped_entries = [x[0][0] for x in reversed_entries]
    # Perform an initial lookahead to prime manager with the 1st major release
    handle_first_release_line(stripped_entries, manager)
    # Start crawling...
    for index, obj in enumerate(reversed_entries):
        # Issue object is always found in obj (LI) index 0 (first, often only
        # P) and is the 1st item within that (index 0 again).
        # Preserve all other contents of 'obj'.
        focus = obj[0].pop(0)
        rest = obj
        log(repr(focus))
        # Releases 'eat' the entries in their line's list and get added to the
        # final data structure. They also inform new release-line 'buffers'.
        # Release lines, once the release obj is removed, should be empty or a
        # comma-separated list of issue numbers.
        if isinstance(focus, Release):
            construct_entry_with_release(
                focus, issues, manager, log, releases, rest
            )
            # After each release is handled, look ahead to see if we're
            # entering "last stretch before a major release". If so,
            # pre-emptively update the line-manager so upcoming features are
            # correctly sorted into that major release by default (re: logic in
            # Release.add_to_manager)
            handle_upcoming_major_release(
                stripped_entries[index + 1:], manager
            )

        # Entries get copied into release line buckets as follows:
        # * Features and support go into 'unreleased_feature' for use in new
        # feature releases.
        # * Bugfixes go into all release lines (so they can be printed in >1
        # bugfix release as appropriate) as well as 'unreleased_bugfix' (so
        # they can be displayed prior to release'). Caveats include bugs marked
        # 'major' (they go into unreleased_feature instead) or with 'N.N+'
        # (meaning they only go into release line buckets for that release and
        # up.)
        # * Support/feature entries marked as 'backported' go into all
        # release lines as well, on the assumption that they were released to
        # all active branches.
        # * The 'rest' variable (which here is the bug description, vitally
        # important!) is preserved by stuffing it into the focus (issue)
        # object - it will get unpacked by construct_nodes() later.
        else:
            construct_entry_without_release(focus, issues, manager, log, rest)

    if manager.unstable_prehistory:
        releases.append(generate_unreleased_entry(
            header="Next release",
            line="unreleased",
            issues=manager[0]['unreleased'],
            manager=manager,
            app=app,
        ))
    else:
        append_unreleased_entries(app, manager, releases)

    reorder_release_entries(releases)

    return releases, manager


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
            # node.  If this is not done, multiple references to the same
            # object (e.g. a reference object in the description of #649, which
            # is then copied into 2 different release lists) will end up in the
            # doctree, which makes subsequent parse steps very angry (index()
            # errors).
            desc = entry['description'].deepcopy()
            # Additionally, expand any other issue roles found in the
            # description - sometimes we refer to related issues inline. (They
            # can't be left as issue() objects at render time since that's
            # undefined.)
            # Use [:] slicing to avoid mutation during the loops.
            for index, node in enumerate(desc[:]):
                for subindex, subnode in enumerate(node[:]):
                    if isinstance(subnode, Issue):
                        lst = subnode['nodelist']
                        desc[index][subindex:subindex + 1] = lst
            # Rework this entry to insert the now-rendered issue nodes in front
            # of the 1st paragraph of the 'description' nodes (which should be
            # the preserved LI + nested paragraph-or-more from original
            # markup.)
            # FIXME: why is there no "prepend a list" method?
            for node in reversed(entry['nodelist']):
                desc[0].insert(0, node)
            entries.append(desc)
        # Entry list
        list_ = nodes.bullet_list('', *entries)
        # Insert list into release nodelist (as it's a section)
        obj['nodelist'][0].append(list_)
        # Release header
        header = nodes.paragraph('', '', *obj['nodelist'])
        result.extend(header)
    return result


class BulletListVisitor(nodes.NodeVisitor):
    def __init__(self, document, app):
        nodes.NodeVisitor.__init__(self, document)
        self.found_changelog = False
        self.app = app

    def visit_bullet_list(self, node):
        # The first found bullet list (which should be the first one at the top
        # level of the document) is the changelog.
        if not self.found_changelog:
            self.found_changelog = True
            # Walk + parse into release mapping
            releases, _ = construct_releases(node.children, self.app)
            # Construct new set of nodes to replace the old, and we're done
            node.replace_self(construct_nodes(releases))

    def unknown_visit(self, node):
        pass


def generate_changelog(app, doctree):
    # Don't scan/mutate documents that don't match the configured document name
    # (which by default is ['changelog.rst', ]).
    if app.env.docname not in app.config.releases_document_name:
        return

    # Find the first bullet-list node & replace it with our organized/parsed
    # elements.
    changelog_visitor = BulletListVisitor(doctree, app)
    doctree.walk(changelog_visitor)


def setup(app):
    for key, default in (
        # Issue base URI setting: releases_issue_uri
        # E.g. 'https://github.com/fabric/fabric/issues/'
        ('issue_uri', None),
        # Release-tag base URI setting: releases_release_uri
        # E.g. 'https://github.com/fabric/fabric/tree/'
        ('release_uri', None),
        # Convenience Github version of above
        ('github_path', None),
        # Which document to use as the changelog
        ('document_name', ['changelog']),
        # Debug output
        ('debug', False),
        # Whether to enable linear history during 0.x release timeline
        # TODO: flip this to True by default in our 2.0 release
        ('unstable_prehistory', False),
    ):
        app.add_config_value(
            name='releases_{}'.format(key), default=default, rebuild='html'
        )
    # if a string is given for `document_name`, convert it to a list
    # done to maintain backwards compatibility
    # https://stackoverflow.com/questions/1303243/how-to-find-out-if-a-python-object-is-a-string
    PY2 = sys.version_info[0] == 2
    if PY2:
        string_types = (basestring,)
    else:
        string_types = (str,)

    if isinstance(app.config.releases_document_name, string_types):
        app.config.releases_document_name = [app.config.releases_document_name]

    # Register intermediate roles
    for x in list(ISSUE_TYPES) + ['issue']:
        add_role(app, x, issues_role)
    add_role(app, 'release', release_role)
    # Hook in our changelog transmutation at appropriate step
    app.connect('doctree-read', generate_changelog)

    # identifies the version of our extension
    return {'version': __version__}


def add_role(app, name, role_obj):
    # This (introspecting docutils.parser.rst.roles._roles) is the same trick
    # Sphinx uses to emit warnings about double-registering; it's a PITA to try
    # and configure the app early on so it doesn't emit those warnings, so we
    # instead just...don't double-register. Meh.
    if name not in roles._roles:
        app.add_role(name, role_obj)
