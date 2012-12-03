Dylan Foundry website
#####################

This website uses the `Pelican <http://getpelican.com/>`_ static site
generator.

To build this repository, install Pelican. I do this with ``virtualenv``
and have included a ``requirements.txt`` with the packages that I've
installed.

The theme is pulled in via a git submodule. Be sure to either
clone this repository recursively or initialize and update
submodules::

    git submodule update --init
