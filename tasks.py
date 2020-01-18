from os.path import join

from invocations import docs
from invocations.pytest import test, integration
from invocations.packaging import release

from invoke import Collection


ns = Collection(test, integration, release, docs)
ns.configure({
    'packaging': {
        'sign': True,
        'wheel': True,
        'changelog_file': join(
            docs.ns.configuration()['sphinx']['source'],
            'changelog.rst',
        ),
    },
})
