Binding nanomsg with melange
############################

:author: Bruce Mitchener, Jr.
:date: 2013-01-21
:tags: Tutorials, C-FFI, melange
:status: draft

For those who haven't heard about it, `nanomsg`_ is a great library
from Martin Sustrik. It provides high performance messaging with a
simple API similar to that of BSD sockets. It bears some similarity
to what someone might do with ZeroMQ and is licensed under the
liberal terms of the MIT license.

I have recently written bindings for it for use with Dylan which
are available as `nanomsg-dylan`_.

In Dylan, we have a couple of options when writing bindings. We
have a low level ``direct-c-ffi`` and a higher level `C-FFI`_.
Using the lower level interface is fairly tedious and verbose
while using C-FFI is fairly convenient.  But writing a binding
using either involves a lot of work and hand-translation of
the C APIs into the right Dylan definitions.

This is where the `melange`_ tool is very useful. Melange can
parse C headers and automatically generate the `C-FFI`_ bindings.
While doing this code generation, it also handles details like
automatically translations the C names into the correct Dylan
names following the Dylan conventions.

Using Melange
=============

Melange generates a Dylan file which contains `C-FFI`_ bindings.
This file will need to be compiled by the ``dylan-compiler``.
As part of that, you will want to provide the usual ``.lid``
and ``library.dylan`` files. We don't discuss these additional
files below, but a fully working setup can be seen in the
`nanomsg-dylan`_ repository on GitHub.

Melange is not a perfect tool and in particular, it does not
do a perfect job of parsing C. At times, it can be rather fiddly
and frustrating.  We plan to continue to improve upon it though
and welcome bug reports and patches.  Other aspects of it, such
as those discussed below, work remarkably well and should remain
largely the same in the future.

Getting Melange
===============

Melange isn't packaged yet, so you will have to clone the `melange
git repository`_.  After doing that, it should be a simple matter
of running ``make`` to produce a build of the ``melange`` executable.

You'll want to add the resulting ``_build/bin`` directory to your
``PATH`` environment variable. In the future, this will be more
straightforward.

The first draft
===============

I start out with a simple *interface definition*, ``nanomsg.intr``:

.. code-block:: dylan

    module: nanomsg

    define interface
      include {
        "sp/sp.h",
        "sp/fanin.h",
        "sp/inproc.h",
        "sp/pair.h",
        "sp/reqrep.h",
        "sp/survey.h",
        "sp/fanout.h",
        "sp/ipc.h",
        "sp/pubsub.h",
        "sp/tcp.h"
      },

      equate: {"char *" => <c-string>},

      import: all;

This tells melange to process that list of include files and import
all definitions found within them.  The ``equate:`` clause informs
melange that it should consider ``char *`` (and also ``const char *``)
to be the Dylan type ``<c-string>``.

Melange interface definition files use the file extension ``.intr``
by convention.

However, this will import some things that we don't need to bind
that are for internal use within ``nanomsg``.  To deal with this,
we introduce an ``exclude:`` clause:

.. code-block:: dylan

    module: nanomsg

    define interface
      include {
        ...
      },

      equate: {"char *" => <c-string>},

      import all,

      exclude: {
        "SP_HAUSNUMERO",
        "SP_PAIR_ID",
        "SP_PUBSUB_ID",
        "SP_REQREP_ID",
        "SP_FANIN_ID",
        "SP_FANOUT_ID",
        "SP_SURVEY_ID"
      };

We might also notice that not everything was imported into Dylan.
In particular, various functions are defined to cause ``sp-errno``
to return ``EAGAIN``, ``EADDRINUSE`` and other errors that are
defined by the OS.  They aren't imported because they aren't
defined with the headers that we're directly including.

The best way to get these imported is to specifically import them:

.. code-block:: dylan

      import: all,

      // Pick up the definitions that aren't defined by nanomsg itself.
      import: {
        "EADDRINUSE",
        "EADDRNOTAVAIL",
        "EAFNOSUPPORT",
        "EAGAIN",
        "EBADF",
        "EFAULT",
        "EINTR",
        "EINVAL",
        "EMFILE",
        "ENAMETOOLONG",
        "ENODEV",
        "ENOMEM",
        "ENOPROTOOPT",
        "ENOTSUP",
        "EPROTONOSUPPORT",
        "ETIMEDOUT"
      },

Input / Output Parameters
=========================

If we look at ``sp_version`` in the C headers, we'll see that it is
defined as:

.. code-block:: c

    SP_EXPORT void sp_version (int *major, int *minor, int *patch);

This is not so convenient when using it from Dylan.  We can simplify
this though by adding a function clause after the interface definition.
This function clause will help ``melange`` refine how the function
definition is mapped into Dylan's `C-FFI`_:

.. code-block:: dylan

    function "sp_version",
      output-argument: 1,
      output-argument: 2,
      output-argument: 3;

With this refinement in place, we can now call ``sp-version`` as follows:

.. code-block:: dylan

    let (major, minor, patch) = sp-version();

Awesome!

Improving upon error status codes
=================================

With a direct mapping of the C API into Dylan, we're left having to
handle error checking in the same way as the C API. This should be
enough to make us all feel a bit sad:

.. code-block:: dylan

    let res = sp-bind(sock, "inproc://test");
    if (res < 0)
      let error = sp-errno();
      // Do something
    end if;

Fixing this is a bit trickier.

What we want to do is say that the return type of these functions,
like ``sp-bind`` isn't merely an integer, but it is a special type
which has meaning when it is less than zero.  In Dylan's `C-FFI`_,
we call this a `C-mapped-subtype`_.  That sounds complicated, but
this code should make it more readily understandable:

.. code-block:: dylan

    define class <sp-error> (<error>)
      constant slot sp-error-status :: <integer>,
        required-init-keyword: status:;
      constant slot sp-error-message :: <string>,
        init-keyword: message:,
        init-value: "Unknown error";
    end;

    define C-mapped-subtype <sp-status> (<C-int>)
      import-map <integer>,
        import-function:
          method (result :: <integer>) => (checked :: <integer>)
            if ((result < 0) & (result ~= $EAGAIN))
              let errno = sp-errno();
              error(make(<sp-error>,
                         status: errno,
                         message: sp-strerror(errno)));
            else
              result;
            end;
          end;
    end;

Here we've just defined an error type, ``<sp-error>`` as well as our
``C-mapped-subtype``, ``<sp-status>``.  When we import a value that is
an ``<sp-status>``, the import function is called to help map the value
from C to Dylan.  In this case, if it is less than ``0`` and not
``$EAGAIN``, we signal an error.

In this case, we specifically exclude ``$EAGAIN`` as it isn't usually an
error when it occurs, such as when using the ``$SP-DONTWAIT`` flag.

Note that Melange interface files can include regular Dylan code which
will simply be directly copied to the generated Dylan file.

Now, we just need to add ``function`` clauses to specify that when to use
``<sp-status>`` as the result type:

.. code-block:: dylan

    function "sp_bind",
      map-result: <sp-status>;

    function "sp_close",
      map-result: <sp-status>;

Easy, once we know what we're doing, right? :)

Handling I/O
============

Another small difficulty to resolve is actually sending and receiving
data.

In C, the relevant functions look like:

.. code-block:: c

    SP_EXPORT int sp_send (int s, const void *buf, size_t len, int flags);
    SP_EXPORT int sp_recv (int s, void *buf, size_t len, int flags);

For now, we'll set up I/O using ``<buffer>`` from the I/O library.
Similar techniques can be used with ``<byte-vector>`` or ``<byte-string>``.

First, we're going to want to write wrappers around the ``sp-send`` and
``sp-recv`` functions, but we'd still like for our wrappers to keep those
names, so we'll rename the raw C-FFI functions, via a ``rename:`` clause
in our interface definition:

.. code-block:: dylan

    rename: {
      "sp_recv" => %sp-recv,
      "sp_send" => %sp-send
    };

Now, we can set up some wrapper methods:

.. code-block:: dylan

    define inline function sp-send
        (socket :: <integer>, data :: <buffer>,
         flags :: <integer>)
     => (res :: <integer>)
      %sp-send(...)
    end;

    define inline function sp-recv
        (socket :: <integer>, data :: <buffer>,
         flags :: <integer>)
     => (res :: <integer>)
      %sp-recv(...);
    end;

To actually pass data through to ``%sp-send`` and get it back from
``%sp-recv``, we need to do a little more work though.  We want to
get a pointer to the underlying storage within a ``<buffer>`` and
pass that to the C functions.

To do that, we define a new ``C-mapped-subtype`` and a helper function:

.. code-block:: dylan

    define simple-C-mapped-subtype <C-buffer-offset> (<C-void*>)
      export-map <machine-word>, export-function: identity;
    end;

    // Function for adding the base address of the repeated slots of a <buffer>
    // to an offset and returning the result as a <machine-word>.  This is
    // necessary for passing <buffer> contents across the FFI.

    define function buffer-offset
        (the-buffer :: <buffer>, data-offset :: <integer>)
     => (result-offset :: <machine-word>)
      u%+(data-offset,
          primitive-wrap-machine-word
            (primitive-repeated-slot-as-raw
               (the-buffer, primitive-repeated-slot-offset(the-buffer))))
    end function;

The function ``buffer-offset`` is using some low level primitives to
get at the internal storage and return the address as a ``<machine-word>``.
In this code, we don't use the ``data-offset``, but in cases where you want
to work with a subset of a buffer, it can be useful.

We'll have to tell melange that these functions want a ``<C-buffer-offset>``:

.. code-block:: dylan

    function "sp_recv",
      map-argument: { 2 => <C-buffer-offset> },
      map-result: <sp-status>;

    function "sp_send",
      map-argument: { 2 => <C-buffer-offset> },
      map-result: <sp-status>;

And now we can provide the full definition for ``sp-send`` and ``sp-recv``:

.. code-block:: dylan

    define inline function sp-send
        (socket :: <integer>, data :: <buffer>,
         flags :: <integer>)
     => (res :: <integer>)
      %sp-send(socket, buffer-offset(data, 0), data.size, flags)
    end;

     define inline function sp-recv
        (socket :: <integer>, data :: <buffer>,
         flags :: <integer>)
     => (res :: <integer>)
      %sp-recv(socket, buffer-offset(data, 0), data.size, flags);
    end;

Further Improvements
====================

Further improvements are possible:

- Define a specialized type that we use for sockets so that
  they can't be confused with regular integers.

- Provide custom wrappers around ``sp-setsockopt`` and
  ``sp-getsockopt`` to handle the data conversions involved.

- Do something to improve the experience of using the
  zero-copy nanomsg APIs.

Some of this is already done in the `nanomsg-dylan`_ repository
while other work remains.  Feel free to try out the bindings and
report any issues that you encounter.

In future blog posts, we'll write about using the `C-FFI`_ directly
as well as using the lower level ``direct-c-ffi`` (which is currently
undocumented).

Hopefully you have a good idea now of what is involved in producing
bindings for a C library using the `melange`_ tool and are ready
to try binding a library on your own!

.. _nanomsg: http://nanomsg.org/
.. _melange: https://github.com/dylan-lang/melange
.. _melange git repository: https://github.com/dylan-lang/melange
.. _C-FFI: http://opendylan.org/documentation/library-reference/c-ffi/index.html
.. _C-mapped-subtype: http://opendylan.org/documentation/library-reference/c-ffi/index.html#XXXX
.. _nanomsg-dylan: https://github.com/dylan-foundry/nanomsg-dylan
