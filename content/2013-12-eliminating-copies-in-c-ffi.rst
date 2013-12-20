Eliminating Copies in C-FFI
###########################

:author: Bruce Mitchener, Jr.
:date: 2013-12-8
:tags: Tutorials, C-FFI

We've run into a situation fairly regularly when wrapping C libraries where
we'd like to avoid making extra copies of data when passing it between Dylan
and C code via the `C-FFI`_.  Related to this, we want to be able to use
multiple types from the Dylan side of things such as `\<buffer>`_,
`\<byte-vector>`_ or `\<byte-string>`_ without having to have separate code
paths for each of them. Each of these classes can store raw byte data that
we may want to share with other code.

An example that we'll work with in this discussion comes from `bindings`_
(in simplified and excerpted forms) for the `LevelDB`_ library:

.. code-block:: c

    extern void leveldb_put(
        leveldb_t* db,
        const leveldb_writeoptions_t* options,
        const char* key, size_t keylen,
        const char* val, size_t vallen,
        char** errptr);

<C-string>
==========

The easiest way to bind ``leveldb_put`` would be to use ``<C-string>``:

.. code-block:: dylan

    define C-function %leveldb-put
      input parameter db_ :: <leveldb-t*>;
      input parameter options_ :: <leveldb-writeoptions-t*>;
      input parameter key_ :: <C-string>;
      input parameter keylen_ :: <size-t>;
      input parameter val_ :: <C-string>;
      input parameter vallen_ :: <size-t>;
      output parameter errptr_ :: <char**>;
      c-name: "leveldb_put";
    end;

However, this would mean that every key and value would have to be copied
from an existing byte container (like ``<buffer>``, ``<string>`` or
``<byte-vector>``) to a ``<C-string>``. That's what we'd like to avoid.

primitive-string-as-raw
=======================

If we were just dealing with strings, we could use Open Dylan primitives,
``primitive-string-as-raw`` and ``primitive-wrap-machine-word``.

``primitive-string-as-raw`` gives us access to the raw internal storage
of a ``<byte-string>`` which is guaranteed to be NULL terminated.

However, this doesn't solve our problem as it doesn't provide us with an
answer for other byte container types, so we'll move along without
going through all of the details.

An Excursion Into Run-time Representations
==========================================

To go further, we need to understand how some parts of the Dylan object
model are represented in memory, and in particular, how ``<buffer>``,
``<byte-string>`` and ``<byte-vector>`` are.

Taking an example definition of ``<byte-string>``, we would see something
like this:

.. code-block:: dylan

    define class <byte-string> (<string>, <vector>)
      repeated slot string-element :: <byte-character>,
        init-value:        ' ',
        init-keyword:      fill:,
        size-init-value:   0,
        size-init-keyword: size:,
        size-getter:       size;
    end class;

What's special there is the ``repeated slot string-element``. In Open Dylan,
repeated slots are used for all vector types. To see what that means in C, let's
look at how a string is represented when emitted by the C back-end for the
Open Dylan compiler:

.. code-block:: c

    static _KLbyte_stringGVKd_3 K148 = {
      &KLbyte_stringGVKdW,
      (D) 13,
      "abc"
    };

In the C runtime, we have a C preprocessor macro for creating these struct
definitions:

.. code-block:: c

    define define_byte_string(_name, _size) \
      typedef struct _bs##_name { \
        D class; \
        D size; \
        char data[_size + 1]; \
      } _name

What this means is that it is using an old (but good technique) of storing the
string data in the same struct as everything else, avoiding an extra memory
allocation and redirection which would've been necessary had it been defined
with a ``char *`` pointer to the data. In short, a repeated slot causes the
underlying struct to have an extra size member and an array for the data.

``<buffer>`` and ``<byte-vector>`` have similar definitions. In the case of
``<buffer>``, it has a number of extra variables, so the offset into the
struct to access the byte data is different from ``<byte-string>`` or
``<byte-vector>``.

Putting It All Together
=======================

What we'd like to do is to be able to pass the address of the raw storage
to the underlying C function. In Dylan, we use a `\<machine-word>`_ to
do this. So, given an object, we want to get the address of the raw
underlying repeated slot storage, so we can define a function like this:

.. code-block:: dylan

    define function byte-storage-address
        (the-buffer)
     => (result-offset :: <machine-word>)
          primitive-wrap-machine-word
            (primitive-repeated-slot-as-raw
               (the-buffer, primitive-repeated-slot-offset(the-buffer)))
    end function;

This function will work on any of ``<buffer>``, ``<byte-string>`` or
``<byte-vector>``.

Now, since we'll want to pass a machine word, we have to teach the C-FFI
how to deal with that, and we can do that with a `mapped subtype`_:

.. code-block:: dylan

    define simple-C-mapped-subtype <C-storage-address> (<C-void*>)
      export-map <machine-word>, export-function: identity;
    end;

A mapped subtype specifies how data is exchanged between Dylan and the
C world. In this case, we're specifying that ``<C-storage-address>``
is a subtype of ``<C-void*>`` that is handled on the Dylan side using
a ``<machine-word>``.

And then we can alter the parameter definitions in our C-FFI definition
as follows:

.. code-block:: dylan

    define C-function %leveldb-put
      input parameter db_ :: <leveldb-t*>;
      input parameter options_ :: <leveldb-writeoptions-t*>;
      input parameter key_ :: <C-storage-address>;
      input parameter keylen_ :: <size-t>;
      input parameter val_ :: <C-storage-address>;
      input parameter vallen_ :: <size-t>;
      output parameter errptr_ :: <char**>;
      c-name: "leveldb_put";
    end;

And then we can invoke it as follows:

.. code-block:: dylan

    %leveldb-put(db, options, byte-storage-address(key), key.size,
                 byte-storage-address(value), value.size)

Further improvements to this are possible, such as passing an offset
to the ``byte-storage-address`` function to let us do subsequences
of the original byte container:

.. code-block:: dylan

    define inline function byte-storage-offset-address
        (the-buffer, data-offset :: <integer>)
     => (result-offset :: <machine-word>)
      u%+(data-offset,
          primitive-wrap-machine-word
            (primitive-repeated-slot-as-raw
               (the-buffer, primitive-repeated-slot-offset(the-buffer))))
    end function;

Another Example
===============

You can also use this for writing into a byte container as we do
within the `hash-algorithms`_ library.

Previously, we had to copy data when interacting with the C-FFI binding
for ``final-sha1``:

.. code-block:: dylan

    define C-function final-sha1
      parameter hash :: <C-unsigned-char*>;
      parameter context :: <sha1-context>;
      c-name: "sha1_Final"
    end;

    define method digest (hash :: <sha1>) => (result :: <byte-vector>)
      let res = make(<byte-vector>, size: 20);
      let storage = make(<C-unsigned-char*>, element-count: 20);
      final-sha1(storage, hash.context);
      for (i from 0 below 20)
        res[i] := as(<byte>, storage[i]);
      end;
      destroy(storage);
      res;
    end;

This again is a copy that we don't want or need, and using the same
techniques as above, we can eliminate it:

.. code-block:: dylan

    define C-function final-sha1
      parameter hash :: <C-storage-address>;
      parameter context :: <sha1-context>;
      c-name: "sha1_Final"
    end;

    define method digest (hash :: <sha1>) => (result :: <byte-vector>)
      let res = make(<byte-vector>, size: 20);
      final-sha1(byte-storage-address(res), hash.context);
      res;
    end;

And now, the ``digest`` method lets ``final-sha1`` write directly into the
byte storage area for the ``<byte-vector>``.

Dangers
=======

Using Open Dylan primitives like ``primitive-string-as-raw`` and
``primitive-repeated-slot-as-raw`` is unsafe. When using these primitives
and others like them, it is possible to access memory in a way that
can result in memory corruption or crashes.

Wrap Up
=======

While it isn't always necessary to wring out every drop of performance
from a C-FFI binding, it is sometimes necessary or useful. Hopefully,
you now have a better understanding of how you can eliminate data
copies as well as some of how objects are laid out in memory by the
Open Dylan compiler and run-time.

.. _C-FFI: http://opendylan.org/documentation/library-reference/c-ffi/
.. _<buffer>: http://opendylan.org/documentation/library-reference/io/streams.html#io:streams:[buffer]
.. _<byte-vector>: http://opendylan.org/documentation/library-reference/io/streams.html#io:streams:[byte-vector]
.. _<byte-string>: http://opendylan.org/books/drm/Collection_Classes#byte-string
.. _bindings: https://github.com/dylan-foundry/leveldb-dylan/
.. _LevelDB: https://code.google.com/p/leveldb/
.. _<machine-word>: http://opendylan.org/documentation/library-reference/common-dylan/machine-words.html
.. _mapped subtype: http://opendylan.org/documentation/library-reference/c-ffi/#c-ffi:c-ffi:definec-mapped-subtype
.. _hash-algorithms: http://opendylan.org/documentation/library-reference/hash-algorithms/
