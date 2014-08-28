Type System Overview
####################

:author: Bruce Mitchener, Jr.
:date: 2014-8-28
:tags: Type System

The type system and how it is used is a commonly misunderstood aspect
of the Dylan language. Although it lacks some forms of expressiveness
in the current incarnation, it also has some features that aren't
found in many languages, such as singleton types. It is also very
important in helping the compiler to generate faster yet still safe code.

One interesting feature in Dylan is that it is optionally typed.  While
this is more common today and sometimes has fancy names applied like
'gradually typed', the overall point is the same: Your code can start
out untyped and looking like code does in Ruby or Python. However,
when you want or need additional performance or correctness guarantees,
you can supply type annotations that the compiler can use.  The compiler
can also infer some types from the values used or other type annotations.

In this post, we'll explain some of the basic concepts of the Dylan
type system and show how it is used by the compiler.


Type and Value Relationships
============================

There are 2 important relationships between values and types in Dylan.

They are ``instance?`` and ``subtype?``. Other relationships, such as
``known-disjoint?`` are used within the compiler to assist with type
inference, but these other relationships are not regularly of use to
the typical Dylan programmer.

``instance?``:
    The ``instance?`` relationship holds between a value and a type. A
    value can be an instance of a type (or not).

``subtype?``:
    The ``subtype?`` relationship holds between two types. One type can
    be a subtype of another type. When a type A is a subtype of type B,
    then an instance of A can be used anywhere that expects an instance
    of B.

From the Dylan Reference Manual (DRM):

    The following is an informal description of type relationships: The
    function ``subtype?`` defines a partial ordering of all types. Type
    *t1* is a subtype of type *t2* (i.e., ``subtype?(t1, t2)`` is true)
    if it is impossible to encounter an object that is an instance of *t1*
    but not an instance of *t2*. It follows that every type is a subtype of
    itself.  Two types *t1* and *t2* are said to be **equivalent types**
    if ``subtype?(t1, t2)`` and ``subtype?(t2, t1)`` are both true. *t1*
    is said to be a **proper subtype** of *t2* if *t1* is a subtype of
    *t2* and *t2* is not a subtype of *t1*.

As we will discuss below, there are multiple kinds of types and each
kind of type defines its own rules for how subtype relationships involving
that kind of type operate. The specifics of these subtype relationships
are discussed in the `Dylan Reference Manual`_.


How is the type system used?
============================

The DRM doesn't specify much about how the type system should be used
and enforced. In general, it assumes that at a minimum, run-time enforcement
via type checks will occur, and leaves any further checks and optimization
up to the implementation.

In practice though, the Open Dylan compiler makes extensive use of
type annotations at compile time as we will discuss shortly.

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

The Open Dylan compiler makes extensive use of type annotations and
type inference to remove as many run-time type checks from the generated
code as possible, as well as to perform other optimizations.

The compiler also seeks to provide compile time warnings about as many
type errors as it can.

One of the major parts of the Dylan language design that increases what is
possible to optimize at compile time is `sealing`_. Sealing plays a very
important role in the optimization of a Dylan program. It even gets
an entire chapter of the DRM dedicated to it.

Function Call Upgrades
----------------------

One of the important things that is made possible by the Open Dylan
compiler and the judicious use of sealing is moving some of the work
involved in method dispatch from run time to compile time.

It is through this mechanism that we are able to often avoid performing
an expensive dispatch at all, inline methods, upgrade from a function
call to a direct slot access and many other optimizations.

Examples
--------

We can define a simple sealed method that simply returns false (``#f``).
We seal the method so that the compiler is aware that it knows of all
implementations of the generic function. By sealing the method, no
new methods may be added to the generic function outside of the library
being built.

.. code-block:: dylan

    define sealed method foo (a :: <string>)
     #f
    end;

    define function main
        (name :: <string>, arguments :: <vector>)
      foo("abc");
      exit-application(0)
    end;

If we go and call ``foo`` with a value of the wrong type, we'll see that
we get an error (which Open Dylan calls a serious warning)::

    foo.dylan:9: Serious warning - Invalid type for argument a in call to method
      foo (a :: <string>, #next next-method :: <object>) => ():
        singleton(123 :: <integer>) supplied, <string> expected.

      --------
      foo(123);
      --------

(An interesting side note here is that the compiler inferred a very specific
type for the value passed in:  ``singleton(123 :: <integer>)`` rather than
just ``<integer>``. We'll learn about singleton types below.)

Now, we can take a look at the C code that is generated for ``foo``. The compiler
generated no type checks within the method. The name of the method is mangled
by the compiler so that it is unique and obeys C function name rules.

.. code-block:: c

    dylan_value KfooVfooMM0I (dylan_value a_) {
      dylan_value T2;

      T2 = &KPfalseVKi;
      MV_SET_COUNT(0);
      return(T2);
    }

Similarly, if we look at some code that invokes ``foo`` and immediately
exits, we'll see that the compiler was able to directly invoke the
appropriate methods without going through generic dispatch and without
performing any unnecessary type checks:

.. code-block:: c

    dylan_value KmainVfooI (dylan_value name_, dylan_value arguments_) {
      dylan_value T2;

      KfooVfooMM0I(&K5);
      T2 = Kexit_applicationYcommon_extensionsVcommon_dylanI((dylan_value) 1);
      return(T2);
    }

If the compiler were not sure what exactly to invoke for ``foo("abc")``,
we would have seen it performing a generic dispatch in the generated C
rather than directly invoking a C function as it did (``KfooVfooMM0I``).
Similarly, if the compiler wasn't sure about what was happening at the
type level, it may have emitted code for a run-time type check to be
sure that the types were correct.

Hopefully, this helps to make it more clear how the type system is used
at compile time and how it helps us to generate faster code while still
maintaining the safety checks where required.

We will see another example of this in the section below on limited
types.


Kinds of Types
==============

The DRM specifies 4 kinds of types:

* Classes
* Limited Types
* Union Types
* Singleton Types

These are discussed in detail `in the DRM`_.

In the near future, we are likely to see this list of types expand.
For example, `function types`_ are already being discussed.

Classes
-------

`Classes`_ are described in detail in the DRM. The important parts for now
are:

* Classes are used to define the inheritance, structure, and
  initialization of objects.
* Every object is a direct instance of exactly one class, and
  a general instance of the superclasses of that class.
* A class determines which slots its instances have. Slots are
  the local storage available within instances. They are used
  to store the state of objects.

An interesting tidbit is that new classes can be created at run-time.

Limited Types
-------------

Limited types consist of a base type and a restricted set of constraints
to be applied.

Currently, integers and collections can be limited.  Limited integers have
minimum and maximum bounds. Limited collections can constrain the type
of the elements stored in the collection as well as the size or dimensions
of the collection.

Simple examples:

.. code-block:: dylan

  define constant <byte> = limited(<integer>, min: 0, max: 255);

  define constant <float32x4> = limited(<vector>,
                                        of: <single-float>,
                                        size: 4);

The last example is particularly interesting (to me at least). In Dylan,
``<single-float>`` is a 32 bit float, but will usually be stored in a boxed
form. By creating a limited vector of ``<single-float>`` with a size of 4,
the compiler is able to optimize away bounds checks and it is able to store
the floating point values without being boxed.

For example, storing some floating point values into an instance of the
above ``<float32x4>`` limited type would look like:

.. code-block:: dylan

  fs[0] := 1.0s0;
  fs[1] := 2.0s0;
  fs[2] := 3.0s0;
  fs[3] := 4.0s0;

That compiles to this in C:

.. code-block:: c

  REPEATED_DSFLT_SLOT_VALUE_TAGGED_SETTER(1.0000000, fs_, 1, 1);
  REPEATED_DSFLT_SLOT_VALUE_TAGGED_SETTER(2.0000000, fs_, 1, 5);
  REPEATED_DSFLT_SLOT_VALUE_TAGGED_SETTER(3.0000000, fs_, 1, 9);
  REPEATED_DSFLT_SLOT_VALUE_TAGGED_SETTER(4.0000000, fs_, 1, 13);

``REPEATED_DSFLT_SLOT_VALUE_TAGGED_SETTER`` is a C preprocessor
definition that results in a direct memory access without any function
call overhead. To confirm that and just for fun, here is the resulting
assembler code (x86):

.. code-block:: asm

  movl  $0x3f800000, 0x8(%eax)
  movl  $0x40000000, 0xc(%eax)
  movl  $0x40400000, 0x10(%eax)
  movl  $0x40800000, 0x14(%eax)

Doing the same thing, but with a regular vector would require boxing each
value.  For literals, this generates a static file-scope value in the C
back-end, increasing the memory usage:

.. code-block:: c

  static _KLsingle_floatGVKd K3 = {
    &KLsingle_floatGVKdW, // wrapper
    5.0000000
  };

Similarly, when we go to fetch and add the values, using the limited vector
will be far more efficient as it already knows the type of the value involved
and no additional checks need to be done.

We'll use this snippet to demonstrate where ``fs`` is a limited vector as above
and ``bfs`` is a normal vector with boxed values:

.. code-block:: dylan

  let s = fs[0] + fs[1];
  let bs = bfs[0] + bfs[1];

This results in the following code

.. code-block:: c

  // Limited vector
  T9 = REPEATED_DSFLT_SLOT_VALUE_TAGGED(fs_, 1, 1);
  T10 = REPEATED_DSFLT_SLOT_VALUE_TAGGED(fs_, 1, 5);
  T11 = primitive_single_float_add(T9, T10);

  // Normal vector with boxed floats
  T19 = KelementVKdMM11I(bfs_, (dylan_value) 1, &KPempty_vectorVKi, &Kunsupplied_objectVKi);
  T20 = KelementVKdMM11I(bfs_, (dylan_value) 5, &KPempty_vectorVKi, &Kunsupplied_objectVKi);
  CONGRUENT_CALL_PROLOG(&KAVKd, 2);
  T3 = CONGRUENT_CALL2(T19, T20);

There's a lot going on there. With the limited vector,
``REPEATED_DSFLT_SLOT_VALUE_TAGGED`` is a direct memory access, while with
the normal vector, it is going through the ``element`` method (whose mangled
name is ``KelementVKdMM11I``) and doing bounds checks. When performing the
addition, the limited vector code is able to directly add the floating point
values. However, with the normal vector, it may have gotten any type of object
out of the vector, so it has to go through a generic dispatch
(``CONGRUENT_CALL_PROLOG`` and ``CONGRUENT_CALL2``) to invoke the method for ``+``
which is mangled to be ``KAVKd`` in C.

This should help you understand that limited types can help the compiler greatly
optimize the resulting code and improve the memory usage.

Union Types
-----------

In Dylan, union types represent a way to specify that a given value is one of
a two or more types. They are frequently used to represent that a value does
not exist:

.. code-block:: dylan

  let x :: type-union(singleton(#f), <integer>) = bar(3);

As we can see, union types are created using the ``type-union`` function.

Dylan provides a shorthand for the above technique, a method ``false-or``,
which returns the union of ``#f`` and a given type:

.. code-block:: dylan

  let x :: false-or(<integer>) = bar(3);

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

This example is also interesting as it demonstrates that the type is a
first class object by using ``type-for-file-stream`` to look up which type
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

A common example of treating types as values was the shorthand function
introduced above when discussing type unions: ``false-or``.


Moving On
=========

In future blog posts, we'll explore some additional aspects of the type
system in more detail, look at possible changes to the type system and
how the type system can be extended. There's a lot of material to cover
here, so it will take some time.


.. _Dylan Reference Manual: http://opendylan.org/books/drm/
.. _Method Dispatch section of the DRM: http://opendylan.org/books/drm/Method_Dispatch
.. _Sealing: http://opendylan.org/books/drm/Sealing
.. _in a bit more detail: http://opendylan.org/books/drm/Singletons
.. _described in the DRM: http://opendylan.org/books/drm/Types_and_Classes_Overview
.. _Classes: http://opendylan.org/books/drm/Classes
.. _in the DRM: http://opendylan.org/books/drm/Types_and_Classes
.. _function types: http://dylanfoundry.org/2014/08/01/function-types-and-dylan-2016/
