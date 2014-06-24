Reducing Dispatch Overhead
##########################

:author: Bruce Mitchener, Jr.
:date: 2014-6-24
:tags: Performance, Method Dispatch

Method dispatch in Dylan is the process by which the compiler and run-time
collaborate to choose the right implementation of a function to call. This
can get rather complex as a number of factors are involved in choosing
the right method to call and whether that can be done at compile-time or
deferred to run-time.

Unfortunately, full generic method dispatch at run-time in Open Dylan is
currently not as fast as we would like. This means that when performance
issues strike, they may well be due to the overhead of method dispatch.

Discussing and improving the overall performance of method dispatch isn't
the subject of this post. That's going to require a fair bit of planning
and work before that is resolved.

Instead, we're going to look at what to do when you're experiencing
performance problems at particular call sites due to the overhead of
method dispatch.

Sometimes, this is readily visible in the profiler:

.. image:: /static/images/method_dispatch_in_profiler.png
   :align: right

Here, we can see that the ``percent-encode`` method in the ``uri`` library
is going through dispatch to call ``member?``.  (I've translated from the
names of the functions in C to their names in Dylan. The name mangling
isn't that difficult to pick up.)

In Dylan, this method looks like:

.. code-block:: dylan

    define method percent-encode
        (chars :: <sequence>, unencoded :: <byte-string>)
     => (encoded :: <string>)
      let encoded = "";
      for (char in unencoded)
        encoded := concatenate(encoded,
                               if (member?(char, chars))
                                 list(char)
                               else
                                 format-to-string("%%%X", as(<byte>, char))
                               end if);
      end for;
      encoded
    end method percent-encode;

And in C, we can see that the dispatch looks like this (from
``_build/build/uri/uri.c``):

.. code-block:: c

    CONGRUENT_CALL_PROLOG(&KmemberQVKd, 3);
    T4 = CONGRUENT_CALL3(T16, chars_, &KPempty_vectorVKi);

Method dispatch in the generated C can take many forms. It won't always be
a ``CONGRUENT_CALL``.  It might be an ``ENGINE_NODE_CALL``, ``CALL``,
``MEP_CALL`` among other things.

There are multiple implementations of the ``member?`` function. Some of the
function signatures available are (simplifying a bit):

* ``member? (<object>, <sequence>)``
* ``member? (<object>, <list>)`` (sealed)
* ``member? (<number>, <range>)``
* ``member? (<object>, <vector>)``
* ``member? (<byte-character>, <byte-string>)`` (sealed)

Looking at the Dylan code, one of the first things that we can see here is
that the ``chars`` parameter is a plain ``<sequence>`` rather than a more
specific class. This means that the compiler isn't seeing what type of
data is actually being passed in, and has to make the most generic decision.

Because the applicable function is not sealed, the compiler can't be sure
which implementation is the right one to invoke. This is because the
types of the arguments at run-time could lead to the selection of a more
specific ``member?`` implementation. Also, since the function isn't sealed,
there may well be implementations of ``member?`` that aren't visible to
the compiler yet (through shared libraries, plug-ins, etc.).

This leads to the compiler deciding to emit a fully generic method dispatch
at run-time rather than directly invoking a more specific implementation by
evaluating the method dispatch at compile time.

What we would like to see happen here instead is for the compiler to emit
a call directly to the specialized implementation of
``member?(<byte-character>, <byte-string>)``. This is possible because
that implementation is sealed (no more specific version can be provided)
and, in all cases, what is passed in can be a ``<byte-string>``, so we
can change the signature of the method to:

.. code-block:: dylan

    define method percent-encode
        (chars :: <byte-string>, unencoded :: <byte-string>)
      => (encoded :: <string>)
       ...
    end method percent-encode;

Now, when we compile this and examine the C, we can see that it has
eliminated the dispatch and is directly invoking the correct method,
``member?(<byte-character>, <byte-string>)``, which has been optimized
for this case:

.. code-block:: c

    T16 = KmemberQVKdMM3I(T15, chars_, &KPempty_vectorVKi, &KEEVKd);

Other changes could still be made to improve this function to further
reduce the dispatch, but we've solved the issue with ``member?``. In
particular, building a string by using ``concatenate`` to append
each character won't perform all that well and should be addressed.

In reality, there wasn't yet a specialized implementation of ``member?``
defined on ``<byte-character>`` and ``<byte-string>``, but one has been
added to the 2014.1 release as a result of this work.

Indeed, there won't always be a way to fully eliminate all dispatch.
This can have varying causes:

* There isn't a more specific method.
* There isn't a most specific method where the method or classes
  involved are sealed, so the compiler can't be sure it can eliminate
  the dispatch.
* The compiler can't figure out enough about the types of objects
  involved to find a more specific method.
* Generic dispatch is actually required at this call-site.

We'll look into some of these things in future blog posts.
