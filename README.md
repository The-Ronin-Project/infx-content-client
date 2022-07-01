### Deployment
To trigger deployment, you must create a PR and merge to master. You must also check in a new VERSION.txt file of the form  a version number MAJOR.MINOR.PATCH

example 0.0.6

increment the:

MAJOR version when you make incompatible API changes,
MINOR version when you add functionality in a backwards compatible manner, and
PATCH version when you make backwards compatible bug fixes.


Theoretically, Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

When you increment the version number, your version must also be a valid git tag or this workflow will fail.

Valid Semantic versioning passes as a tag.

We do not yet insure that you increment the version. not yet. You must do that.

### under the hood

We use setuptools_scm and dynamic loading of the VERSION.txt through pyproject.toml to build this package before we
publish it to nexus.

to test the build locally:

``` shell
pipenv install setuptools_scm setuptools_scm_git_semver
pipenv run python setup.py sdist bdist_wheel
```

### infx-content-client
Client needs to be able to:
 - Load the most recent active version of a value set, given the name of the value set
 - List of all available versions of a value set, given the name of the value set (as JSON or pandas DataFrame)
 - Load a previous version of a value set, given the ID of that specific version
