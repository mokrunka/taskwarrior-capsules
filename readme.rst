Taskwarrior Capsules - The easy plugin framework for Taskwarrior
================================================================

Taskwarrior Capsules allows you to easily extend Taskwarrior functionality
to add new commands and other things.


Installation
------------

1. Install from Pip::

    pip install taskwarrior-capsules

Please note that you *might* need to run the above command with ``sudo``.

2. Install some plugins and follow their documentation.

Taskwarrior Capsules itself does not offer any meaningful functionality;
to use Taskwarrior Capsules, you'll want to install some Capsules
(read: Plugins).
`Search for some plugins on github and follow their
instructions <https://github.com/search?utf8=%E2%9C%93&q=taskwarrior+capsule>`_.

Use
---

Taskwarrior Capsules wraps ``task`` using a separate command -- ``tw``,
but all commands that are not recognized
by Taskwarrior Capsules will be passed-through to Taskwarrior itself verbatim.

To make this clearer: to use Taskwarrior Capsules, rather than listing your tasks
with ``task``, use::

    tw

And rather than adding a task with ``task add Homework due:tomorrow priority:h``::

    tw add Homework due:tomorrow priority:h

And for other Taskwarrior commands, just be sure to type ``tw`` instead of ``task``.

Go
`search for some plugins <https://github.com/search?utf8=%E2%9C%93&q=taskwarrior+capsule>`_
and get started!

