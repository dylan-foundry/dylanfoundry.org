Windows: Current State of Support
#################################

:author: Bruce Mitchener, Jr.
:date: 2013-01-23
:tags: Platform Support

Related to the recent post `Why is the OpenDylan IDE only on Windows?`_,
another source of common questions are some of the requirements that we
have for running on Windows and the state of 64 bit Windows support.

Building Open Dylan Applications on Windows
===========================================

Building an Open Dylan application on any platform requires at least a
linker. On Windows, it also requires a resource compiler for handling
``.rc`` files which controls things like an applications icons.

On Windows, we support debugging an application written in Dylan when
using the Open Dylan IDE. To do this, we must have the debug data
available.  Our debug data on Windows is in `CodeView 4`_ (CV4) format rather
than the more modern PDBs in use today.  This is partially a historical
artifact of the fact that this code was written in the 1990s and partially
due to the later formats not being publicly specified.

So, to link on Windows and support debugging, we need a linker that supports
CV4 debug data.  Unfortunately, Microsoft removed support for this in their
linkers after Visual C 6.  However, the `PellesC`_ linker, ``polink`` does
support CV4 debug data.

PellesC also provides a resource compiler, ``porc.exe``.

PellesC provides a complete toolchain that allows for Dylan applications to
be linked and debugged.  Using more recent versions of Visual Studio may
allow linking a Dylan application, but it will not work with the debugger.
Using Visual C 6 is possible, but it is no longer available and requires
using a Windows SDK from 2003 as more recent ones don't work with Visual C 6.

Hopefully it is clear that the easiest thing to do currently is to use
the PellesC toolchain for linking and debugging Dylan applications on Windows.

In the future, we hope to integrate aspects of the PellesC distribution
into our installer to make this a seamless and easy installation.

Building Open Dylan on Windows
==============================

Much of this is the same as the above, except that we currently have to
use Visual C 6 for a full bootstrap rather than PellesC.

The issue at play here is that the low-level runtime code includes the
excellent `MPS`_ garbage collector from `Ravenbrook`_.  There is some
code within MPS that triggers a bug in PellesC.  We are also using a
slightly older version of MPS as the current version triggers a different
set of bugs in Visual C 6 due to MPS having support for 64 bit Windows.

We are working on producing a minimized test case of the issues with
compiling MPS with PellesC so that we can eventually use PellesC to
build a full bootstrap of the Open Dylan IDE. This will also allow us
to upgrade to the current versions of MPS which are faster and more stable.

Running the Open Dylan IDE on 64-bit Windows
============================================

The Open Dylan IDE does not run on 64-bit Windows prior to Windows 8.
This is due to a bug in a low level portion of Windows known as "WoW64"
which had a bug in an API call ``GetThreadContext``. This breaks many
garbage collectors when trying to run a 32-bit application on 64-bit
Windows while using threads. Our IDE uses threads and, since it is built
for 32-bit Windows, has fallen victim to this issue.

However, the command line tools do not use threads and are able to
run on 64-bit Windows.

We do not currently support producing a 64-bit build of Open Dylan on
Windows because we use a compiler backend on Windows that produces native
code.  Our 64-bit platform support comes from using a compiler backend
that generates C, but that backend doesn't support Windows.  This situation
will hopefully improve with the upcoming LLVM compiler backend which
will make it easier for us to generate 64-bit Windows code, although
we will then have some exciting problems to solve surrounding debugging.

Hopefully this helps clarify the current status and where we're going
in the future!

.. _Why is the OpenDylan IDE only on Windows?: ../18/why-is-the-opendylan-ide-only-on-windows/
.. _CodeView 4: http://en.wikipedia.org/wiki/CodeView
.. _PellesC: http://www.smorgasbordet.com/pellesc/
.. _MPS: http://www.ravenbrook.com/project/mps/
.. _Ravenbrook: http://www.ravenbrook.com/
