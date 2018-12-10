# Publishing Project Mu Pip Python Library

The MuPythonLibrary is published as a pypi (pip) module.  The pip module is named __mu_python_library__.  Pypi allows for easy version management, dependency management, and sharing.

Publishing/releasing a new version is generally handled thru a server based build process but for completeness the process is documented here.

## Steps

!!! Info
    These directions assume you have already configured your workspace for developing.  If not please first do that.  Directions on the [developing](developing.md) page.

1. Pass all development tests and check. Update the readme with info on changes for this version.
2. Get your changes into master branch (official releases should only be done from the master branch)
3. Make a git tag for the version that will be released.  Tag format is v<Major>.<Minor>.<Patch>
4. Do the release process

    1. Install tools
        ``` cmd
        pip install --upgrade -r requirements.publisher.txt
        ```
    2. Build a wheel
        ``` cmd
        python setup.py sdist bdist_wheel
        ```
    3. Confirm wheel version is aligned with git tag
        ``` cmd
        ConfirmVersionAndTag.py
        ```
    4. Publish the wheel/distribution to pypi
        ``` cmd
        twine upload dist/*
        ```
