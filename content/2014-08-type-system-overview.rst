Type System Overview
####################

:author: Bruce Mitchener, Jr.
:date: 2014-8-21
:tags: Type System
:status: draft

The type system and how it is used is a commonly misunderstood aspect
of the Dylan language. Although it lacks some forms of expressiveness
in the current incarnation, it also has some features that aren't
found in many languages such as singleton types.


Type and Value Relationships
============================

There are 2 important relationships between values and types in Dylan.

They are ``instance?`` and ``subtype?``. Other relationships, such as
``known-disjoint?`` are used within the compiler to assist with type
inference, but these other relationships are not regularly of use to
the typical Dylan programmer.

``instance?``
-------------

The ``instance?`` relationship holds between a value and a type. A
value can be an instance of a type (or not).

``subtype?``
------------

The ``subtype?`` relationship holds between two types. One type can
be a subtype of another type. When a type A is a subtype of type B,
then an instance of A can be used anywhere that expects an instance
of B.

From the DRM:

    The following is an informal description of type relationships: The
    function subtype? defines a partial ordering of all types. Type *t1*
    is a subtype of type *t2* (i.e., ``subtype?(t1, t2)`` is true) if it
    is impossible to encounter an object that is an instance of *t1* but
    not an instance of *t2*. It follows that every type is a subtype of
    itself.  Two types *t1* and *t2* are said to be **equivalent types**
    if ``subtype?(t1, t2)`` and ``subtype?(t2, t1)`` are both true. *t1*
    is said to be a **proper subtype** of *t2* if *t1* is a subtype of
    *t2* and *t2* is not a subtype of *t1*.

As we will discuss below, there are multiple kinds of types and each
kind of type defines its own rules for how subtype relationships involving
that kind of type operate.


How is the type system used?
============================

The DRM doesn't specify much about how the type system should be used
and enforced. In general, it assumes that at a minimum, run-time enforcement
via type checks will occur, and leaves any further checks and optimization
up to the implementation.

In practice though, the Open Dylan compiler makes extensive use of
type annotations at compile time.

Variable bindings
-----------------

A variable may have its type restricted by specifying a type:

.. code-block:: dylan

  let x = 123; // x can be re-assigned to any type of value
  let y :: <integer> = 123; // the value of y must be an instance of <integer>

Method Dispatch
---------------

The type system plays a very important role in method dispatch. Method
dispatch is the act (or art) of choosing which of several possible methods
should be invoked for a given set of arguments. This is covered in some
depth in the `Method Dispatch section of the DRM`_.

Two important things to note here are

* ``subtype?`` relationships are a key part of ordering methods and choosing
  which one to invoke.
* ``instance?`` relationships must also hold for a method to be chosen.


Compile vs Run Time
===================

...


Kinds of Types
==============

The DRM specifies 4 kinds of types:

* Classes
* Limited Types
* Union Types
* Singleton Types

Classes
-------

...

Limited Types
-------------

...

Union Types
-----------

...

Singleton Types
---------------

What Dylan calls *singleton types* are a way to create a new type that indicates
that an individual object is expected. This is commonly used in method dispatch:

.. code-block:: dylan

  define method factorial (n :: singleton(0))
    1
  end;

An alternative syntax makes this a bit more readable to many people:

.. code-block:: dylan

  define method factorial (n == 0)
    1
  end;

Singletons are described in the DRM `in a bit more detail`_, but the
important thing to note is that for a value to match a singleton type,
it must be ``==`` to the object used to create the singleton. This means
that not all objects can be used as singleton types; in particular,
strings are a notable exception.

Also important is that a method specializer that is a singleton is
considered to be the most specific match. This is because it is
directly matching against the value passed in.

A common use of singleton types is in defining ``make`` methods by using
a singleton type for the ``class`` argument:

.. code-block:: dylan

  define method make (class == <file-stream>, #rest initargs,
                      #key locator,
                           element-type = <byte-character>,
                           encoding)
   => (stream :: <file-stream>)
    let type
      = apply(type-for-file-stream, locator, element-type,
              encoding, initargs);
    if (type == class)
      next-method()
    else
      apply(make, type, initargs)
    end
  end method make;

This example is also interesting as demonstrates that the type is a first
class object by using ``type-for-file-stream`` to look up which type
should be used to instantiate the file stream. (This way of implementing
a ``make`` method specialized on an abstract class like ``<file-stream>``
is a common way to implement a factory method in Dylan.)


Types Are Values
================

As `described in the DRM`_:

    All types are first class objects, and are general instances of ``<type>``.
    Implementations may add additional kinds of types. The language does
    not define any way for programmers to define new subclasses of ``<type>``.

This means that functions can return instances of a type and type objects
are treated like any other value in Dylan. This is used in many places,
including ``type-for-copy`` in the standard library.


Extending The Type System
=========================

As the language does not define a mechanism for programmers to define new
types, this is left to the implementation.

In Open Dylan, this is currently limited to providing refinements on vectors
via ``limited(<vector>, of: ...)`` and new instances of the ``<limited-integer>``
type (which allows specifying the bounds on allowable integer values).

It would be interesting to look at what is involved in adding a new type
without compiler modifications, but that is not currently permissible in
the Open Dylan implementation. This sounds like a pretty interesting topic
though, so we'll likely take a look at it in a future blog post and set
of patches to Open Dylan. (An example of a new type would be generating
a type that represents constrained values based on a schema definition.)


.. _Method Dispatch section of the DRM: http://opendylan.org/books/drm/Method_Dispatch
.. _in a bit more detail: http://opendylan.org/books/drm/Singletons
.. _described in the DRM: http://opendylan.org/books/drm/Types_and_Classes_Overview
