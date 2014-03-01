Early Thoughts on Atom
######################

:author: Bruce Mitchener, Jr.
:date: 2014-2-28
:tags: Atom, Editor Support

I got a beta of the `Atom`_ editor soon after its initial release.  The first
thing that I decided to do was to add support for the `Dylan language`_.

As we had a Textmate bundle available, this was an easy process::

  apm init -p ~/.atom/packages/language-dylan \
    -c https://github.com/textmate/dylan.tmbundle

This was the start of a pleasurable experience with Atom. Creating and
publishing a new package was easy and the command line tools were easy
to use (and documented). After just a couple of minutes, I had a package
that provided basic syntax highlighting and code folding for Dylan. It
also worked on any Dylan file that I opened, unlike using our Textmate
bundle in SublimeText which would occasionally hang on some files
(while Textmate was fine). How's that for extensibility? :)

Next up, I decided to improve upon our new Dylan package. So I added
support for auto-indenting and code snippets. This too was straight
forward and easy.

As a comparison, I've also worked in the past with some other Dylan
hackers on a plugin for IntelliJ to provide Dylan language support.
While many things in IntelliJ are relatively easy to do, they all
involve a lot of boilerplate, conflicting or missing bits of documentation,
and a lot of toil overall. That's not to say Atom's documentation is perfect
though. One downside is that I did these extensions by looking at other
language packages as the documentation for some of these things is not
yet written.

While API documentation looks decent so far, documentation on all of the
things that are supported or not when converting a Textmate bundle would
be nice. Do we need to customize smart matching of things like quotes,
parentheses and brackets? (Seemingly not.) How exactly does code folding
work and do we need the same stuff that we had in Textmate / Sublime
Text? (Not sure yet.)

Common Criticisms
=================

I've also noticed a number of common criticisms when the subject of Atom
is brought up.

Privacy
-------

Atom defaults to sending metrics on usage to Google. There's no dialog
at startup to prompt about this and I didn't notice anything in the
initial experience that mentioned this. It can be disabled in the preferences,
but I think that GitHub should consider allowing users to opt in or out
via a dialog on first launch.  It would also be nice to have an idea
of what sort of metrics are being collected.

Another Browser Editor? Why Not Something Native?
-------------------------------------------------

I don't view Atom (or LightTable) as "browser editors".  You don't fire
up your web browser and go to them. They're applications that happen
to re-use the browser environment as a cross-platform rendering and UI
framework. By using the browser, they get to leverage a lot of great tools
and capabilities:

* Chrome's DevTools for profiling, debugging, browsing the DOM.
* Strong layout and rendering capabilities.
* Already cross-platform at the core. (Clearly there's a lot of other code
  that needs to be made portable.)
* A strong and decently performing language implementation.

But as for the concern that it isn't native...  How is emacs any more or
less native than Atom? Large parts of emacs are written in Emacs Lisp while
large parts of Atom are written in JavaScript. The emacs UI doesn't really
look or feel native on many platforms and they carry their own rendering
and layout code around with them. The focus is on providing us with a tool
and a framework for building tools and Atom appears to be on a track to do
a decent job of that.

Is This Just a Sublime Text Clone?
----------------------------------

Visually and at first glance, many aspects of Atom look like they're
cloned from Sublime Text. However, many of the underlying parts clearly
are not:

* Built-in package management and publishing tools that work well.
* The APIs appear to be larger and more flexible.
* More parts of the editor as a whole are plugins and accessible
  to developers.

What Does "Hackable" Mean?
--------------------------

What does it really mean that Atom is a hackable editor? How is Sublime Text
with its API and ability to be scripted in Python not as hackable?

I think the answer here lies in a couple of points:

* Many core parts of the editor are actually plugins and available in
  source form to be hacked upon.
* Having the Developer Tools available makes it easy to poke at something
  in the editor and debug it.

Is It Worth All of the Hype?
----------------------------

Who really cares?  If you find it useful and usable, then great! If not,
there are tons of other choices out there, open or closed.  GitHub has
created a strong offering and we have yet to see how it will evolve, what
sort of community will grow up around it, how it will be used.

What Does the Future Hold?
==========================

As with all things, this is unknowable. It isn't even known yet how much
the editor will cost, how the licensing for the core will work, or even
what platforms it will be available on.  (While there's talk of Linux and
Windows being available soon, some of the keybindings code hints at others
being supported.)

I could easily see features like some of those in LightTable being
provided by Atom.  It could also be used as a client for something like
IPython's Notebook.  It would be interesting to see some of the things
that `David Nolen`_ has been building with `Om, React, and ClojureScript`_
applied to Atom. And that's part of why Atom is exciting: by building
on common technologies and making so much pluggable, we have a platform
with a lot of potential.

We have tools in Dylan that I think would be very exciting to bring
to Atom. What happens if we integrate D3.js and our dependency graphing
code? Can we write a tool that integrates with our control and data flow
graph `debugging code in our compiler`_ that shows how they change as the
optimizer works?

For now, it is a great time to just settle down, see how things develop,
and quietly build great things.

.. _Atom: http://atom.io/
.. _Dylan language: http://opendylan.org/
.. _David Nolen: https://twitter.com/swannodette
.. _Om, React, and ClojureScript: http://sgrove.github.io/omchaya/docs/presentation.html
.. _debugging code in our compiler: https://opendylan.org/documentation/release-notes/2014.1.html#compiler
