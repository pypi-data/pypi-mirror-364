Python-GMP
==========

Python extension module providing safe bindings to the GNU GMP.  This module
shouldn't crash the interpreter!

This module can be used as a gmpy2/python-flint replacement to provide
CPython-compatible integer (mpz) type.  It includes few functions (factorial,
gcd and isqrt), compatible with the stdlib's module math.

It requires Python 3.9 or later versions and has been tested with CPython 3.9
through 3.14, for PyPy 3.11 and for GraalPy 24.2.  Free-threading builds of the
CPython are supported.

Releases are available in the Python Package Index (PyPI) at
https://pypi.org/project/python-gmp/


Warning on alloca
-----------------

Most GMP packages enable using alloca() for temporary workspace allocation.
This module can't prevent a crash in case of a stack overflow.  To avoid this,
you should compile the GMP library with '--disable-alloca' configure option to
use rather the heap for all temporary allocations.

Of course, published on the PyPI binary wheels aren't affected by this issue.


Warning on using mp_set_memory_functions()
------------------------------------------

This extension customize memory allocation routines, used by the GMP.  Don't
use together with other GMP bindings, like the gmpy2!


Motivation
----------

The CPython (and most other Python implementations, like PyPy) is optimized to
work with small integers.  Algorithms used here for "big enough" integers
usually aren't best known in the field.  Fortunately, it's possible to use
bindings (for example, the `gmpy2 <https://pypi.org/project/gmpy2/>`_ package)
to the GNU Multiple Precision Arithmetic Library (GMP), which aims to be faster
than any other bignum library for all operand sizes.

But such extension modules usually rely on default GMP's memory allocation
functions and can't recover from errors such as out of memory.  So, it's easy
to crash the Python interpreter during the interactive session.  Following
example with the gmpy2 should work on most Unix systems:

.. code:: pycon

   >>> import gmpy2, resource
   >>> gmpy2.__version__
   '2.2.1'
   >>> resource.setrlimit(resource.RLIMIT_AS, (1024*32*1024, -1))
   >>> z = gmpy2.mpz(29925959575501)
   >>> while True:  # this loop will crash interpter
   ...     z = z*z
   ...
   GNU MP: Cannot allocate memory (size=2949160)
   Aborted

The gmp module handles such errors correctly:

.. code:: pycon

   >>> import gmp, resource
   >>> resource.setrlimit(resource.RLIMIT_AS, (1024*32*1024, -1))
   >>> z = gmp.mpz(29925959575501)
   >>> while True:
   ...     z = z*z
   ...
   Traceback (most recent call last):
     File "<python-input-3>", line 2, in <module>
       z = z*z
           ~^~
   MemoryError
   >>> # interpreter still works, all variables in
   >>> # the current scope are available,
   >>> z.bit_length()  # including pre-failure value of z
   mpz(5867630)
