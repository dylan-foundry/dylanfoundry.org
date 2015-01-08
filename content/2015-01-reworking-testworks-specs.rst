Reworking testworks-specs
#########################

:author: Bruce Mitchener, Jr.
:date: 2015-01-12
:status: draft

In the Dylan community, we've long had a testing framework called
`Testworks`_. This framework is used for almost all of the testing
done on Dylan libraries.

A typical set of tests might look something like:

.. code-block:: dylan

   define test buffer-creation-test ()
     let new-buffer = make-empty-buffer(<non-file-buffer>);
     dynamic-bind(*buffer* = new-buffer)
       check-equal("New buffer is in fundamental mode",
                   buffer-major-mode(new-buffer),
                   find-mode(<fundamental-mode>));
       let node = buffer-start-node(new-buffer);
       let end-node = buffer-end-node(new-buffer);
       check-true("New buffer contains exactly 1 node",
                  node == end-node & node ~== #f);
       ...
     end;
   end test;

   define suite buffer-suite ()
     test buffer-creation-test;
     test buffer-change-test;
     test buffer-structure-test;
     test buffer-characters-test;
   end suite;

A series of revisions to *testworks* last year simplified the internals
substantially and allowed the compiler to warn when tests weren't used
in a suite, among other things.

Introducing testworks-specs
---------------------------

There's another library built on top of *testworks* though,
*testworks-specs*.  *testworks-specs* provides a different structure
for writing tests and lets you re-state what the exported interface
of a module / library should look like and write tests against that.
This is done via a set of macros and code that layers on top of
*testworks*.

A typical specification and tests might look like:

.. code-block:: dylan

   define module-spec pprint ()
     variable *print-miser-width*   :: false-or(<integer>);
     variable *default-line-length* :: <integer>;

     sealed instantiable class <pretty-stream> (<stream>);

     function pprint-logical-block (<stream>) => ();
     function pprint-newline (one-of(#"linear", #"fill", #"miser", #"mandatory"), <stream>) => ();
     function pprint-indent (one-of(#"block", #"current"), <integer>, <stream>) => ();
     function pprint-tab (one-of(#"line", #"line-relative", #"section", #"section-relative"),
                          <integer>, <integer>, <stream>) => ();

     macro-test printing-logical-block-test;
   end module-spec pprint;

   define module-spec print ()
     ...
     open generic-function print-object (<object>, <stream>) => ();
     ...
   end module-spec print;

   define library-spec io ()
     module streams;
     module pprint;

     suite format-test-suite;
   end library-spec io;

And, separately:

.. code-block:: dylan

   define pprint function-test pprint-newline ()
     //---*** Fill this in...
   end function-test pprint-newline;

When these tests are run, *testworks-specs* will inspect the exported
bindings and ensure that they obey the specifications defined in the
tests. It will also run the associated tests, like that ``function-test``
for ``pprint-newline``.

This is great, and it works pretty well.

Problems with testworks-specs
-----------------------------

However, there are, of course, some problems.

* *testworks-specs* is written in the style of the old *testworks* where
  many things were determined and validated at run-time rather than compile
  time.
* Because *testworks-specs* was written in the old style, it didn't
  integrate at all with features in *testworks* like being able to list
  the available test suites and individual tests, nor did it support
  ignoring or skipping a given suite or test. Features like tagging
  tests also were not supported for *testworks-specs*.
* *testworks-specs* isn't documented and hasn't been well understood by
  the Dylan community for many years.
* Tests for functions and so on were at a high level of granularity. Any
  given function might have several tests that it needs to run. This was
  supported in the past by using a macro ``with-test-unit`` that would
  create a new test at run-time with a body of code. While this was okay
  with the old implementation of *testworks*, it wasn't a great option
  in the new implementation.

As a result, I decided to rework the implementation of *testworks-specs*
to begin addressing these issues and to (hopefully) provide a more stable
foundation for the future.

Switching to Compile-time
-------------------------

One of the first steps that I took was to rewrite how the macros for
*testworks-specs* are expanded. Instead of generating code to register
tests that are then run through special-purpose code, they now generate
normal *testworks* tests and suites.

For example, the ``function-test`` macro is simply implemented as:

.. code-block:: dylan

   define macro function-test-definer
     { define ?protocol-name:name function-test ?function-name:name ()
         ?body:body
       end }
       => { define test "test-function-" ## ?function-name (requires-assertions?: #f)
              ?body
            end }
   end macro function-test-definer;

This is a work in progress at this point. The above definition doesn't
do anything with the ``?protocol-name``, nor does it provide for passing
keyword options to the generated test. (It simply supplies
``requires-assertions?: #t`` to allow unimplemented tests to not be
considered as failures.)

One advantage of this new implementation is that when a ``function-test``
or other test is present, but there's no corresponding ``function`` or
other binding in the specification, then a warning will be issued by
the compiler that the test is not referenced or exported (and is therefore
unused).

Also, when the type of binding given in the specification doesn't exactly
match the type of test (so, saying ``constant <file-type>`` in the specification,
but having a ``class-test`` for it), a compiler error will result.

Intricacies of Testing Classes
------------------------------

Testing classes is an interesting aspect of *testworks-specs* and it
throws a couple of complications into our easy macro expansion for
``class-test``.

First up, classes that are listed in the specification with the adjective
``instantiable`` are tested as part of the specification checking to be
sure that the class can actually be instantiated. This requires a bit
of support from the programmer in the case where the class requires
arguments to be passed to the ``make`` method to create an instance of
the class. To do this, create a specialization on the ``make-test-instance``
method for the class being tested:

.. code-block:: dylan

   define sideways method make-test-instance
       (class == <machine-word>)
    => (instance :: <machine-word>)
     make(<machine-word>, value: 1729)
   end method make-test-instance;

This works fine with both the old and new implementations of
*testworks-specs*.

Next, we sometimes want to share a lot of code between tests of various
classes. This is common with stream or numeric classes. To do this,
another technique had been employed. Previously, ``class-test`` would
expand to a ``definition-test``, which would in turn expand to a method,
``test-protocol-definition``:

.. code-block:: dylan

   define macro class-test-definer
     { define ?protocol-name:name class-test ?class-name:name ()
         ?body:body
       end }
       => { define ?protocol-name definition-test ?class-name () ?body end }
   end macro class-test-definer;

   define macro definition-test-definer
     { define ?protocol-name:name definition-test ?definition-name:name ()
         ?body:body
       end }
       => { define sideways method test-protocol-definition
                (protocol :: <protocol-spec>,
                 protocol-name == ?#"protocol-name",
                 definition    == ?#"definition-name")
             => ()
              ?body
            end method test-protocol-definition }
   end macro definition-test-definer;

There was a default implementation of ``test-protocol-definition``
though which would be run if there was no ``class-test`` generating
a method to override it. This method would use ``class-test-function``
to locate the testing code for the class and then invoke it:

.. code-block:: dylan

   let test-function = class-test-function(class);
   if (test-function)
     let instantiable? = protocol-class-instantiable?(spec, class);
     let abstract? = protocol-class-abstract?(spec, class);
     test-function(class,
                   name: spec-title(definition-spec),
                   abstract?: abstract?,
                   instantiable?: instantiable?);

This mechanism will no longer work in exactly this manner with the
new implementation strategy for *testworks-specs*.

Instead, we will have to generate code for classes that is a little
bit different from the other test types. Unfortunately, this code
won't be able to have as have as much error checking at compile time.

*Explain it more?*


Supporting Multiple Tests
-------------------------

*This isn't worked out yet, and so this section can not be written yet.*

.. _Testworks: http://opendylan.org/documentation/testworks/
