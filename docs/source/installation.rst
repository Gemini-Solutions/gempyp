.. highlight:: shell

============
Installation
============


Stable release
--------------

To install gempyp, run this command in your terminal:

.. code-block:: console

    $ pip install gempyp

This is the preferred method to install gempyp, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for gempyp can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/Gemini-Solutions/gempyp.git

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/Gemini-Solutions/gempyp/tarball/main

Once you have a copy of the source, you can install it. The method of installation will depend on the packaging library being used.

For example, if `setuptools` is being used (a setup.py file is present), install gempyp with:

.. code-block:: console

    $ python setup.py install

If `poetry` is being used (poetry.lock and pyproject.toml files are present), install gempyp with:

.. code-block:: console

    $ poetry install


.. _Github repo: https://github.com/Gemini-Solutions/gempyp
.. _tarball: https://github.com/Gemini-Solutions/gempyp/tarball/master
