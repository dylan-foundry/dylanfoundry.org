Why is the OpenDylan IDE only on Windows?
#########################################

:author: Bruce Mitchener, Jr.
:tags: IDE, Platform Support

We're often asked when the IDE will show up on Linux or Mac OS X.

Unfortunately, the answer to this is rather complex because the IDE
consists of multiple pieces, all of which have separate portability
issues.

------

The Existing IDE
================

DUIM - The GUI Framework
------------------------

The biggest reason that the IDE is only on Windows is that it uses
the DUIM framework which hasn't yet been ported away from Windows
in a functioning and well-maintained manner. (An experimental GTK+
port has existed in the past, but it doesn't currently compile.)

Code Browsers and Inspectors
----------------------------

The code browsers and inspectors pull their information from frameworks
that are independent of the GUI. It is possible to use this information
separately from the IDE itself. The `DIME`_ environment for emacs supplies
some of this functionality. The `Hula`_ project (now defunct) provided
some of this functionality as well via a web-based interface.

This is actually an exciting set of features that our compiler provides.
While many other languages have to glue IDE functionality on as a separate
set of libraries, Open Dylan's compiler supports it internally from the
ground up.

Debugging
---------

The debugger depends on a couple of key components:

* A debugger nub that provides the actual debugging functionality.
* The debug information generated during compilation.

A new debugger nub would need to be written for each supported
platform or an interface would need to be built that allowed the
use of `lldb`_ or GDB's machine interface (``gdb-mi``).

The bigger issue however is the Dylan-level debug information. On
Mac OS X and on 64 bit platforms, we use a C compiler backend, so there
is no Dylan-level debug information at all.  On 32 bit Linux and FreeBSD
where we use HARP, we are also missing debug info due to how we generate
the assembly (among other reasons).

Combined, this makes it difficult for the debugger to work away
from Windows.

REPL / Listener
---------------

In the OpenDylan IDE, the REPL or listener was built on top of the
debugger interfaces.  Without the debugger, that code won't work.

------

Future Directions
=================

We aren't satisfied with the status quo and would love to see it change.

WINE
----

Some components of the Windows IDE actually work under WINE (1.5 and later).
However, this tends to crash a lot and the debugger doesn't work as WINE
doesn't implement that aspect of the Windows APIs.

LLVM
----

The upcoming LLVM compiler backend features much improved support for debug
information generation. This, combined with `lldb`_, should result in debugging
being possible. It is likely that some work will need to be done for this to
work well.

DIME / Emacs
------------

There are many improvements to `DIME`_ that could be made.

Web-based Tools
---------------

Much like `Hula`_ demonstrated, we can build a new web-based tool for doing
code browsing, inspecting libraries and other traditional IDE functions. We
can even use it to integrate documentation.

Porting the existing IDE
------------------------

Porting the existing IDE would mean getting DUIM up and running on other
platforms. This is doable but would require a substantial amount of work.
DUIM has also aged and hasn't kept up with all the things that modern
toolkits can do.

On top of that, it lacks some features like syntax highlighting that might
be easier to provide in other ways.

A new REPL
----------

We're investigating some options for a new REPL. These include using the
LLVM backend and using a JIT, using the existing backend and loading
shared libraries, and the more appealing option of using `DynASM`_
from LuaJIT.

Sublime Text
------------

Sublime Text is a popular editor these days and other languages have built
IDE-like extensions for it. We could do the same for Dylan as well, perhaps
sharing some of the backend code with `DIME`_.

Other Ideas
-----------

It is likely that other people will find new and interesting ways to apply
our compiler frameworks and we'd enjoy seeing what other people are interested
in trying out.

Projects like `Light Table`_, the `iPython Notebook`_ and others show that
there is a lot of fertile ground for exploration and experimentation.

------

Moving Forward
==============

We'd love to hear what people think should happen next.

In the short term, we're working on the LLVM backend so that we can gain
debugging support on more platforms (among other benefits from the LLVM
backend).

It would be wonderful to see some volunteers to help out with some of
these projects. There's a lot of exciting and potentially groundbreaking
work that can be done and we're more than happy to help provide guidance and
direct assistance.

We'll be covering some of these items in more depth soon! Be sure
to follow `@DylanFoundry`_ or our `RSS feed`_.

.. _DIME: http://opendylan.org/news/2011/12/12/dswank.html
.. _Hula: http://turbolent.github.com/hula-presentation/
.. _lldb: http://lldb.llvm.org/
.. _DynASM: http://luajit.org/dynasm.html
.. _@DylanFoundry: https://twitter.com/DylanFoundry
.. _RSS feed: http://dylanfoundry.org/feeds/all.atom.xml
.. _Light Table: http://www.lighttable.com/
.. _iPython Notebook: http://ipython.org/ipython-doc/dev/interactive/htmlnotebook.html
