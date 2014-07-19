HTTP and Stream Processing
##########################

:author: Bruce Mitchener, Jr.
:date: 2014-7-19
:tags: Streams, Dylan 2016, HTTP
:status: draft

As we discussed in the `previous post`_, we are thinking about a new design
and implementation for the streams library in `Open Dylan`_.

While the examples in this post are in Dylan and are using code from our
HTTP server, these issues exist in many HTTP frameworks in many languages.
The code should be clear enough that little to no Dylan knowledge is required
to understand the points being made here.

What does this have to do with HTTP? There are several pain points in our
HTTP stack as it is currently written:

* Requests are read in their entirety into memory, so a large request (such
  as a file upload) takes a significant amount of memory.
* Responses often buffer their entire output in memory as well.
* Because of the use of the existing streams library, we don't handle
  non-blocking sockets and require a thread per socket.
* We don't have a good model for handling long-lasting connections such as
  might be used with `Server Sent Events`_ or `WebSockets`_ without tying
  up a thread for the duration of the socket being open.

We don't know yet what the new streams API will look like, but we can
look at our current HTTP implementation and see how streams will help
us solve the above issues. This can help inform the design of the new
streams API as well as help to make it clear why a new streams API
will be useful.

Other frameworks are already moving in this direction. One example is
`http4s`_ which builds on `scalaz-stream`_.

How does the HTTP server work currently?
========================================

The core of the server's processing looks like roughly like this,
after some unnecessary details have been removed:

.. code-block:: dylan

  let request = make(<request>, client: client);
  read-request(request);
  let response = make(<response>, request: request);
  route-request(server, request, response);
  finish-response(response);


A brief digression
==================

Now, we're creating a response prior to routing the request to the correct
handler. In other words, we have a type signature much like::

  (<http-server>, <request>, <response>) => ()

This has some interesting implications:

* The response's headers must be writable at all times as the handler may
  well want to set some headers (like ``Content-Length`` or ``Content-Type``).
  Now, setting a header after the response has already begun becomes a
  run-time error rather than an operation that isn't possible.
* A request can't specialize the type of response that is generated (if
  such a thing is desired).

If, instead, we operate with a signature like::

  (<http-server>, <request>) => (<response>)

Then we can ensure that all headers are set during the creation of the
response and not allow setting additional headers. This is a nice bit
of safety that falls out of a fairly simple change, but it doesn't have
much to do with stream processing.

As a result of the change to the signature of routing a request, we would
see the code for handling a connection become something like:

.. code-block:: dylan

  let request = make(<request>, client: client);
  read-request(request);
  let response = route-request(server, request);
  finish-response(response);

A downside to both of the above type signatures is that, given the current
implementation of everything, they require that the request be fully read
and that the response be fully generated before the thread is released and
can be used to handle another request.


How can Streams improve this?
=============================

Let's take some of the problems given above and address them individually.

Reading Requests
----------------

* Requests are read in their entirety into memory, so a large request (such
  as a file upload) takes a significant amount of memory.

This can already largely be addressed by the current Dylan streams library,
so long as we maintain the current assumption that reads can be blocking.

By moving to demand-driven, compositional streams though, we can make
a couple of improvements:

* Response handlers can read from the request's stream as they need and
  impose their own limits and restrictions on it without reading all of
  the data into memory. (An example might be varying limitations on the
  maximum allowed body size.)
* Byte vectors read from the network stream will need to be decoded into
  strings or other objects (JSON, `CBOR`_, XML, etc.). This can be handled
  by stages within the stream processing pipeline.

Writing Responses
-----------------

* Responses often buffer their entire output in memory as well.

This one is actually pretty easy! This is also already largely handled
by our existing streams library.

Currently, a ``<response>`` contains an output stream which is used
to implement HTTP/1.1 chunking (when allowed) and to handle output.
Where this currently falls down is for long-lasting connections as
we'll see below.

Another area for improvement in writing responses is handling the
encoding of values. This will be similar to handling the decoding
of request bodies by adding stages to the stream processing pipeline.

Parsing Requests versus Non-Blocking Sockets
--------------------------------------------

* Because of the use of the existing streams library, we don't handle
  non-blocking sockets and require a thread per socket.

Overall, to properly support non-blocking sockets, we want to have
the HTTP server's connection handling act as an incremental processing
of the I/O as it arrives rather than assuming that the entire HTTP
request is available at once or that it is okay to perform a
blocking read request.

Reviewing the code for ``read-request``, we can see that the way that
it is written now does not support non-blocking reads:

.. code-block:: dylan

  define method read-request (request :: <request>) => ()
    ...
    parse-request-line(server, request, buffer, len);
    read-message-headers(socket,
                         buffer: buffer,
                         start: len,
                         headers: request.raw-headers);
    process-incoming-headers(request);
    read-request-content(request);
  end method read-request;

Instead, we will want the server's per-connection code and the
``read-request`` code to cooperate to establish a pipeline for
reading the request and then dispatching that request to a handler,
which might then want to perform further reads. In a future post,
we will see better how stream libraries implement this sort of
incremental stream processing.

Long-Lasting Connections
------------------------

* We don't have a good model for handling long-lasting connections such as
  might be used with `Server Sent Events`_ or `WebSockets`_ without tying
  up a thread for the duration of the socket being open.

This is the final area that we'll cover for now for where streams can
improve our HTTP server.

At this point, our code for handling a request probably looks something
conceptually like this:

.. code-block:: dylan

  ...
  let response = route-request(server, request);
  finish-response(response);

Instead of finishing the response here, we want to set things up so that
when the output stream is closed, the code in ``finish-response`` gets
executed. We'll examine how that actually looks in a future post, but the
overall idea is that the pipeline that we discussed in the section
on reading responses will wait for the response body to be fully written
before finishing the response.

The pipeline would do the following:

* Read the request line.
* Read the request headers.
* Route the request and invoke the correct handler.
* Allow the handler to optionally read additional data from the request.
* The handler would return a response object. The response would have
  an output stream that may or may not be complete.
* The pipeline would wait for the response's output stream to be closed
  before finishing.

How does this help us with long-lasting connections? Well, the request
handler can create a queue or other mechanism for writing to the response
body stream and allow code to write to it. This could take many forms:

* Hooked up to a publish / subscribe system.
* A short lived queue while some work is done.
* A future or promise attached to some work that is being formed in
  the background.
* A database cursor that is processing results.
* And many other things...


Resource Management in the HTTP Server
======================================

Streams can manage the resources associated with the stages in the pipeline.
This is necessary as the execution of the pipeline is no longer something
that is readily handled by traditional Dylan mechanisms such as ``block``
expressions with ``cleanup`` clauses.

Some examples:

* A static file response handler can close the file that it was serving once
  that stage completes or when the socket driving the pipeline is closed.
* A websocket pipeline can unsubscribe from a notification system when the
  socket driving the pipeline is closed.


Summary
=======

In this post, we have identified places where an improved streams library
would help us to produce a better, more efficient, more capable HTTP
server. We have not yet identified exactly what this new code would look
like as we still aren't sure how it should look in Dylan, but hopefully
we have a better idea of the sorts of use cases and problems that we
would expect to use the stream processing code with.


.. _previous post: http://dylanfoundry.org/drafts/beginning-to-rethink-streams.html
.. _Open Dylan: http://opendylan.org/
.. _Server Sent Events: http://www.w3.org/TR/eventsource/
.. _WebSockets: http://tools.ietf.org/html/rfc6455
.. _CBOR: http://cbor.io/
.. _http4s: http://http4s.org/
.. _scalaz-stream: https://github.com/scalaz/scalaz-stream
