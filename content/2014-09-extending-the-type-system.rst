Extending the Type System
#########################

:author: Bruce Mitchener, Jr.
:date: 2014-9-10
:tags: Type System
:status: draft


The Dylan Reference Manaul does not define a mechanism for programmers
to define new types, this is left to the implementation.

In Open Dylan, this is currently limited to providing refinements on vectors
via ``limited(<vector>, of: ...)`` and new instances of the ``<limited-integer>``
type (which allows specifying the bounds on allowable integer values).

It would be interesting to look at what is involved in adding a new type
without compiler modifications, but that is not currently permissible in
the Open Dylan implementation. This sounds like a pretty interesting topic
though, so we'll likely take a look at it in a future blog post and set
of patches to Open Dylan. (An example of a new type would be generating
a type that represents constrained values based on a schema definition.)


