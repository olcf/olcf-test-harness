============
Contributing
============

Collaboration for the improvement of the OLCF Test Harness is greatly appreciated and highly encouraged.
Contributions in the form of bug reports, feature requests, and source-code contributions are all efficient methods of contributing.

Reporting Bugs
==============

Please report bugs to the `OTH GitHub Repository <https://github.com/olcf/olcf-test-harness>`_ Issues page.
Include the following information in your Issue:

- What are you trying to do?
- Command-line usage (ie, ``runtests.py -i rgt.inp ...``)
- Standard output & error from running
- The contents of your harness input file (ie, *rgt.inp*)
- The contents of your machine configuration file (*<machine>.ini*)
- The contents of your test input file (*rgt_test_input.ini*)
- The contents of all logs in **$RESULTS_DIR/LogFiles**


Requesting New Features
=======================

To request a new feature (ie, new command-line flag, support for a new scheduler), please submit an Issue to the `OTH GitHub Repository <https://github.com/olcf/olcf-test-harness>`_ Issues page.
Please add **Feature Request:** to the beginning of your issue title to help the development team quickly identify the request.
Include the following information in your request:

- What do you want the OTH to do? ("I would like the OTH to ...")
- Is the lack of this feature blocking your usage of the OTH?
- How do you want to invoke the new feature? (ie, environment variable, command-line flag, configuration file parameter)


Contributing Source Code
========================

Source-code contribution is welcomed through GitHub Pull Requests to the `OTH GitHub Repository <https://github.com/olcf/olcf-test-harness>`_ Pull Requests page.
For PRs that fix bugs or implement a new feature, please cite the specific Issue in the body of the PR.
To create a PR, please follow the following steps:

- Fork the OTH GitHub Repository to your personal GitHub account
- Clone your fork of the OTH:

.. code-block::

    git clone https://github.com/<your-username>/olcf-test-harness.git
    cd olcf-test-harness
    git checkout devel

- From your fork's ``devel`` branch, point the upstream to the OTH GitHub repo:

.. code-block::

    git remote add olcf https://github.com/olcf/olcf-test-harness.git
    git fetch olcf
    git branch --set-upstream-to=olcf/devel

- Update your local fork from the upstream repository:

.. code-block::

    git checkout devel
    git pull

- Create a new branch in your fork of the OTH GitHub: ``git checkout -b issue64-fix``
- Make your edits
- Add and commit your edits to your branch

.. code-block::

    git add file1.py file.py ...
    git commit -m "Message summarizing your changes"

- Push your edits to your fork: ``git push -u origin issue64-fix``
- Open a Pull Request on `OTH Pull Requests <https://github.com/olcf/olcf-test-harness/pull>`_

A Developer Guide is currently under construction that will contain more information regarding code formatting.
In the meantime, please use the following basic formatting rules:

- Use 4-space indentation
- Use lowercase variable names with underscores (ie ``example_var``)
- Add comments to explain any non-trivial code
- Avoid hard-coding paths. Use existing class variables to specify paths and file names.

.. note::

    All Pull Requests will undergo review from the OTH development team.
    PRs implementing new features will be evaluated for utility provided to the OTH.
    Approval and integration of new features into the OTH is at the discretion of the development team.

