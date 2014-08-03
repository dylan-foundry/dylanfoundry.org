Deepening LLDB Integration
##########################

:author: Bruce Mitchener, Jr.
:date: 2014-8-20
:tags: Debugging, LLDB
:status: draft

A `previous post`_ covered the subject of the initial LLDB and Dylan
integration. This post will dive a bit deeper into the future direction
of LLDB and Dylan integration.

Catching Up
===========

In the previous post, we talked about changing the base representation
from ``void*`` to ``uintptr_t`` to work around a bug in LLDB. This was,
in part, due to our goal to try to have the integration work with the
currently shipping version of LLDB.

Unfortunately, this work won't be completed and merged. In separate
developments, it has emerged that it can be unsafe to treat a pointer
as an integer when working with a garbage collector. The `details`_
of this are quite interesting, so out of an abundance of caution,
we will not be going down this route.

As such, we will be looking at improving LLDB integration by way
of modifying the LLDB sources to add support for Dylan.


.. _previous post: http://dylanfoundry.org/2014/06/25/integrating-with-lldb/
.. _details: http://mailman.ravenbrook.com/pipermail/mps-discussion/2014-July/000144.html
