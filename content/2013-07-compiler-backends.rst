Open Dylan's Compiler Back-ends
###############################

:author: Bruce Mitchener, Jr.
:date: 2013-07-18

Open Dylan has 3 compiler back-ends currently:

* HARP
* C
* LLVM

Harp
====

The HARP back-end generates native code for x86 processes and is used
on Windows, FreeBSD and Linux. While for many years, this was our best
and most mature compiler back-end, it is falling by the wayside and will
be replaced by the LLVM back-end.

The issues with the HARP back-end is that it is 32-bit only and is
more difficult to add support for things like new instructions, better
scheduling, atomic operations and SSE support.

C
=

The C back-end generates C which is then compiled by either clang or gcc.
We use the C back-end on Mac OS X, as well as Linux and FreeBSD on x86_64
processors.

The C back-end is relatively easy to work with and extend and is the
easiest option for bringing up Open Dylan on a new platform. We are currently
doing this with Linux on the ARM processor.

The C back-end used to generate code that was slower than HARP although
in recent months, the C back-end has been optimized and many parts of it
produce faster results than HARP.

The C back-end allows debugging the generated C (rather than at the Dylan
source level).

LLVM
====

The LLVM back-end is still a work in progress. This will replace the use
of the HARP and C back-ends on Mac OS X, Linux, FreeBSD and Windows on
both x86 and x86_64 processors.

The LLVM compiler back-end is much easier to maintain and generates
significantly better code than either of the other back-ends. It is also
much easier than HARP to extend to support new processors features and
things like atomic and SSE operations.

The LLVM back-end will enable debugging at the Dylan source level as it
emits DWARF debug data and will be functional with LLDB.

We hope that the LLVM back-end will be ready for use this calendar year
although some challenges remain on Windows and with debugger support.
