Dylan and Gradual Typing
########################

:author: Bruce Mitchener, Jr.
:date: 2015-01-20
:tags: Dylan 2016, Type System

As we look to the future and what we would like for Dylan to become and
investigate how we would like for Dylan to evolve, it is helpful to look
at some of the current work and how Dylan compares, where Dylan falls
down and whether or not we can improve it.

One of those areas is in the guarantees offered by the type system. While
Dylan is seen as a dynamic language, it has a number of features that
help provide optional static type checking. As we'll see, there is a lot
of room for improvement in this area.

In this post, using a missing compile-time warning as the driver, we'll
walk through some details of the Dylan type system and then see how it
differs from a gradually typed system. We'll see that type annotations
are interpreted very differently under a gradual typing regime versus
the Open Dylan compiler.

I've previously written a `Type System Overview`_ which may be useful,
but hopefully this post can stand on its own.

One particularly interesting body of work is that on *Gradual Typing*.
From `What is Gradual Typing`_:

    Gradual typing is a type system I [Jeremy Siek] developed with
    Walid Taha in 2006 that allows parts of a program to be dynamically
    typed and other parts to be statically typed. The programmer
    controls which parts are which by either leaving out type
    annotations or by adding them in. 

On the surface, this sounds a lot like how the `Dylan`_ type system
operates.  Type annotations can be provided or inferred, and are
optional. When the Dylan compiler has sufficient type information,
it can perform many sorts of optimizations, many of which are key
to getting good run-time performance. The compiler can also use this
type information to provide better warnings and diagnostics for the
Dylan programmer.

The Case of the Missing Warning
===============================

So, how do they differ? Let's start by taking an interesting case that
happened to me the other day!

I accidentally wrote this bit of code:

.. code-block:: dylan

   write(string-data, stream);

Unfortunately, this very simple bit of code compiled with no warnings,
yet was fatally flawed. It should have been this, with the arguments
in the correct order:

.. code-block:: dylan

   write(stream, string-data);

So, why didn't the compiler generate a warning?

In this case, the Dylan compiler knew that ``stream`` was a ``<stream>``
instance and that ``string-data`` was a ``<string>``. It also knew
that the method ``write`` was defined as follows:

.. code-block:: dylan

   define open generic write
       (stream :: <stream>, elements :: <sequence>,
        #key start, \end)
    => ();

To get any further, we're going to have take a trip into the compiler
source code.

Diving into the Depths of the Compiler
======================================

We'd been hoping to see a warning that started with the text ``Invalid
type for argument``. With some quick greps, we can see that this
corresponds to the ``<argument-type-mismatch-in-call>`` warning object
which is emitted from ``check-call-compatibility`` defined in
``sources/dfmc/optimization/dispatch.dylan``.

For the purposes of this post, it isn't too important to know how we
got to this point in the compiler, but the short form is that we're
analyzing function call sites to try to optimize them and we check
them first for various issues, which eventually gets to
``check-call-compatibility``.

The relevant bit of code, with a few things that don't matter here
removed is:

.. code-block:: dylan

   for (arg-te in arg-te*, required-type in required-types,
        i :: <integer> from 0 below required-count)
     if (~guaranteed-joint?(arg-te, required-type))
       if (effectively-disjoint?(arg-te, required-type))
         let required-specs
           = spec-argument-required-variable-specs(signature-spec(f));
         note(<argument-type-mismatch-in-call>,
              source-location: dfm-source-location(call),
              context-id:      dfm-context-id(call),
              function: f,
              required-type:  required-type,
              supplied-type-estimate: arg-te,
              arg: spec-variable-name(required-specs[i]));
       end if;
     end if;
   end for;

Here, ``arg-te*`` is a sequence of "type estimates" for each of the
arguments at the call-site. A type estimate is the data about the
type of a value that the compiler knows, including also information
about where that data came from or how it was inferred.  ``required-types``
is the sequence of types that the function being called requires.

It should also be noted that this check is **only** to emit the
warning. This part of the code plays no role in optimization.
Upgrading the call-site to remove or reduce the run-time dispatch
and the associated decision making is handled in another part of
the optimizer.

Into the Type System
--------------------

The first check is to see if the type estimate and the required
type for the argument is **not** ``guaranteed-joint?``. (In Dylan,
a ``~`` is the negation operator.) The ``guaranteed-joint?`` check
is simply a way of checking whether or not one type or type estimate
is **known** to be a subtype of the second type or type estimate.

In this case, the compiler knows that ``<string>`` and ``<stream>``
are not joint (``<string>`` is not a subtype of ``<stream>``). In
some type systems, this would be an immediate compile-time failure.
But in a dynamic type system, we have a couple of options, and this
is the point at which Dylan diverges from being *Gradually Typed*.

In a *Gradually Typed* type system, I believe that the proper behavior
at this point would be to see if type annotations had been provided
for the value, and if it had, then this would be a compile time
failure. If not, then we're in a part of the program where we are
leaving these sorts of failures to run-time.

From `What is Gradual Typing`_ again:

    The gradual type checker deals with unannotated variables by
    giving them the unknown type (also called the dynamic type
    in the literature), which we abbreviate as ``?`` and by allowing
    implicit conversions from any type to ``?`` and also from ``?``
    to any other type. For simplicity, suppose the ``+`` operator
    expects its arguments to be integers. The following version of
    ``add1`` is accepted by the gradual type checker because we
    allow an implicit conversion from ``?`` (the type of ``x``) to
    ``int`` (the type expected by ``+``).

    .. code-block:: python

       def add1(x):
         return x + 1

In Dylan, however, things are very different. We can see that we
call ``effectively-disjoint?`` here and only emit the warning when
that has returned a true value. In digging into the type system
implementation, not all code will be shown. Only the code related
to the types of values involved here (class vs class) comparisons
will be shown.

``effectively-disjoint?`` does a couple of bits of work related
to ``false-or`` type unions in Dylan, and then hands the work off
to ``guaranteed-disjoint?``. This soon ends up in a call to
``classes-guaranteed-disjoint?``.

When Are Two Classes Disjoint?
------------------------------

We are now at an interesting philosophical question: When are
two classes disjoint? When are they guaranteed to be disjoint?

The answer to this is that it isn't as easy as it seems. A new
class could be available that the compiler isn't aware of while
compiling this call-site and the code would be valid at run-time
even though it didn't appear to be at compile-time.

Given two classes, ``c1`` and ``c2``, if any subclass of ``c1``
is also a subclass of ``c2``, then they're provably not disjoint.

This may cause you to scream in horror. Perhaps rightfully so,
but that's the nature of *this* beast.

So, when does the Open Dylan compiler consider two classes to
be disjoint?

First, neither class can be a subtype of the other. This is pretty
logical.

Next, any of these conditions must be true for it to be guaranteed
disjoint:

* If both of the classes have superclasses which are `primary`_
  and those primary superclasses are not in a subtype relationship,
  then the classes are provably disjoint.
* The DRM defines that "... two classes which specify a slot with
  the same getter or setter generic function are disjoint...".
* Since we've gotten this far, we know that the two classes may
  be disjoint. To be sure that they are, we can check that there
  is no common subclass now and that things are sealed so that a
  new common subclass can't be created in the future.

This is a very different model from that which is provided by *Gradual
Typing*. The gradually typed model produces a compile-time failure
when both arguments have type information available sufficient to
demonstrate the disjointedness of the argument's type estimate and
the argument's required type. A ``<string>`` is not a ``<stream>``
and so it can not be passed as an argument where a ``<stream>`` is
required.

The Dylan model is significantly more dynamic:  it is clear that
a ``<string>`` is not a ``<stream>``, but since it is possible
there could be a future ``<stream>`` which also inherits from
``<string>``, then the compiler assumes that such a thing may
actually happen. No warning is emitted and the dispatch is left
as a fully dynamic (run-time) dispatch.

A shorter summary would be that in a gradually typed system, the type
annotation for a value indicates the most that the compiler should
assume about it, while in the Dylan type system, it represents the
bare minimum that can be known about it, unless otherwise limited (via
primary classes, sealing, or slot definitions).

Can Dylan Move in the Gradual Direction?
========================================

This is an interesting question (to me) and one with a few parts.

* Can the community move in the gradual direction?
* Is there flexibility within the DRM to support a gradually
  typed interpretation or would this effectively end up as a
  more significant language revision?
* How hard would it be to evolve the Dylan type system and
  compiler implementation in this direction?
* To what extent does existing code and existing standard practice
  rely upon the details discussed in this post?

I don't yet have answers for any of that! I do think it could be
an interesting discussion though.

There's an interesting comment related to this in the compiler
source code, shortly before it implements the call compatibility
checks::

  // Do a conservative check of as many things about this call as we
  // possibly can. It's conservative in the sense that it warns only
  // if there's guaranteed to be a problem. If we work out ways of
  // extending the language appropriately so that we don't get
  // swamped with information, a mode conservative the other way
  // would be very useful.

So this isn't a new question or discussion at all...

.. _Type System Overview: http://dylanfoundry.org/2014/08/28/type-system-overview/
.. _What is Gradual Typing: http://wphomes.soic.indiana.edu/jsiek/what-is-gradual-typing/
.. _Dylan: http://opendylan.org/
.. _primary: http://opendylan.org/books/drm/Declaring_Characteristics_of_Classes#IX-1111
