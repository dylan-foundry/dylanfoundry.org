Deepening LLDB Integration
##########################

:author: Bruce Mitchener, Jr.
:date: 2015-3-2
:tags: Debugging, LLDB
:status: draft

A `previous post`_ covered the subject of the initial LLDB and Dylan
integration.

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

We are able to use the "pointer depth" parameter to commands like
``expression`` and ``frame variable`` to show the "expanded" form of
objects::

  (lldb) frame variable -P 1 T15
  (dylan_value) T15 = 0x017e8000 {<buffer>} {
    [buffer-next] = 0x00000001 {<integer>: 0}
    [buffer-end] = 0x00000001 {<integer>: 0}
    [buffer-position] = 0x00000001 {<integer>: 0}
    [buffer-dirty?] = 0x001223e0 {<boolean>: #f}
    [buffer-start] = 0x00000001 {<integer>: 0}
    [buffer-on-page-bits] = 0x0000fffd {<integer>: 16383}
    [buffer-off-page-bits] = 0xffff0001 {<integer>: 1073725440}
    [buffer-use-count] = 0x00000001 {<integer>: 0}
    [buffer-owning-stream] = 0x001223e0 {<boolean>: #f}
    [buffer-element] = 0x00010001 {<integer>: 16384}
  }

More Summaries
==============

Since the last post, a number of new summaries have been added for
a variety of classes. Most of these are things internal to the
language run-time, but some are user-facing, like ``<machine-word>``
and ``<double-integer>``.

.. _previous post: http://dylanfoundry.org/2014/06/25/integrating-with-lldb/
.. _details: http://mailman.ravenbrook.com/pipermail/mps-discussion/2014-July/000144.html
