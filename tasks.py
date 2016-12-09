from os.path import join

from invocations import docs
from invocations.testing import test, integration, watch_tests
from invocations.packaging import release

from invoke import Collection


ns = Collection(test, integration, watch_tests, release, docs)
ns.configure({
    'tests': {
        'package': 'releases',
    },
    'packaging': {
        'sign': True,
        'wheel': True,
        'changelog_file': join(
            docs.ns.configuration()['sphinx']['source'],
            'changelog.rst',
        ),
    },
})
