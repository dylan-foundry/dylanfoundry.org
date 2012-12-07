About
#####

The Dylan Foundry is working on tools and libraries to make it easier to
use the `Dylan <http://opendylan.org/>`_ programming language in production.

Currently under development are libraries covering these areas:

* Database access, including sqlite3, PostgreSQL and LevelDB.
* An improved networking library.
* Improvements to the Dylan HTTP libraries.
* ... and lots more.

The Dylan Foundry is sponsored by `DataFueled <http://datafueled.com/>`_.

What is Dylan?
==============

Dylan is a programming language that was originally created at Apple Computer
in the early 1990s. It was subsequently developed by teams at Apple Computer,
Harlequin, and Carnegie Mellon University. The Harlequin implementation of Dylan
lives on today as an open source project, `Open Dylan <http://opendylan.org/>`_.

Dylan was strongly influenced by the Scheme and Common Lisp programming
languages, but uses a syntax derived from the Algol and Pascal tradition.

The `Introduction to Dylan <http://opendylan.org/documentation/intro-dylan/>`_
gives a nice and easy overview of the language.

Why Dylan?
==========

We love the language and find it both productive and satisfying to work
with. A craftsman should love his tools and Dylan is what makes us happy.

But why?

Some things that we like about Dylan are:

* The syntax is clear and consistent. While it is sometimes verbose,
  it remains highly readable.
* The type system allows for static typing as well as a looser,
  more dynamic view of the world.
* It provides multi-methods and a consistent and ever-present
  object system.
* It provides for a mixture of object-oriented and functional
  programming.
* It allows for multiple return values, ``rest`` arguments,
  and keyword arguments.
* It has a condition system like Common Lisp.
* It has a powerful macro system.
* Dylan compiles to an efficient executable.

Overall, Dylan gives the programmer a flexible set of primitives
to build on and these primitives mesh together well. You don't
find yourself wondering how various language features fit together.

We've used many other languages in the past and in the intervening
years since discovering Dylan, but keep getting drawn back. Dylan
is something special.

Learning More
=============

Dylan has a large amount of documentation available:

* `Introduction to Dylan <http://opendylan.org/documentation/intro-dylan/>`_:
   A tutorial is written primarily for those with solid programming
   experience in C++ or another object-oriented, static language. It
   provides a gentler introduction to Dylan than does the Dylan
   Reference Manual (DRM).
* `Dylan Reference Manual <http://opendylan.org/books/drm/>`_:
   The official definition of the Dylan language and standard library.
* `Dylan Programming Guide <http://opendylan.org/books/dpg/>`_:
   A good, book length Dylan tutorial by several Harlequin employees.


What does Dylan look like?
==========================

Much like pictures are worth a thousand words, snippets of a programming
language can help to communicate the essence of the language.

A simple factorial, using recursion and multi-method dispatch:

.. code-block:: dylan

  define method factorial (n == 0) 1 end;
  define method factorial (n == 1) 1 end;

  define method factorial (n)
    n * factorial(n - 1)
  end;

A simple fibonacci sequence generator, using a closure:

.. code-block:: dylan

  define function make-fibonacci()
    let n = 0;
    let m = 1;
    method ()
      let result = n + m;
      n := m;
      m := result  // return value
    end
  end;

  define constant fib = make-fibonacci();

  for (i from 1 to 15)
    format-out("%d ", fib())
  end;
