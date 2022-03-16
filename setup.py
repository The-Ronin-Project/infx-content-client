from setuptools import setup

setup(
    name='infx_api',
    packages=['infx_api'],
    use_scm_version = {
        "local_scheme": "no-local-version"
    },
    setup_requires=['setuptools_scm'],
)
