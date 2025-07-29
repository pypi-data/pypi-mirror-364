==========================
pdfposter
==========================

-------------------------------------------------------------
Scale and tile PDF images/pages to print on multiple pages.
-------------------------------------------------------------

:Author:    Hartmut Goebel <h.goebel@crazy-compilers.com>
:Version:   Version 0.9.post1
:Copyright: 2008-2025 by Hartmut Goebel
:License:   GNU Public License v3 or later (GPL-3.0-or-later)
:Homepage:  https://pdfposter.readthedocs.io/

``Pdfposter`` can be used to create a large poster by building it from
multiple pages and/or printing it on large media. It expects as input a
PDF file, normally printing on a single page. The output is again a
PDF file, maybe containing multiple pages together building the
poster.
The input page will be scaled to obtain the desired size.

This is much like ``poster`` does for Postscript files, but working
with PDF. Since sometimes poster does not like your files converted
from PDF. :-) Indeed ``pdfposter`` was inspired by ``poster``.

For more information please refer to the manpage or visit
the `project homepage <https://pdfposter.readthedocs.io/>`_.


Requirements and Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Pdfposter`` requires

* `Python`__  (3.7—3.13, but newer versions should work, too),
* `setuptools`__ or `pip`__ for installation, and
* `pypdf`__ (3.0 or newer, tested with 5.8.0)

__ https://www.python.org/download/
__ https://pypi.org/project/setuptools
__ https://pypi.org/project/pip
__ https://pypi.org/project/pypdf


.. Emacs config:
 Local Variables:
 mode: rst
 End:
