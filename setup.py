from setuptools import setup

setup(
    name='infx_content_client',
    packages=['infx_content_client'],
    use_scm_version = {
        "local_scheme": "no-local-version"
    },
    setup_requires=['setuptools_scm'],
)
