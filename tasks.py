from invocations import docs
from invocations.testing import test
from invocations.packaging import release

from invoke import Collection
from invoke import run
from invoke import task


@task(help={
    'pty': "Whether to run tests under a pseudo-tty",
})
def integration(pty=True):
    """Runs integration tests."""
    cmd = 'inv test -o --tests=integration'
    run(cmd + ('' if pty else ' --no-pty'), pty=pty)


ns = Collection(test, integration, release, docs)
