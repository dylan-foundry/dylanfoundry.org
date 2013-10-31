A New IDE Approach
##################

:author: Bruce Mitchener, Jr.
:date: 2013-10-31

.. image:: /static/images/DeftIDEA_smaller.png
   :align: right
   :target: /static/images/DeftIDEA.png

We've previously written about the state of the Open Dylan IDE. In short,
it is currently only available on Windows and looks like an application
from the 1990s (because it is).  Simply getting it running on Mac OS X
or Linux would be a lot of work (an attempt was made to port the underlying
GUI framework), not counting modernization and adding new features.

In late September, we had a seemingly crazy idea: What if we built a new
IDE on an existing IDE framework. We've previously worked with Eclipse and
didn't want to do that again. IntelliJ, however, officially supports IDEs
for Java, Python, Ruby, PHP, and Objective C. Unofficially, it has support
for a host of other languages including Erlang, Lua, Scala, HaXe and many
others.

So, we wondered, what would it take to get some basics running for Dylan?
In the end, the answer was that within 10 hours of first looking at IntelliJ
plug-in authoring, we had it recognizing file types, doing some basic
parsing for LID files and some other minor things.

This led to the creation of DeftIDEA, a new Dylan Environment For Tools
running inside of IntelliJ IDEA.

Why did we pick IntelliJ over other alternatives such as Sublime Text or
emacs (with `DIME`_) or any of the many other options, some of which
already had some degree of Dylan support?

IntelliJ provides a lot of infrastructure for building a modern IDE,
including tools for building parsers, custom views of files, templating,
completion, refactoring, version control integration and many modern
features. It is also cross-platform and readily usable on Windows, Linux
and Mac OS X.

Using IntelliJ, we've been able to create a new Dylan parser that is fairly
complete, apart from macro-expansion. This parser lets us use a lot of
facilities from within IntelliJ with little effort. So far, we have syntax
highlighting, code annotations, custom warnings and errors, code folding,
structural views of files, code navigation (like go to a definition, go to
class) and live templating. Features like code formatting, auto-indenting,
reformatting are coming.

We don't call into the existing Dylan compiler to provide this functionality
as that wouldn't get us a lot of the advantages of using the IntelliJ
frameworks and infrastructure. Our new parser also allows for feedback as
you type rather than waiting on a compilation cycle. We've already had an
instance where the Open Dylan compiler was returning a vague error message
for a syntax error in a library definition, but opening the file within
DeftIDEA made it immediately obvious what was wrong.

We're looking forward to adding more features to DeftIDEA, like invoking
the Open Dylan compiler and processing errors and warnings, displaying
method dispatch optimization feedback, and integrating with Testworks.

There are also many easy opportunities to help improve the plug-in such
as improving syntax highlighting, improving the structural views,
implementing reference resolution (uses, implements, etc), improving
auto-indentation and code formatting, providing additional live templates
and fixing bugs in general.

.. _DIME: http://opendylan.org/news/2011/12/12/dswank.html
