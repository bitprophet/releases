from invocations import docs
from invocations.testing import test
from invocations.packaging import release

from invoke import Collection
from invoke import run
from invoke import task


@task()
def integration_tests():
    """Runs integration tests."""
    run('inv test -o --tests=integration')


ns = Collection(test, integration_tests, release, docs)
