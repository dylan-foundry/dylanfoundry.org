The Limits of Limited Types
###########################

:author: Bruce Mitchener, Jr.
:date: 2014-12-10
:tags: Type System
:status: draft

What Are Limited Types?
=======================

Limited types are used to indicate objects that are instances of another
type and have additional constraints imposed upon them. They are used in
two scenarios typically: limiting integers and limiting collections.

Limited Integers
----------------

Limited integers allow the programmer to express the specific range
of integers permitted within a value via an upper and lower bound:

.. code-block:: dylan

  // Accepts all strictly positive integers.
  define method f (x :: limited(<integer>, min: 1))
    ...
  end method f;

Limited Collections
-------------------

Limited collections can constrain the size or dimensions of a collection
as well as the types of values that can be stored within the collection:

.. code-block:: dylan

  let <integer-vector> = limited(<vector>, of: <integer>);
  let <veci3> = limited(<vector>, of: <integer>, size: 3);

Origins of Limited Types
------------------------

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

According to Wikipedia, `parametric polymorphism is`_:

    In programming languages and type theory, parametric polymorphism is
    a way to make a language more expressive, while still maintaining full
    static type-safety. Using parametric polymorphism, a function or a data
    type can be written generically so that it can handle values identically
    without depending on their type.[1] Such functions and data types are
    called generic functions and generic datatypes respectively and form
    the basis of generic programming.

    For example, a function ``append`` that joins two lists can be
    constructed so that it does not care about the type of elements: it
    can append lists of integers, lists of real numbers, lists of strings,
    and so on. Let the *type variable a* denote the type of elements in
    the lists. Then ``append`` can be typed ``[a] × [a] -> [a]``, where
    ``[a]`` denotes the type of lists with elements of type *a*. We say
    that the type of ``append`` is *parameterized by a* for all values
    of *a*. (Note that since there is only one type variable, the
    function cannot be applied to just any pair of lists: the pair, as well as
    the result list, must consist of the same type of elements.) For each
    place where ``append`` is applied, a value is decided for *a*.

Hannes Mehnert wrote about Dylan and parametric polymorphism in his paper
`Extending Dylan’s type system for better type inference and error detection`_,
presented at ILC2010. He discusses how this can apply to Dylan (assumning
also that `function types`_ have been added to Dylan):

    The motivating example to enhance Dylan’s type inference is
    ``map(method(x) x + 1 end, #(1, 2, 3))`` which applies the
    anonymous method ``x + 1`` to every element of the list
    ``#(1, 2, 3)``. Previously the compiler called the generic
    function ``+``, since it could not infer precise enough types,
    using the type inference algorithm described in `[2]`_.

    By introduction of parametric polymorphism (type variables) the
    types can be inferred more precisely. The former signature of our
    map is ``<function>, <collection> ⇒ <collection>``. A more specific
    signature using type variables would be ``<function>α→β,
    <collection>α ⇒ <collection>β``, where the first parameter is a
    ``<function>`` which is restricted to ``α → β``, the second
    parameter is a ``<collection>`` of ``α``, and the return value is
    a ``<collection> of β``.  Using this signature, ``α`` will be bound
    to ``<integer>``, and the optimizer can upgrade the call to ``+`` to
    a direct call to ``+ (<integer>, <integer>)``, since the types of the
    arguments are ``<integer>`` and ``singleton(1)``.

I don't have a lot more to add to that at the moment. Adding parametric
polymorphism to Dylan instead of having a very limited set of generic
classes available (and all of them collections) would be a great step
forward in terms of expressiveness and safety.

Refinement Types
----------------

...

The Pains of Expressiveness
===========================

Above, we have treated gains in expressiveness as an unquestioned
good. After all, they allow the programmer to more clearly express
what they want and the compiler is better able to check for errors.
It sounds great!

Unfortunately, however, gains in expressiveness can come at a cost.

In the case of Dylan, the language specification and the compiler
itself were able to take advantage of the restrictions imposed upon
limited types in various ways.

For example, with limited integers since the constraints are restricted
to upper and lower bounds, it was readily possible to statically
determine subtype relationships between various limited integer
types at compile and run time. This allowed them to work cleanly with
method dispatch and in an intuitive and clear way.

Information about the static size of limited collections (those with
a static size) is used during optimization as well to help constant
fold away some checks that would otherwise have been performed.

Allowing arbitrary predicates to be attached to a base type, as is
done by refinement types, makes it much harder (or impossible) to
determine type relations at compile or run time.

How Can We Improve Dylan?
=========================

That's a great question!

...

.. _Satisfiability Modulo Theories: http://en.wikipedia.org/wiki/Satisfiability_Modulo_Theories
.. _parametric polymorphism is: http://en.wikipedia.org/wiki/Parametric_polymorphism
.. _Extending Dylan’s type system for better type inference and error detection: http://www.itu.dk/~hame/ilc2010.pdf
.. _function types: http://dylanfoundry.org/2014/08/01/function-types-and-dylan-2016/
.. _[2]: http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.93.4969
