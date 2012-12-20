Getting Started with OpenDylan 2012.1
#####################################

:author: Bruce Mitchener, Jr.
:date: 2012-12-17
:tags: Tutorials

There are many `exciting changes <http://opendylan.org/documentation/release-notes/2012.1.html>`_
in the 2012.1 release of OpenDylan, but to me, some of the most exciting
changes are the ones that make it easier to get a new project going and
building.  We'll be writing more about that in the future, but for now,
let's look at how to get OpenDylan installed in the first place!

Installation
============

Linux and Mac OS X
------------------

Installing OpenDylan is pretty easy on Linux and Mac OS X.

1. First, you'll want to make sure that you have the basic developer
   tools like gcc installed.
2. On Gentoo, OpenDylan is available via the package system, so go
   ahead and install it that way. Packages for other operating
   systems are coming in the future and help is appreciated.
3. Otherwise, `download <http://opendylan.org/download/>`_ and install
   a build of OpenDylan for your operating system. Put OpenDylan
   in a directory of its own, like ``/opt/opendylan-2012.1``.
4. Make sure that the ``bin`` directory under the installation path
   is on your ``PATH``.  You can do this by placing a line in your
   ``.bashrc`` in your home directory like this::

     export PATH=/opt/opendylan-2012.1/bin:$PATH

   You can enter that command in your current shell as well.

Now is a good time to read over the documentation for the
`command line tools <http://opendylan.org/documentation/getting-started/console.html>`_.

Go ahead and build a ``hello-world`` application as described in the
documentation for the `command line tools <http://opendylan.org/documentation/getting-started/console.html>`_.

Windows
-------

While this tutorial is about the command line tools, we'll still
at least give you some pointers on getting started on Windows.

On Windows, things are a bit more involved.

1. First, you'll want to install `PellesC <http://www.smorgasbordet.com/pellesc/>`_.
   We need this compiler for handling linking executables. The reasons
   for needing this particular tool are fairly complicated.
2. Next, you can install OpenDylan and select the PellesC toolchain
   when prompted (rather than VC6 or other versions of Visual Studio).
3. When you want to run the OpenDylan IDE or command line tools, you'll
   need to do so from a PellesC Command Prompt or have added the PellesC
   environment variables to your system.

For further help getting started on Windows, we suggest reading
the `Getting Started <http://opendylan.org/documentation/getting-started/>`_
documentation for the IDE.

Learning More
=============

To learn more about Dylan, watch this blog as we'll be posting further
tutorials.  Also, check out this great documentation:

* `Introduction to Dylan <http://opendylan.org/documentation/intro-dylan/>`_:
   A tutorial is written primarily for those with solid programming
   experience in C++ or another object-oriented, static language. It
   provides a gentler introduction to Dylan than does the Dylan
   Reference Manual (DRM).
* `Dylan Reference Manual <http://opendylan.org/books/drm/>`_:
   The official definition of the Dylan language and standard library.
* `Dylan Programming Guide <http://opendylan.org/books/dpg/>`_:
   A good, book length Dylan tutorial.
* `OpenDylan Documentation <http://opendylan.org/documentation/>`_:
   All of the OpenDylan documentation.

Talk to Us!
===========

If you run into any problems, feel free to leave a comment here, talk to
us on IRC on #dylan on irc.freenode.net, or get in touch with us on our
`mailing list <http://opendylan.org/community/#mailing-lists>`_.

Good luck!
