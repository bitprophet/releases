from os.path import join

from invocations import docs, checks, travis
from invocations.pytest import test, integration
from invocations.packaging import release

from invoke import Collection


ns = Collection(test, integration, release, docs, travis, checks.blacken)
ns.configure(
    {
        "travis": {"black": {"version": "18.6b4"}},
        "packaging": {
            "sign": True,
            "wheel": True,
            "changelog_file": join(
                docs.ns.configuration()["sphinx"]["source"], "changelog.rst"
            ),
        },
    }
)
