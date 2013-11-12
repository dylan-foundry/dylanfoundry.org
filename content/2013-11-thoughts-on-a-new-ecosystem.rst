Thoughts on a New Dylan Ecosystem
#################################

:author: Bruce Mitchener, Jr.
:date: 2013-11-12

Dylan is in an unusual position for a programming language.

It has a pretty mature implementation, a specification, and a lot
of high quality documentation. It has a long history and many
people remember it from the early days of its history when it
was being developed at Apple and other institutions.

On the other hand, the current community is fairly small as is
the available set of libraries. This is typically a disadvantage,
however it can be used to the community's advantage in a couple
of ways.

Looking Forward
===============

One way is that we can look forward and take advantage of what we
know and want now without having to worry about backward compatibility.

A parallel might be seen with the early days of Node.js.  Early
on, Node.js was also working with a programming language with
a specification and a mature implementation. However, Node.js was
using JavaScript in a new way: to create server-side software
employing asynchronous and non-blocking techniques. A big advantage
that Node.js had was that there wasn't a large collection of
libraries for doing server-side programming. The developers could
(largely) start from a clean slate, producing libraries that fit
in with the non-blocking, asynchronous nature that Node.js wanted
to encourage.

On the opposite side of this are languages like Python where
there is no one solution for handling non-blocking I/O and so
some libraries do one thing, others do something else, and large
parts of the standard library don't deal with it at all.

In Scala and Java, there's no coherent strategy for tracing
execution, metrics gathering or concurrency. Twitter (as an example)
has solved this for themselves by producing a `large set of libraries`_
that stand on their own and integrate together, but they don't
integrate well with other frameworks from other companies (like,
say, Akka). Logging used to be an issue, but this has largely been
solved by `slf4j-api`_.

In these (and many other) cases, you see fragmentation amongst the
libraries as newer considerations that weren't present when the
initial libraries were written get dealt with separately rather than
as part of the language's core libraries.

Clojure is a demonstration of how a language can benefit from being
forward-looking by having a rich and comprehensive set of concurrency
primitives that are available as part of the standard library.

How might this work with Dylan? What core concepts do we want to
support throughout our software stacks to give us an advantage
over others?

A few things come to mind:

* Fully integrated tracing framework.
* Coroutine-based solution to non-blocking and asynchronous work.
* A solid approach to Unicode strings and byte buffers.

Tracing
-------

We have just produced a new `tracing library`_ (based on Google's
`Dapper`_) for use in Dylan software. We should be able to readily
integrate it with the `HTTP`_, `concurrency`_, `nanomsg`_ and
database libraries and other libraries in the future. Any server
side software using Dylan should be able to have awesome tracing
support from day one.

Coroutines
----------

Event-driven software often means having to use callbacks. While
we can support callbacks in Dylan without any issue, it is also
nice to be able to use coroutines to have more natural looking
code. We can integrate coroutines as a threading model within
the compiler, runtime and common libraries, including the I/O
libraries.

Unicode
-------

We should have a clear distinction between buffer (byte vector)
types and strings. Strings should be Unicode and this should be
supported by all libraries.  This was something that was done
in Python 3.0 and is a great improvement over the past.

Other things
------------

We should look at improving our concurrency support and our usage
of (functional) data structures that are better suited for
concurrency. But there are probably many other ways that we can
help build libraries that are well suited for the future.

Quality
=======

Another way that we can benefit from having a small community and set of
libraries now is where we set the bar for quality and lead the next
generation of Dylan developers to follow.

We should require that all packages / libraries follow some guidelines:

* Consistent documentation tooling.
* Consistent testing framework usage.

We should be conservative about accepting new packages and generous
in offering up resources like continuous builds to help everyone
achieve these goals.

This is an area where Perl has done very well with CPAN. Packages have
a consistent build, test, and documentation procedure: something we should
aim to emulate.

Documentation Tools
-------------------

All of our documentation is written using `Sphinx`_ using our Dylan
extensions. By having a single toolset for all of our documentation,
we'll be able to build new tools on top of that. An example would be
writing a JSON exporter and providing searchable, browsable documentation
using something like ElasticSearch on the back-end.

Testing Framework
-----------------

We have a solid testing framework in `Testworks`_. While it can
be augmented in some ways, like providing property-based testing
support ala `QuickCheck`_, it already serves our purposes pretty
well. Having a single testing framework also makes tool integration
much easier.

Help!
=====

If this sounds interesting to you or the idea of working on new libraries
sounds appealing, please get `in touch`_ with us in the Open Dylan
community on IRC or our mailing list.

`Sic itur ad astra!`_

.. _large set of libraries: https://github.com/twitter/finagle/
.. _slf4j-api: http://www.slf4j.org/
.. _tracing library: https://github.com/dylan-foundry/tracing/
.. _Dapper: http://research.google.com/pubs/pub36356.html
.. _HTTP: https://github.com/dylan-lang/http/
.. _concurrency: https://github.com/dylan-foundry/concurrency/
.. _nanomsg: https://github.com/dylan-foundry/nanomsg-dylan/
.. _Sphinx: http://sphinx-doc.org/
.. _Testworks: https://github.com/dylan-lang/testworks/
.. _QuickCheck: http://en.wikipedia.org/wiki/QuickCheck
.. _in touch: http://opendylan.org/community/index.html
.. _Sic itur ad astra!: http://en.wikipedia.org/wiki/Ad_astra_(phrase)