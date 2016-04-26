from invocations import docs
from invocations.testing import test, integration, watch_tests
from invocations.packaging import release

from invoke import Collection
from invoke import run
from invoke import task


ns = Collection(test, integration, watch_tests, release, docs)
ns.configure({
    'tests': {
        'package': 'releases',
    },
})
