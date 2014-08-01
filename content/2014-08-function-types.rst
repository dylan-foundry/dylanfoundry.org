Function Types and Dylan 2016
#############################

:author: Bruce Mitchener, Jr.
:date: 2014-8-16
:tags: Dylan 2016
:status: draft

Moving towards **Dylan 2016**, we would like to address some weaknesses
in the language specification and what can be readily expressed in Dylan
code. In this post, we'll talk about function types as well as provide
a brief introduction to some details of the type system implementation
within the Open Dylan compiler.


Function Types
==============

One of the big holes in the Dylan type system is the inability to specify
function types. What this means is that you can only say that a value is
of type ``<function>`` and can't indicate anything about the desired
signature, types of arguments, return values, etc. This is unfortunate
for a number of reasons:

* **Poor static type safety.** The compiler can't verify almost anything
  involving a function value.  It can't warn when the wrong number
  of arguments or the wrong types of arguments are passed.
* **Less clear interfaces.** The type signature of a function must
  be documented clearly rather than being expressed clearly within
  the code.
* **Optimization is more difficult.** Since the compiler can't
  perform as many checks at compile time, more checks need to be
  performed at run-time, which limits the amount of optimization
  that can be performed by the compiler and restricts the generated
  code to using slower paths for function invocation.

In addition, function types may allow us to **improve type inference**.

This is something that people have long wanted to have in the Dylan
language. According to a comment by Kim Barrett in 2001:

    Several people at Apple and Harlequin (and maybe CMU too, I don't
    remember off hand) spent some time working on this, because it
    seemed like a serious hole in the Dylan type system.  However, it
    seemed that every attempt at a specification got arbitrarily hairy
    around variadic parameter lists and return types.  I have memories
    of a whiteboard densely covered with small print purporting to
    describe all the possible permutations...

There were also discussions about function types as far back as 1992
and 1993 in the early "Dylan partners" communications between Apple,
CMU, and Harlequin.  As such, it is clear that this will be an effort
that will require some time and patience to get right. That said,
function types are common in other modern programming languages,
especially those from the ML school.

A Motivating Case
-----------------

To guide this discussion, it will be easier to do it in the context
of a specific snippet of code. In this case, the code comes
from the ``logging`` library:

.. code-block:: dylan

  for (item in formatter.parsed-pattern)
    if (instance?(item, <string>))
      write(stream, item);
    else
      let result = item(level, target, object, args);
      if (result)
        write(stream, result);
      end;
    end;
  end;

The definition of ``parsed-pattern`` is:

.. code-block:: dylan

  slot parsed-pattern :: <sequence>;

Given Dylan as it is today, this could be tightened up and specified as:

.. code-block:: dylan

  slot parsed-pattern :: limited(<vector>,
                                 of: type-union(<string>, <function>));

Poor Static Type Safety
-----------------------

In the above example, the compiler can't check to verify that the
correct arguments are passed to ``item``. When constructing the
``parsed-pattern`` sequence, it also can't verify that the
functions in the sequence have the correct signatures.

The issue here is that the only thing that the compiler knows about
``item`` is that it is of type ``<function>``. It doesn't know about
the required function signature, so it can't verify anything. In a
normal function call, the compiler knows the signature of the function
and is therefore able to perform a number of static checks at compile
time.

Less Clear Interfaces
---------------------

While this is less clear in the example above, you can't tell from looking
at the slot what sort of function is involved.

But an easy example of where the lack of function types makes things more
complex is in the ``map`` function:

.. code-block:: dylan

  define sealed generic map
      (fn :: <function>, coll :: <collection>,
       #rest more-colls :: <collection>)
   => (new-collection :: <collection>);

Ignoring the lack of parametric polymorphism, which we'll deal with in a
future blog post, it is clear that it would be nice to have more detail
about what sort of function should be passed to ``map``. We would like
to have a way to specify that the function passed to map should have
a signature congruent with ``(<object>) => (<object>)``.

Optimization Is More Difficult
------------------------------

Instead of looking at the full body of code from above, we'll restrict
ourselves to the invocation of the ``item`` function:

.. code-block:: dylan

  let result = item(level, target, object, args);

When we look at the compiler's IR, we see this::

  {{ result }} := [CALLo t7({{ level }}, {{ target }}, {{ object }}, {{ args }})]

When we look at the generated C, we see:

.. code-block:: c

  result_ = CALL4(T7, level_, target_, object_, args_);

Ideally, once more information is present at compile time, we would like
to be able to use more efficient calling sequences, perhaps even able to
directly invoke the function via its IEP (internal entry point) rather
than going through any of the dispatch machinery.

Improving Type Inference
------------------------

An interesting possibility is that function types can be used to improve
type inference. This is something that SBCL does.

Given code like this:

.. code-block:: dylan

  define function bar (x :: <integer>) => (r :: <integer>)
    ... calculations involving x ...
  end;

  define function foo (x)
    let y = bar(x)
    ... other calculations involving x and y ...
  end;

If the function call to bar does not fail, then we know that ``x`` must
be of type ``<integer>``. So we can infer that ``x`` is an ``<integer>``
for the subsequent uses of ``x`` after ``let y = bar(x)`` (assuming
nothing assigns a new value to it).

**Note:** *See if this is actually valid. We may already effectively
have this bit of type inference due to some other aspects of the
type system.*


Adding Function Types to Open Dylan
===================================

Adding function types to Open Dylan will be an interesting task. For the
most part, no one is sure of all of the steps that will be involved.

Syntax
------

An interesting question is what sort of syntax should function types have?

One option is to use the same ``limited`` syntax that we use for other
specialized types. This was proposed by Neel Krishnaswami in a patch
to Gwydion Dylan in January, 2000.  A limited type looks like:

.. code-block:: dylan

  limited(<vector>, of: <byte>, size: 3)

However, when applying that to functions, this would be pretty verbose:

.. code-block:: dylan

  limited(<function>, specializers: #[<string>], return-types: #[<boolean>])

This proposal did not support specifying ``#rest`` or ``#key`` arguments.

In 2010, Hannes Mehnert proposed a different syntax as part of his work on
function types and parametric polymorphism to extend the Dylan type system:

.. code-block:: dylan

  <string> => <boolean>

The main criticism of this syntax is that it isn't like existing Dylan
syntax. However, it is concise and is flexible enough to support ``#rest``
and ``#key`` arguments, as well as future language extensions such as
parametric polymorphism. This syntax was implemented with some specialized
code when parsing function signatures within ``dfmc-definitions``.

A proposal has been made by Carl Gay that I like a lot. Instead of
stand-alone syntax like that employed by Hannes, the signature can be
wrapped in what looks like a function call:

.. code-block:: dylan

  fn(<string> => <boolean>)

This provides a more Dylan-like surface syntax and is readily able to support
``#rest`` and ``#key`` parameters:

.. code-block:: dylan

  fn(<string>, #key instance?, #all-keys => ())

By using a macro to implement ``fn``, it can produce an instance of a
function type, including the desired signature:

.. code-block:: dylan

  limited(<function>, signature: sig)

This area will be a subject of discussion for some time and will probably
involve some experimentation.

Modeling
--------

The first place to hook up function types is by implementing them as
*limited functions* within ``dfmc-modeling``. This is where the compile
time and run-time representations of objects are managed.

Apart from the topic covered in the next section, the basics of this are
fairly straight forward (using ``&class`` and ``&slot`` syntax available
within the compiler):

.. code-block:: dylan

  define primary &class <limited-function> (<limited-type>)
    constant &slot limited-function-signature :: <signature>,
      required-init-keyword: signature:;
  end;

  define method ^base-type (lf :: <limited-function>
   => (type :: <&type>)
    dylan-value(#"<function>")
  end;

The complicated part is defining how function types interact with
the type system.

Instance, Subtype and Disjoint Relations
----------------------------------------

It is necessary to determine how function types should fit into the
existing ``instance?``, ``subtype?`` and ``known-disjoint?`` relationships
between types. The main problem here will be determining the rules for
relationships between any two given function types.

This will need to be fully worked out as part of writing a DEP (Dylan
Enhancement Proposal), but an initial take on this has already been
implemented within the ``dfmc-typist`` in the long ago past.

The implementation of these relationships is somewhat complicated within
the compiler as there are 3 implementations:

* **Run-time.** This is implemented within the Dylan library and is
  available to user code.
* **Compile time.** This is implemented within the ``dfmc-modeling``
  library and represents what is known at compile time.
* **Type inference.** When performing type inference, types are tracked
  via *type estimates*, which have their own implementation of the
  type relationships.

It would be nice to find a way to simplify and improve this. In the
Gwydion Dylan compiler, for example, there was a single implementation.

Interaction With Currying and Partial Application
-------------------------------------------------

Currently, when using ``curry``, ``rcurry`` or the partial application
extension to the Dylan language, the generated functions do not have
very useful type signatures.  This can be seen by peeking at the
implementation of ``curry``:

.. code-block:: dylan

  define inline function curry
      (function :: <function>, #rest curried-args) => (result :: <function>)
    method (#rest args)
      %dynamic-extent(args);
      apply(function, concatenate-2(curried-args, args))
    end method
  end function curry;

We can see here that the compiler has lost all knowledge that it
might otherwise have had about the arguments, types and keyword
parameters that the curried function might take. This is unfortunate
and it would be nice to address it.

Library Improvements
--------------------

Functions defined in the standard library as well as various libraries
that Open Dylan ships with should be modified to use function types.
Optimal amounts of type safety will not yet be possible as we don't yet
support parametric polymorphism, but first steps using function types
can be made.

Other Implementation Issues
---------------------------

We don't really know yet what else will have to be changed to support
function types within the compiler. Presumably, some changes will be
required to the optimizer and perhaps code generation.

Some known areas to fix are:

* ``check-function-call`` in ``sources/dfmc/optimization/dispatch.dylan``.
  This attempts to validate call compatibility. It currently doesn't
  check if it doesn't know the function object involved.
* Error messages will need improvement and further work.

Testing
-------

While the ``dfmc-testing`` project has been brought back to life recently
for testing compiler internals, it doesn't perform sufficient tests of
subtyping and other areas yet. We will extend it to better test the areas
of the code that are being modified to support function types.

Some test improvements will also be needed within the tests for the
``dylan`` library.


Getting Started
===============

If this sounds like something you'd be interested in helping to work on,
please let us know in the ``#dylan`` channel on irc.freenode.net. There
are many opportunities to help out, as described above. Bruce Mitchener
has already started a branch that is in the early stages of supporting
function types.


In Closing
==========

Adding function types to the Dylan language and the Open Dylan
compiler is an interesting project, involving a wide range of
changes across the compiler codebase. It will provide functionality
that people have wanted from Dylan practically since Dylan was
created in the early 1990s.

*Thanks to Paul Khuong, an SBCL developer, for feedback on this article and
discussing how SBCL uses function types.*
