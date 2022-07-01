### Deployment
To trigger deployment, you must create a PR and merge to master.
The deployment workflow will run on every push to master:

### Version

The published version is set by a file: [VERSION.txt](./VERSION.txt)

You must check in a new VERSION.txt file of A Semantic Version form:  a version numbered MAJOR.MINOR.PATCH

example: 0.0.7

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

On merge to master, a workflow runs that builds the package based on the version:

to see what that version will be on your local machine:

``` shell
pipenv run python setup.py --version
```

### infx-content-client
Client needs to be able to:
 - Load the most recent active version of a value set, given the name of the value set
 - List of all available versions of a value set, given the name of the value set (as JSON or pandas DataFrame)
 - Load a previous version of a value set, given the ID of that specific version
