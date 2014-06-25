Integrating with LLDB
#####################

:author: Bruce Mitchener, Jr.
:date: 2014-6-25
:tags: Debugging, LLDB

I spend a lot of time debugging Dylan code. Up until now, this has been a
somewhat painful process when not using the IDE on Windows. (And I don't
really use the IDE on Windows as it doesn't fit well into my workflow.)
I finally reached the point where I decided that I wanted to improve our
debugger integration.

Much of what is described below may be applicable to people working on
debugging support for other languages.

Current State of Dylan Debugging
================================

We have a debugger on Windows integrated with our IDE. This facility is
not available on the other platforms that we support. There are many reasons
for this:

* The debug info that Open Dylan generates is only done on Windows.
* The debugger code for interacting with the OS is only implemented for Windows.
* The IDE itself is only available on Windows.

This means that debugging on Linux, FreeBSD and Mac OS X has traditionally
been more challenging. We often resort to "printf debugging" and have
some basic debug printing functions that can be invoked from the compiler
so long as they don't crash. Debugging is really only effective with the
C back-end as the HARP back-end doesn't generate sufficient debug info
when it generates native code.

Moving Forward
==============

We're going to focus on improving the debugging experience when using the
C back-end as that is readily achievable. We plan to replace the HARP
back-end with a new back-end using LLVM which will generate far superior
debug information.

Since both the C and LLVM compiler back-ends can generate DWARF debug data,
we'll be able to use traditional debugger implementations like LLDB and
GDB to debug Dylan code. We can improve upon the experience of using
LLDB and GDB though by providing specialized integration scripts that
know more about Dylan objects and can help present them in more intuitive
ways.

My goals here are:

* Have a solution that works well on Mac OS X with the out of the box
  developer tools. I don't want people to have to install a custom
  build of LLDB.
* When developing workarounds for problems in LLDB, also try to work
  with the upstream LLDB developers to improve the situation for the
  future.
* Don't rely on running code within the target process. By not running
  code within the target process, we can also support debugging core
  files. This means that we need to implement things in terms of
  reading memory from the target process.
* Integrate with existing commands as much as possible rather than
  creating new commands to do similar things, but with Dylan data types.
  This means that we don't want a ``dprint`` command to print a Dylan
  object. We want our printing to work natively with ``print``, ``expr``,
  and ``frame variable``.
* Try to do all of the extensions in Python rather than writing C++
  extensions which must be built and loaded separately.
* Be able to provide a good example for people doing something similar
  in the future with other languages.

The LLDB project provides `documentation <http://lldb.llvm.org/varformats.html>`_
for much of what is discussed here. It may be useful to refer to
that documentation. The current version of the code can be found
`here <https://github.com/dylan-lang/opendylan/tree/master/tools/lldb/dylan>`_.
The code below is usually simplified in some form for purposes
of instruction.

Also please note that not all of the issues described here have been
discussed with the upstream LLDB developers yet. I plan to bring
them all up and hope to get some of them resolved.

Summary Strings
===============

Summary strings are a quick and short summary of a value. The first
thing that we wanted to do was to set up some summary providers to
handle things like integers, symbols, strings, and boolean values.

In the C run-time, all Dylan types are represented by a typedef:

.. code-block:: c

    typedef void* D;

Dylan values are tagged, using the bottom 2 bits. Integers have a tag
bit of 1, byte characters have a tag bit of 2, Unicode characters
have a tag bit of 3. All other objects are full objects and have
no tag.

So, the first summary provider that we wanted to do was roughly this:

.. code-block:: python

  def dylan_value_summary(value, internal_dict):
    tag = value.GetValueAsUnsigned() & 3
    if tag == 0:
      return dylan_object_summary(value, internal_dict)
    elif tag == 1:
      return dylan_integer_summary(value, internal_dict)
    elif tag == 2:
      return dylan_byte_character_summary(value, internal_dict)
    elif tag == 3:
      return dylan_unicode_character_summary(value, internal_dict)
    else:
      return 'Invalid tag'

  ...

  def dylan_integer_summary(value, internal_dict):
    return '{<integer>: %s}' % value.GetValueAsUnsigned() >> 2

  def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('type summary add D -F dylan.dylan_value_summary -e -w dylan')
    debugger.HandleCommand('type category enable dylan')

Here, we have defined an initial summary provider, added it to LLDB for
the type ``D`` and enabled the Dylan category of type providers.

Unfortunately, in the version of LLDB shipping with Xcode 5.x, this
causes LLDB to crash.  It ends up that the currently shipping version
of LLDB is unhappy with a type with a name that is a single character.
This is fixed in the beta version of Xcode 6, but as our goals indicate,
we want to have our LLDB integration work with the currently shipping
version of LLDB.

To solve the crash, we modified our C run-time and the C back-end to
use ``dylan_value`` as the typedef name rather than ``D``. We also
took this opportunity to clean up a number of other type names in the
C run-time. We also discovered that two different sorts of values
inhabited the ``D`` values: Dylan objects and raw pointers. We gave
raw-pointers a different name to distinguish them from Dylan objects.

Now, we can see a variable value like this::

    (lldb) frame variable count_
    (dylan_value) count_ = 0x00010001 {<integer>: 16384}

We then added a bunch of other summaries, including for the default
vector class, ``<simple-object-vector>`` (rarely spelled out like that
in code)::

    (lldb) frame variable Urest_
    (dylan_value) Urest_ = 0xbfffc930 {<simple-object-vector>: size: 2}

The next step here is obvious: It would be great to show expanded
values and show the vector's contents.

Synthetic Children
==================

In LLDB, when an object is opaque or the internals aren't user-friendly,
synthetic children can be created via a "synthetic provider".

Immediately, we run into an issue: while synthetic providers are specified
per type, all of our values are the same type (``dylan_value``). We
dealt with this by creating a generic synthetic type and then changing
the class at run-time in the Python script to the appropriate
synthetic provider:

.. code-block:: python

  class SyntheticDylanValue(object):
    def __init__(self, value, internal_dict):
      tag = dylan_tag_bits(value)
      new_class = None
      if tag == OBJECT_TAG:
        class_name = dylan_object_class_name(value)
        new_class = SYNTHETIC_CLASS_TABLE.get(class_name, None)
        if new_class:
          self.__class__ = new_class
      self.value = self.cast_value(value)
      self.update()

    ...

  def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('type synthetic add dylan_value -l dylan.SyntheticDylanValue -w dylan')
    debugger.HandleCommand('type summary   add dylan_value -F dylan.dylan_value_summary -e -w dylan')
    debugger.HandleCommand('type category  enable dylan')

Something to call out in particular here is that we must pass the ``-e`` flag
when adding the summary to indicate that it can be expanded and display
children.

Unfortunately, this doesn't work! We built LLDB from source and debugged it
and found that synthetic children aren't correctly displayed when the
object is a pointer in all cases. We're pursuing this with the upstream
developers to be fixed in a future version. But again, we want this to work
with the current release version of Xcode, so what can we do? In this case,
if ``dylan_value`` were not a pointer but was a simple type instead, this
would work.

Therefore, we undertook a larger change to the run-time: converting
``dylan_value`` to an integer value:

.. code-block:: c

  typedef uintptr_t dylan_value;

This change is not yet complete and hasn't been merged with Open Dylan
master. But I'm using it for now as a local hack to keep making progress
with the LLDB integration.

Now that ``dylan_value`` is an integer, we want to still display it in
hex, so we tell the debugger to do so::

    def __lldb_init_module(debugger, internal_dict):
      debugger.HandleCommand('type format add dylan_value -f hex')

Now, we can see our vector nicely::

    (dylan_value) Urest_ = 0xbfffc930 {<simple-object-vector>: size: 2} {
      [0] = 0x00000009 {<integer>: 2}
      [1] = 0x00545b70 {<symbol>: buffer}
    }

Printing Arbitrary Objects
--------------------------

After that, I thought it would be fun to go crazy, so I wrote a synthetic
type that knows how to walk the internal data structures that describe
classes to print out any arbitrary object with its internal structure.
The details of this are very specific to the Dylan compiler and how it lays
out data and metadata.  The result though is quite handy::

    (lldb) frame variable data_
    (dylan_value) data_ = 0x028b6000 {<buffer>} {
      [buffer-next] = 0x00000001 {<integer>: 0}
      [buffer-end] = 0x00000001 {<integer>: 0}
      [buffer-position] = 0x00000001 {<integer>: 0}
      [buffer-dirty?] = 0x00188374 {<boolean>: False}
      [buffer-start] = 0x00000001 {<integer>: 0}
      [buffer-on-page-bits] = 0x0000fffd {<integer>: 16383}
      [buffer-off-page-bits] = 0xffff0001 {<integer>: 1073725440}
      [buffer-use-count] = 0x00000001 {<integer>: 0}
      [buffer-owning-stream] = 0x00188374 {<boolean>: False}
      [buffer-element] = 0x00010001 {<integer>: 16384}
    }

This is great! Unfortunately, this leads us to our next problem. What happens
if a structure is nested with other structures? What happens if there are
any cyclic references in the structures being printed?

Unfortunately, by default, there are no limits to the depth to which the
printing traverse the structures which makes it very easy to lock up LLDB
by having it traverse to infinity.

The way to limit this is with the ``-D`` or ``--depth`` flag which can be
given to either ``frame variable`` or ``expr``::

    frame variable -D 1
    expr -D 1 -- data_

Unfortunately, this does not work for ``print``::

    (lldb) print -D 1 -- data_
    error: unexpected type name 'D': expected expression
    error: 1 errors parsing expression

This is because ``print`` is an alias for ``expr --``, so it can not pass
any arguments to ``expr``.

There isn't yet have a good solution to this problem, so be sure to always
remember to specify the printing depth with ``frame variable`` or ``expr``.

Other Issues
============

Missing Debug Info
------------------

We have some types that we define in the C run-time for simplifying
data access, and we attempt to use those same types within the
debugger scripts as well.

An example of this is:

.. code-block:: c

  typedef struct _dylan_byte_string {
    dylan_value class;
    dylan_value size;
    char data[_size + 1];
  } dylan_byte_string;

And in the Python code:

.. code-block:: python

  def dylan_byte_string_data(value):
    target = lldb.debugger.GetSelectedTarget()
    byte_string_type = target.FindFirstType('dylan_byte_string').GetPointerType()
    value = value.Cast(byte_string_type)
    size = dylan_integer_value(value.GetChildMemberWithName('size'))
    if size == 0:
      return ''
    data = value.GetChildMemberWithName('data').GetPointeeData(0, size + 1)
    error = lldb.SBError()
    string = data.GetString(error, 0)
    if error.Fail():
      return '<error: %s>' % error.GetCString()
    else:
      return string

Unfortunately, sometimes the convenience types that we define like that
are not present at debug time as they're absent from the debug info.

There's a utility that is very helpful in diagnosing this: ``dwarfdump``.
``dwarfdump``, as the name indicates, dumps the DWARF debug info from
an object file in a form that is human readable (although some knowledge
of DWARF is useful in fully understanding it). You can run it on the object
files from building the C run-time (example here is for ``x86-darwin``)::

    dwarfdump sources/lib/run-time/obj-x86-darwin/c-run-time.o

This file contains no definition for the ``dylan_byte_string`` typedef
or the ``struct _dylan_byte_string``. We can keep looking though in
other files and we'll find it in ``debug-print.o``::

    0x00000642:     TAG_typedef [9]
                     AT_type( {0x0000064e} ( _dylan_byte_string ) )
                     AT_name( "dylan_byte_string" )
                     AT_decl_file( ".../sources/lib/run-time/debug-print.c" )
                     AT_decl_line( 345 )

    0x0000064e:     TAG_structure_type [26] *
                     AT_name( "_dylan_byte_string" )
                     AT_byte_size( 0x0c )
                     AT_decl_file( ".../sources/lib/run-time/run-time.h" )
                     AT_decl_line( 341 )

A typedef needs to be used to be kept alive and represented in the debug
info. In this case, I made sure that a few functions in the C run-time
took arguments of type ``dylan_byte_string`` or returned a value of that
type.

Uninitialized Variables
-----------------------

The Open Dylan compiler's C back-end doesn't initialize local variables
in the generated C until they're actually used. It was written to target
C89 a long time ago, and so it declares all variables used within a
function at the start of that function.

Since variables aren't initialized, sometimes when LLDB goes to display
the values using our summary strings and synthetic providers, things
get a bit confused and may print invalid data or even temporarily hang
LLDB for 5-10 seconds.

We're looking at the impact of initializing all local variables to
a known safe value such as 0 or the %unbound value that Dylan uses
for other uninitialized values.

This is also related to providing better scoping of variable declarations
within the generated C. This is something that we will investigate
in the future.

Wrapping Up
===========

While we've found various issues in providing an improved debugging
experience for Dylan with LLDB, overall, things work fairly well so
far.

There's still work to do though:

* Finish cleaning up changes to Open Dylan and get them merged
  into the master branch.
* Discuss these issues with the upstream LLDB developers and see
  how we can improve things in future releases.
* Implement more summary string methods and more synthetic providers.
* Try to reduce the number of type lookups that we do to improve
  performance. We can cache some data and pass it around internally.
* Handle stack traces better and make them easier to read.
* Add a command line flag to dylan-compiler to have it generate
  code with more debug information available (and less optimization).
