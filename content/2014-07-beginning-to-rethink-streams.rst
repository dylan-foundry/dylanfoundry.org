Beginning to Rethink Streams
############################

:author: Bruce Mitchener, Jr.
:date: 2014-7-18
:tags: Streams, Dylan 2016
:status: draft

Dylan's current ``streams`` library has served us moderately well
over the years. However, it has some issues which can be addressed
by a new design, expanding the range of problems for which it is
suited.


How things are now
==================

According to the current ``streams`` library's `documentation`_, the
`design goals`_ were:

* A generic, easy-to-use interface for streaming over sequences and files.
  The same high-level interface for consuming or producing is available
  irrespective of the type of stream, or the types of the elements being
  streamed over.
* Efficiency, especially for the common case of file I/O.
* Access to an underlying buffer management protocol.

One of the things it was explicitly **not designed** to handle was, again,
according to the `design goals`_ in the `documentation`_:

* A comprehensive range of I/O facilities for using memory-mapped files,
  network connections, and so on.

Unfortunately, the primary interface to our current `network library`_
is based on these very streams for which network connections were not
a design goal. While this works in practice, it imposes some important
limitations on our networking code. The biggest of these is that sockets
can not be non-blocking as it is expected that reads and writes will
complete. This prevents us from effectively utilizing event loops and
largely requires that networking code require a thread per connection.

This is only one of the ways in which the current design and implementation
of the streams library is limiting us.


The present and future?
=======================

The state of the art in stream libraries has advanced in the last 15+
years. Most recently, stream processing and data flow have been the
focus of libraries in Haskell such as `pipes`_, `conduit`_, and
`Machines`_. Similar libraries exist in Scala, like `scalaz-stream`_.
There is a new effort afoot to provide similar capabilities for
Java and Scala via `Reactive Streams`_.  A library that implements
some similar concepts for networking code, although not in a
functional programming manner, is `Netty`_. Another approach is taken
in the Play framework with `Iteratees`_.

Some of the primary concerns driving these more recent stream processing
libraries are:

* **Functional in nature.** A stream isn't an object, but rather a pipeline
  of functions.
* **Type safety.** Each stage of the stream processing has typed inputs and
  outputs. Some systems provide additional guarantees.
* **Compositional.** Streams can be composed with each other, just as
  functions can be.
* **Event driven.** Part of being CPU friendly is that streams only execute
  when data is available or something has changed.
* **Resource management friendly.** They should be CPU efficient, memory
  friendly (not requiring an entire dataset to be loaded into memory),
  and they should free resources (like closing open files) once they're
  completed.
* **Not focused around I/O itself.** Many stream usages might just be
  processing data.
* **Unbounded.** The stream may be unbounded in size.
* **Lazy.** Streams shouldn't do work unless there is demand.
* **No storage.** Streams typically don't store data, although they
  may perform some buffering.

This similar to the general concept of pipes, except that these are typically
both *push* and *pull*. When the consumer is faster than the producer, the
producer is pushing to the consumer. When the consumer is slower than the
producer, then the consumer is pulling from the producer.


Examples from other frameworks
==============================

What does code look like using some of these frameworks?

This is a very simple network server using Haskell's `conduit`_
and some additional libraries:

.. code-block:: haskell

  {-# LANGUAGE OverloadedStrings #-}
  import           Conduit
  import           Data.Conduit.Network
  import           Data.Word8           (toUpper)

  main :: IO ()
  main = runTCPServer (serverSettings 4000 "*") $ \appData ->
      appSource appData $$ omapCE toUpper =$ appSink appData

It is explained in a blog post about `network-conduit examples`_:

  runTCPServer takes two parameters. The first is the server settings,
  which indicates how to listen for incoming connections. Our two
  parameters say to listen on port 4000 and that the server should
  answer on all network interfaces. The second parameter is an Application,
  which takes some AppData and runs some action. Importantly, our app data
  provides a Source to read data from the client, and a Sink to write data
  to the client. (There's also information available such as the SockAddr
  of the client.)

  The next line is a very trivial conduit pipeline: we take all data from
  the source, pump it through ``omapCE toUpper``, and send it back to the
  client.  ``omapCE`` is our first taste of *conduit-combinators*: ``omap``
  means we're doing a monomorphic map (on a ``ByteString``), and ``C``
  means conduit, and ``E`` means "do it to each element in the container."

Hopefully that is fairly clear without necessarily having a lot of
Haskell knowledge.

------

This is an example of a program that loads a file, converts values
from Fahrenheit to Celsius and saves the results in a new file,
using the `scalaz-stream`_ framework in Scala:

.. code-block:: scala

  import scalaz.stream._
  import scalaz.concurrent.Task

  val converter: Task[Unit] =
    io.linesR("testdata/fahrenheit.txt").
       filter(s => !s.trim.isEmpty && !s.startsWith("//")).
       map(line => fahrenheitToCelsius(line.toDouble).toString).
       intersperse("\n").
       pipe(text.utf8Encode).
       to(io.fileChunkW("testdata/celsius.txt")).
       run

  val u: Unit = converter.run

This example is explained in depth in the `scalaz-stream examples`_.
An interesting thing about this example is that the entire file is
not read into memory to convert it into lines. Instead, it is streamed
through memory bit by bit, keeping memory consumption to a reasonable
and hopefully constant amount.


Callbacks? No!
==============

One thing that we definitely want to avoid is the phenomenon known
as "callback hell". This is common in some frameworks such as Node.js
(without using their stream libraries) and Python's `Twisted`_.

In frameworks using callbacks, the flow of control is often difficult
to visualize from the code and the flow of the code is often confusing
or inverted.

There are ways to avoid callbacks in these frameworks, such as using
``defer.inlineCallbacks`` in Twisted. But the overall pattern of
relying upon chains of callbacks is something that we wish to avoid.


What should stream processing look like in Dylan?
=================================================

Neither of the above resemble anything like idiomatic Dylan. What
should a new generation of a stream library look like in Dylan?

I don't have an answer for that yet, but I will explore that in
subsequent posts.

Some interesting questions to consider along the way:

* To what extent should we use **functions versus multiple dispatch**?
* Should any part of the system **be modelled as objects**?
* How **concise and readable** can we make things, while still keeping
  the overall **design and usage approachable**?
* How closely should we hew to the **terminology** used in other
  frameworks and languages? (Note that many of the frameworks already
  don't share a lot of terminology with each other.)
* Should this replace all usages of our current streams library?
* What level of **type safety** can be achieved with the current version
  of the Dylan language and compiler? What sort of extensions might
  we consider to improve this for `Dylan 2016`_?
* Similarly, what level of **performance and optimization** is our
  current compiler capable of producing on highly functional
  code and what improvements can or should be made in that area?

Further, what sort of use cases would we expect to see taking
advantage of a new stream processing framework?  We'll explore
this in the next blog post about stream processing and HTTP.

.. _documentation: http://opendylan.org/documentation/library-reference/io/streams.html
.. _design goals: http://opendylan.org/documentation/library-reference/io/streams.html#goals-of-the-module
.. _network library: http://opendylan.org/documentation/library-reference/network/index.html
.. _pipes: https://hackage.haskell.org/package/pipes
.. _conduit: https://hackage.haskell.org/package/conduit
.. _Machines: https://hackage.haskell.org/package/machines
.. _scalaz-stream: https://github.com/scalaz/scalaz-stream/
.. _Reactive Streams: http://www.reactive-streams.org/
.. _Netty: http://netty.io/
.. _Iteratees: http://www.playframework.com/documentation/2.0/Iteratees
.. _network-conduit examples: http://www.yesodweb.com/blog/2014/03/network-conduit-async
.. _scalaz-stream examples: https://github.com/scalaz/scalaz-stream/blob/master/src/test/scala/scalaz/stream/examples/StartHere.scala
.. _Twisted: https://twistedmatrix.com/trac/
.. _Dylan 2016: https://lists.opendylan.org/pipermail/hackers/2014-April/007032.html
