Type System Overview
####################

:author: Bruce Mitchener, Jr.
:date: 2014-8-21
:tags:
:status: draft

The type system and how it is used is a commonly misunderstood aspect
of the Dylan language. Although it lacks some forms of expressiveness
in the current incarnation, it also has some features that aren't
found in many languages such as singleton types.

How is the type system used?
============================

Variable bindings
-----------------

...

Method Dispatch
---------------

...

Compile vs Run Time
===================

Types Are Values
================

As `described in the DRM`_:

    All types are first class objects, and are general instances of ``<type>``.
    Implementations may add additional kinds of types. The language does
    not define any way for programmers to define new subclasses of ``<type>``.

As the language does not define a mechanism for programmers to define new
types, this is left to the implementation.


Extending The Type System
=========================

...

Interesting Features
====================

Singleton Types
---------------

What Dylan calls *singleton types* are a way to create a new type that indicates
that an individual object. This is commonly used in method dispatch:

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

Dispatch vs Pattern Matching
----------------------------

...

.. _described in the DRM: http://opendylan.org/books/drm/Types_and_Classes_Overview
.. _in a bit more detail: http://opendylan.org/books/drm/Singletons
