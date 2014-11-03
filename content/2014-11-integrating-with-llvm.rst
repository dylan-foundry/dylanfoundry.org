Integrating with LLVM
#####################

:author: Bruce Mitchener, Jr.
:date: 2014-11-10
:tags: LLVM
:status: draft

Many compilers are now being outfitted with LLVM backends. There are
a variety of ways to do this, and we'll take a look at some of them
here.

Calling LLVM APIs Directly
==========================

One common and easy way to integrate with LLVM is to directly link
against the LLVM libraries and invoke the LLVM API directly.

C++ API
-------

LLVM's native APIs are C++. Examples of languages that talk to LLVM
via the C++ APIs are Julia and `CLASP`_.

This is also the approach taken by `Clang`_, however, Clang lives
within the same code repository as LLVM and shares many developers.
It is part of the LLVM project rather than a separate compiler
that is using LLVM as a backend.

While this seems like an attractive option, there are some issues
with it:

* Your code must either be written in C++ or be able to invoke C++
  code via an `FFI`_ (foreign function interface).
* You are tied to a particular version of the LLVM API at compile
  time.
* It is harder to re-use someone's existing installation of LLVM
  as you are tied to a particular version.

C API
-----

LLVM also provides a C wrapper around the C++ APIs. This is intended
to be used by others who want to use LLVM, but don't want to directly
use the C++ APIs for whatever reason.

The C API is also intended to be a more stable API over time as it
exposes fewer details and avoids some of the complexity inherent
in providing a C++ API.

While the C API improves upon some of the issues with the C++ API,
it isn't without its own issues:

* Not everything possible with the C++ API is possible with the C API.
* This means that you'll have to work with the upstream LLVM team
  to make extensions and get them into a new release.

Other Bindings
--------------

There are bindings for LLVM available in a variety of languages with
prominent bindings being those written in Go and OCaml. Using these
assumes that your code is written in one of those languages and usually
has the same drawbacks as using either the C or C++ APIs (depending
on which APIs the bindings are using).

Another Path?
=============

There's another path that can be taken however that gets us away from
having to link directly with LLVM libraries and invoking the LLVM
APIs, whatever the language involved.


.. _CLASP: https://github.com/drmeister/clasp
.. _Clang: http://clang.llvm.org/
.. _FFI: http://en.wikipedia.org/wiki/Foreign_function_interface
