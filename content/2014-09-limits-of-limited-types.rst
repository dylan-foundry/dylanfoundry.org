The Limits of Limited Types
###########################

:author: Bruce Mitchener, Jr.
:date: 2014-9-10
:tags: Type System
:status: draft

What Are Limited Types?
=======================

Limited types are used to indicate objects that are instances of another
type and have additional constraints imposed upon them. They are used in
two scenarios typically:

* Limiting the range of valid integer values:

  .. code-block:: dylan

    // Accepts all strictly positive integers.
    define method f (x :: limited(<integer>, min: 1))
      ...
    end method f;

* Limiting the size or types of elements contained within a collection:

  .. code-block:: dylan

    let <integer-vector> = limited(<vector>, of: <integer>);
    let <veci3> = limited(<vector>, of: <integer>, size: 3);

Like many elements of the Dylan design, these clearly came from Common Lisp,
where integer types can specify upper and lower bounds, and collections
can specify an element type and dimensions:

.. code-block:: lisp

  (integer 0 32)
  (vector integer)
  (vector integer 3)
  (array integer (4 4))


What's Limiting About Limited Types?
====================================

While limited types can be very useful, they are unfortunately, limited
in that usefulness. This limited usefulness is caused by a couple of
factors:

* Limited types are restricted to a particular set of classes, requiring
  run-time and compiler support. This is not a fully general mechanism
  that is available to users of the language to extend for their own
  classes.
* Constraints on limited types, such as size or the range of valid integer
  values, require compiler-side support and are not as expressive
  as they might be with respect to the constraints that can be imposed.
  Again, this is not a fully general mechanism, extensible by a Dylan
  programmer. The constraints that can be applied are very limited.

If we were to generalize limited types, we can begin to see how limited
the existing design is.

While I am not sure exactly why this design was limited in these ways,
I can make some guesses:

* Dylan was building on existing practice and not adding experimental
  features. The basis for limited types was already present in Common
  Lisp and more generalized or advanced designs had not spread widely
  outside of the ML community.
* Computers were slower at the time, so more advanced compilation
  strategies that were more generalized may not have been as common
  as they are today.
* As we'll see below, some of the exciting new type system designs
  are based on other research which has only recently come into
  maturity. An example of this are systems which employ SMT
  (`Satisfiability Modulo Theories`_) solvers.

*Note: I should drop David Moon and others an email perhaps and ask
about this.*

Looking Forward By Looking Around
=================================

Looking at computer science research, there are a couple of interesting
areas of research and development within the type system world that are
applicable here:

* Parametric Polymorphism
* Refinement Types

Both of these techniques are more common in the ML world and have been
active areas of research over the last 25 years (or longer).

Parametric Polymorphism
-----------------------

...

Refinement Types
----------------

...

How Can We Improve Dylan?
=========================

That's a great question!

...

.. _Satisfiability Modulo Theories: http://en.wikipedia.org/wiki/Satisfiability_Modulo_Theories
