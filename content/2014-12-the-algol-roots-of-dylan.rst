The ALGOL Roots of Dylan
########################

:author: Bruce Mitchener, Jr.
:date: 2014-12-10
:status: draft

Dylan is often seen as a descendent of the Lisp family of languages. It
was designed (and implemented) by people from the `Common Lisp`_ world and
borrowed lots from `Scheme`_, `EuLisp`_ and other Lisp dialects. On the
other hand, it was given a syntax from the `ALGOL`_ tradition rather than
using `s-expressions`_.

It is interesting to compare some of what is present within the Dylan
language design with `ALGOL`_ though and see if perhaps some of the
ALGOL influence wasn't just in the syntax. It is difficult today to
know the extent to which ALGOL 68 was a direct influence versus having
been filtered through Common Lisp and other languages. After all, Dylan
was designed some 25 years or so after ALGOL 68. (At the time of this
writing, Dylan itself is over 20 years old.)

It is clear though that many languages have picked up ideas from
ALGOL over the years, including languages that were direct influencers
of Dylan such as Scheme.

This post isn't intended to say "this concept came from ALGOL" but just
to look at some of the interesting similarities.

Orthogonal Design
=================

`ALGOL 68`_ as defined in the `Revised Report on the Algorithmic Language
ALGOL 68`_ and one of the design goals `noted there`_ is that it should
have an *orthogonal design*:

    The number of independent primitive concepts has been minimized in
    order that the language be easy to describe, to learn, and to
    implement. On the other hand, these concepts have been applied
    "orthogonally" in order to maximize the expressive power of the
    language while trying to avoid deleterious superfluities.

This is something that was (largely) followed when designing Dylan as
well. (It is arguably complicated somewhat by the addition of macros.)

While this wasn't a design goal for, say, Common Lisp which had other design
goals, Scheme was designed to be a much more minimal Lisp. Looking around
today, this clearly isn't a design goal for many of the popular languages
of today like C++, Java, Scala or Ruby.

Lexical Scope and Block Structure
=================================

Interestingly, `lexical scope originated`_ in ALGOL and was picked up by
many languages after that. While Scheme uses lexical scope, Common Lisp
permits dynamic scope as well. Dylan uses lexical scope.

Similarly, the block structure of Scheme (and Dylan) originated with ALGOL.

Union Types
===========

ALGOL 68 introduced the concept of "united modes", or what we now know as
"union types" in many modern languages.

In ALGOL 68, this would look like::

    MODE node = UNION (REAL, INT, STRING);

In Dylan, this would look like:

.. code-block:: dylan

    let <node> = type-union(<real>, <integer>, <string>);

In Dylan, types are values, so we just use a regular old variable to store
the new type.

Common Lisp supports union types via ``or`` and compilers can use union types
internally, as described in the `CMUCL User's Manual`_.

Expression Oriented
===================

ALGOL 68 was an expression-oriented language. This meant that all constructs
in the language could be used as expressions. (This is typical in a Lisp
as well as many other languages today.)

In ALGOL 68, this was valid code::

    INT output := IF input = 2 THEN 42 ELSE 4711 FI;

Control Flow
============

...

In Closing
==========

Hopefully, this gives you a taste for some of the many influences that
`ALGOL`_ and `ALGOL 68_` had on subsequent programming languages and,
in particular, on Dylan.

ALGOL and ALGOL 68 were very interesting languages in their own rights
and drove a lot of innovation in their own times. Some of these ideas
survived through to the current day (call by value vs call by name
parameters for example), while others have fallen by the wayside
(like allowing spaces in variable names or Van Wijngaarden grammars).

Further Reading
===============

* `The History of the ALGOL Effort`_ by HT de Beer.
* `The Design of Elegant Languages`_ by Lambert Meertens.
* `Djikstra's Crisis: The End of Algol and Beginning of Software Engineering, 1968-72`_
  (draft) by Thomas Haigh.
* `ALGOL 68g`_, an open source implementation of ALGOL 68.

.. _Common Lisp: http://en.wikipedia.org/wiki/Common_Lisp
.. _Scheme: http://en.wikipedia.org/wiki/Scheme_%28programming_language%29
.. _EuLisp: http://en.wikipedia.org/wiki/EuLisp
.. _ALGOL 68: http://en.wikipedia.org/wiki/ALGOL_68
.. _ALGOL: http://en.wikipedia.org/wiki/ALGOL
.. _s-expressions: http://en.wikipedia.org/wiki/S-expression
.. _Revised Report on the Algorithmic Language ALGOL 68: http://jmvdveer.home.xs4all.nl/report.html#012
.. _noted there: http://jmvdveer.home.xs4all.nl/report.html#012
.. _lexical scope originated: http://en.wikipedia.org/wiki/Scope_%28computer_science%29#History
.. _CMUCL User's Manual: http://common-lisp.net/project/cmucl/doc/cmu-user/compiler-hint.html#toc146
.. _The History of the ALGOL Effort: http://heerdebeer.org/ALGOL/The_History_of_ALGOL.pdf
.. _The Design of Elegant Languages: http://www.kestrel.edu/home/people/meertens/publications/papers/The_design_of_elegant_languages.pdf
.. _Djikstra's Crisis\: The End of Algol and Beginning of Software Engineering, 1968-72: http://www.tomandmaria.com/tom/Writing/DijkstrasCrisis_LeidenDRAFT.pdf
.. _ALGOL 68g: http://jmvdveer.home.xs4all.nl/
