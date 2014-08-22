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
    let <point> = limited(<vector>, of: <integer>, size: 3);

What's Limiting About Limited Types?
====================================

While limited types can be very useful, they are unfortunately, limited
in that usefulness. This limited usefulness is caused by a couple of
factors:

* Limited types are restricted to a particular set of classes, requiring
  run-time and compiler support.
* Constraints on limited types, such as size or the range of valid integer
  values, require compiler-side support and are not as expressive
  as they might be with respect to the constraints that can be imposed.

If we were to generalize limited types, we can begin to see how limited
the existing design is. Looking at computer science research, there are
a couple of interesting areas of research and development within the
type system world that are applicable here:

* Parametric Polymorphism
* Refinement Types

Both of these techniques are more common in the ML world and have been
active areas of research over the last 25 years (or longer).

Parametric Polymorphism
=======================

...

Refinement Types
================

...

How Can We Improve Dylan?
=========================

That's a great question!
