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

Generating Bitcode
------------------

In Dylan, `Peter Housel`_ opted to, instead, model the LLVM IR and
then generate `bitcode`_ files from it. This is all wrapped up
pretty neatly within a `Dylan library, llvm`_. At the time of this
writing, that library is slightly dated as his most recent work has
not yet landed on the master branch in the main Open Dylan repository.

When building LLVM IR, there are methods whose names start with ``ins--``
for each of the instructions, as well as some that perform additional
work to simplify the process of building the IR. These functions are
used with an instance of ``<llvm-builder>``, of which ``<llvm-back-end>``
is a subclass.

For a brief example, the Dylan compiler has a variety of primitives
which express low-level concepts. For example, to cast a machine word
to a floating point value, we have
``primitive-cast-machine-word-as-single-float``, which is implemented
in the LLVM backend as:

.. code-block:: dylan

   define side-effect-free stateless dynamic-extent
     &primitive-descriptor
     primitive-cast-machine-word-as-single-float
       (b :: <raw-machine-word>)
    => (f :: <raw-single-float>)
     let f-bits = if (back-end-word-size(be) = 4)
                    b
                  else
                    ins--trunc(be, b, $llvm-i32-type)
                  end if;
     ins--bitcast(be, f-bits, $llvm-float-type)
   end;

This shows a ``&primitive-descriptor`` with a couple of adjectives
(``side-effect-free``, ``stateless``, ``dynamic-extent``) which are
used by other parts of the compiler, and when the compiler is generating
code and sees a call to this primitive, it instead emits the code as
described in the body of the primitive:

* If the target platform is 32 bits, then use the given raw machine word
  value. Otherwise, truncate it to a 32 bit integer (``$llvm-i32-type``).
* Then, emit a bitcast of that value to the LLVM float type
  (``$llvm-float-type``).

One minor note is that the variable ``be`` above is bound to an instance
of ``<llvm-back-end>`` via a bit of macro magic.

Generating some sorts of control flow structures can be tedious due to
things like `phi instructions`_. Peter Housel cleverly added some macros
to make this far more natural, as we can see some this snippet, which
comes from some code that implements ``instance?`` checks for ``<boolean>``
values:

.. code-block:: dylan

   // Compare against #f
   let false-cmp
     = ins--icmp-eq(back-end, object, emit-reference(back-end, m, &false));
   ins--if (back-end, false-cmp)
     $llvm-true
   ins--else
     // Compare against #t
     ins--icmp-eq(back-end, object, emit-reference(back-end, m, &true))
   end ins--if;

Here, we can see the usage of a new control flow structure in the Dylan
code, ``ins--if ... ins--else ... end ins--if`` which simplifies the
emission of conditional code as LLVM IR.

Generating Machine Code
-----------------------

Now that bitcode files are being generated, the next step is to generate
actual machine code in the form of executables or shared libraries. This
can readily be done by invoking ``clang`` or ``llc`` on the bitcode files.
Additional optimization passes can be run by running ``opt`` (or just
relying upon the behavior of ``clang -Ox``).

JIT Compilation
---------------

We haven't yet worked out a strategy for handling JIT compilation.
Our old compiler backend on Windows supported this with the help
of the Open Dylan debugger and we will re-visit similar solutions
in the future once everything else is working.

The odds are that we'll be able to accomplish this by invoking
``clang -c`` and then using our existing "spy" routines within the
run-time to load the resulting code into the running application.
We'll want to look at supporting the `GDB JIT interface`_ to
let the debugger be able to find the debug info for the newly
compiled code.

Downsides?
----------

There are a couple of possible downsides with this approach.

One is that things occasionally change and require updates to the bitcode
generation or the IR modeling code. To date, this hasn't been too
terrible. This is also true when new LLVM has new intrinsics or
annotations added.

The other is that we haven't yet dealt with versioning the bitcode
generation code, instead assuming that we're using a relatively current
version of LLVM. In the future, we may want to be able to target
differing versions of LLVM. (This isn't readily doable when linking
directly against LLVM, so our ability to consider this in the future
is an advantage.)

These downsides don't seem all that serious in practice though,
especially once the initial investment of writing something like
the Dylan ``llvm`` library has been made.

In Closing
==========

Open Dylan has a (nearly working) LLVM backend that generates its
own model of the LLVM IR and emits bitcode files from that. By doing
this, it is able to avoid any link-time dependency directly upon
the LLVM libraries. It is able to invoke ``clang`` to generate
machine code as needed.

By avoiding direct use of the C++ or C APIs to LLVM, it is able
to be more flexible in terms of how it integrates with LLVM and
which version or build must be used.

This is a different approach taken from many other languages which
have implemented LLVM backends, but it is one that appears to have
an interesting set of trade-offs that others may find interesting.

.. _CLASP: https://github.com/drmeister/clasp
.. _Clang: http://clang.llvm.org/
.. _FFI: http://en.wikipedia.org/wiki/Foreign_function_interface
.. _Peter Housel: https://twitter.com/peterhousel
.. _bitcode: http://llvm.org/docs/BitCodeFormat.html
.. _Dylan library, llvm: https://github.com/dylan-lang/opendylan/tree/master/sources/lib/llvm
.. _phi instructions: http://llvm.org/docs/LangRef.html#phi-instruction
.. _GDB JIT interface: https://sourceware.org/gdb/current/onlinedocs/gdb/JIT-Interface.html
