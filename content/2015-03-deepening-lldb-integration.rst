Deepening LLDB Integration
##########################

:author: Bruce Mitchener, Jr.
:date: 2015-3-2
:tags: Debugging, LLDB

A `previous post`_ covered the subject of the initial LLDB and Dylan
integration.

While much of this post discusses what we did to improve Dylan integration,
the overall techniques are broadly useful for many languages. In fact,
if anyone is interested, I am available for consulting on this topic.
Just email `me <bruce.mitchener@gmail.com>`_.

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

Expanding Objects
=================

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

Note that when using the ``expression`` command, you'll have to
use the ``--`` separator between options and the expression::

  (lldb) expr -P 1 -- (dylan_value)0x018154e0
  (dylan_value) $4 = 0x018154e0 {<string-table>} {
    [element-type] = 0x000e4854 {<class>: <object>}
    [table-vector] = 0x01ae9620 {<table-vector>}
    [initial-entries] = 0x00000029 {<integer>: 10}
    [grow-size-function] = 0x00133630 {<simple-method>}
    [weak?] = 0x000e46f0 {<boolean>: #f}
  }

Note here also that when we want to pretty print a Dylan object by address,
we must cast the address to ``(dylan_value)``. Unfortunately,
we also see here that we don't (yet) have a pretty printer for ``<table>``
objects.

Some features of LLDB don't work yet, like being able to use expression
paths with ``frame variable``::

  (lldb) frame variable T8->some-slot

We'll take this up on the LLDB side of things in the near future.

More Summaries
==============

Since the last post, a number of new summaries have been added for
a variety of classes. Most of these are things internal to the
language run-time, but some are user-facing, like ``<machine-word>``,
``<double-integer>``, ``<single-float>`` and ``<double-float>``.

Additionally, summaries were previously done so that they keyed off
of a value's class name. This was slow because of having to chase
through some pointers to get the string name. It was also unreliable
as multiple libraries might define something with the same name.
Summaries (and other things) now key off of an internal run-time
structure called the "wrapper". The wrapper contains information
about each class, but also information used by the garbage collector
for tracing object references, as well as some other data. Each
wrapper has a distinct symbol name using the Dylan name mangling,
so it will be a unique name within a process. This makes the
debugger integration both faster and more reliable.

Supporting LLVM and C back-ends
===============================

Another issue is that various parts of the debugger integration
scripts were using C debug information. When we're building code
with the LLVM back-end, that debug information won't be available
in the same way or with the same structure. To address this,
some changes were made to the code to stop using the C debug
data and to change to having a better understanding of the memory
layout of Dylan objects and directly working from that.

For example, we previously got the value for a Dylan symbol
with this code:

.. code-block:: python

  def dylan_symbol_name(value):
    target = lldb.debugger.GetSelectedTarget()
    symbol_type = target.FindFirstType('dylan_symbol').GetPointerType()
    value = value.Cast(symbol_type)
    return dylan_byte_string_data(value.GetChildMemberWithName('name'))

The new code is:

.. code-block:: python

  SYMBOL_NAME = 0

  def dylan_symbol_name(value):
    ensure_value_class(value, 'KLsymbolGVKdW', '<symbol>')
    name = dylan_slot_element(value, SYMBOL_NAME)
    return dylan_byte_string_data(name)

The difference here is that the ``dylan_symbol`` type was part of the
C run-time and not in the LLVM run-time. In the C run-time, we can
cast a value to ``dylan_symbol`` and then look for a member of that
struct named ``name``. In the LLVM run-time, that data simply isn't
available in that way. But we know that the name of a symbol will
always be in the first slot (0), so we can just access it directly.

This means that (hopefully) the debugger integration will work
with the upcoming LLVM compiler back-end without too much trouble.

Missing Debug Information
=========================

In a normal / default build, a lot of debug information is missing
due to optimization by the C compiler. We're still working on
addressing this.

Simplified Stack Traces
=======================

Getting a stack trace in LLDB from a Dylan program is pretty
intimidating::

  (lldb) bt
  * thread #1: tid = 0x84e7cb, 0x97e07736 libsystem_kernel.dylib`__read_nocancel + 10, queue = 'com.apple.main-thread', stop reason = signal SIGSTOP
    * frame #0: 0x97e07736 libsystem_kernel.dylib`__read_nocancel + 10
      frame #1: 0x003301b9 libio.dylib`Kunix_readYio_internalsVioI(fd_=0x00000001, data_=<unavailable>, offset_=0x00000001, count_=0x00010001) + 89 at unix-interface.c:561
      frame #2: 0x000b7b7f libdylan.dylib`xep_4(fn=0x00345d78, n=<unavailable>, a1=<unavailable>, a2=<unavailable>, a3=<unavailable>, a4=<unavailable>) + 271 at c-run-time.c:1163
      frame #3: 0x0032f6d4 libio.dylib`Kaccessor_read_intoXYstreams_internalsVioMM0I(accessor_=0x015a32a0, stream_=<unavailable>, offset_=<unavailable>, count_=<unavailable>, Urest_=0xbfff8a10, buffer_=<unavailable>) + 164 at unix-file-accessor.c:1710
      frame #4: 0x000be5c5 libdylan.dylib`key_mep_6(a1=0x015a32a0) + 501 at c-run-time.c:1691
      frame #5: 0x000c2490 libdylan.dylib`implicit_keyed_single_method_engine_4(a1=<unavailable>, a2=<unavailable>, a3=<unavailable>, a4=<unavailable>, optionals=0xbfff8a10) + 400 at c-run-time.c:2483
      frame #6: 0x000bfd2d libdylan.dylib`gf_optional_xep_4 [inlined] gf_iep_5(a1=0x015a32a0, a2=0x01564eb0, a3=0x00000001, a4=0x00010001) + 54 at c-run-time.c:1792
      frame #7: 0x000bfcf7 libdylan.dylib`gf_optional_xep_4(fn=<unavailable>, n=<unavailable>) + 311 at c-run-time.c:1929
      frame #8: 0x003180d1 libio.dylib`Kload_bufferYstreams_internalsVioI(the_stream_=0x01564eb0, the_buffer_=0x015b8000, desired_file_position_=<unavailable>, start_=0x00000001, count_=<unavailable>) + 305 at 14=file-stream.c:3934

That's pretty dense output and it isn't clear in an easy visual sense
which frames are actual Dylan methods and which are parts of the Dylan
run-time.

We've now added ``dylan-bt`` which presents a simplified stack trace::

  (lldb) dylan-bt
    frame #1    Kunix_readYio_internalsVioI                                  0x000000003301b9 libio.dylib at unix-interface.c:561
    frame #3    Kaccessor_read_intoXYstreams_internalsVioMM0I                0x0000000032f6d4 libio.dylib at unix-file-accessor.c:1710
    frame #8    Kload_bufferYstreams_internalsVioI                           0x000000003180d1 libio.dylib at 14=file-stream.c:3934

The ``-a`` parameter can be passed to show all frames, but with a visual
distinction between Dylan methods and methods from the run-time.

When using ``dylan-bt``, you may find it useful to use ``frame select ##``
in LLDB rather than ``up`` to directly select any given frame without
having to skip over the intervening Dylan run-time frames manually.

Breakpoints and Generic Functions
=================================

Another common thing that someone might want to do is to set a breakpoint
on a function. That's handled already by the breakpoint commands in
LLDB (although you need to know the mangled name of the function rather
than the Dylan name). It is useful to also be able to set a breakpoint
on every method in a generic function. For example, if you're not sure
which ``print-object`` method is calling called, then the ``dylan-break-gf``
command will prove useful::

  (lldb) dylan-break-gf print-object:print:io

That will set a breakpoint on all methods specializing ``print-object``
from the ``print`` module of the ``io`` library. For this to work, the
generic function will already have to have been initialized as well as
all of the methods on it. Because of that, your program will have to be
running prior to using ``dylan-break-gf``.

Future Additions
================

There are a lot of improvements that can be made in the future to
make debugging Dylan programs ever better.

* Add inspection facilities for inspecting classes and other run-time
  objects.
* Add support for pretty-printing function signatures. (This is a bit
  more complicated than it sounds due to the structure of this data
  within the run-time.)
* Add support for setting breakpoints on the Dylan names of functions
  and methods.
* Add support listing the methods on a generic function, including the
  mangled names of the methods to simplify setting breakpoints.
* Keep improving the set of summaries that are provided by default.

Modifying LLDB
==============

At some point in the future, we will take a further step towards
deepening our LLDB integration by writing C++ code to implement
direct support within LLDB for the Open Dylan run-time and object
layouts. This will provide for better performance and tighter
integration, but for now, we're still in the development stage of
debugger integration, so having the flexibility of working in
Python is still useful.

.. _previous post: http://dylanfoundry.org/2014/06/25/integrating-with-lldb/
.. _details: http://mailman.ravenbrook.com/pipermail/mps-discussion/2014-July/000144.html
