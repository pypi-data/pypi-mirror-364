.. _spkg_filelock:

filelock: Platform independent file lock
==================================================

Description
-----------

Platform independent file lock

License
-------

Public Domain <http://unlicense.org>

Upstream Contact
----------------

https://pypi.org/project/filelock/


Type
----

standard


Dependencies
------------

- $(PYTHON)
- :ref:`spkg_pip`

Version Information
-------------------

package-version.txt::

    3.14.0

version_requirements.txt::

    filelock


Equivalent System Packages
--------------------------

.. tab:: conda-forge

   .. CODE-BLOCK:: bash

       $ conda install filelock 


.. tab:: Void Linux

   .. CODE-BLOCK:: bash

       $ sudo xbps-install python3-filelock 



If the system package is installed, ``./configure`` will check if it can be used.

