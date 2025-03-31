======================
Notational Conventions
======================

.. toctree::
   :maxdepth: 1

We shall adopt the conventions used in the book Learning the bash Shell [NR1998]_:

    - The *italic* font is used for filenames, directories, non-unix shell commands, and shell
      functions.

    - The **bold** font is used for shell built-in commands, variables,
      options, command lines when they are within regular text, and text to 
      be typed in by the user within regular text.

    -  ``Constant width`` font is used for file content.

The following text demonstrates some of the conventions.

We shall create a Bash program called *helloWold.sh*. Create program file with the
following text using the *vi* editor:

::

    #!/usr/bin/env bash

    declare -gr message='Hello World'
    printf "%s\n" "${message}" 

It will be necessary to set executable permission on *helloWorld.sh* by typing 
**chmod +x ./helloWorld.sh** . After setting executable permission, run as follows:

    **./helloWorld.sh**

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

