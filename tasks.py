from invocations import docs
from invocations.testing import test
from invocations.packaging import release

from invoke import Collection

ns = Collection(test, release, docs)
