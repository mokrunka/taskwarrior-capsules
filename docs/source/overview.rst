About
=====

Taskwarrior Capsules allows you to easily extend Taskwarrior functionality
by allowing you to add new commands and alter the behavior of existing ones.


Installation
------------

1. Install from Pip::

    pip install taskwarrior-capsules

Please note that you *might* need to run the above command with ``sudo``.

2. Install some capsules (read: plugins) and follow their documentation.

Taskwarrior Capsules itself does not offer any meaningful functionality;
to use Taskwarrior Capsules, you'll want to install some capsules.


Using Capsules
--------------

Taskwarrior Capsules wraps ``task`` using a separate command -- ``tw``,
but all commands that are not recognized
by Taskwarrior Capsules will be passed-through to Taskwarrior itself verbatim.

To make this clearer: to use Taskwarrior Capsules, rather than listing your tasks
with ``task``, use::

    tw

And rather than adding a task with ``task add Homework due:tomorrow priority:h``::

    tw add Homework due:tomorrow priority:h

And for other Taskwarrior commands, just be sure to type ``tw`` instead of ``task``.

.. _finding_plugins:

Finding Capsules
----------------

`Search for some capsules on github <https://github.com/search?utf8=%E2%9C%93&q=taskwarrior+capsule>`_.
