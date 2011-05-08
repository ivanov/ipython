"""Tests for the key interactiveshell module, where the main ipython class is defined.
"""
#-----------------------------------------------------------------------------
# Module imports
#-----------------------------------------------------------------------------

# stdlib
import os
import shutil
import tempfile

# third party
import nose.tools as nt

# our own packages
from IPython.testing import decorators as dec
from IPython.testing.globalipapp import get_ipython

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

# Get the public instance of IPython
ip = get_ipython()

#-----------------------------------------------------------------------------
# Test functions
#-----------------------------------------------------------------------------

@dec.parametric
def test_reset():
    """reset must clear most namespaces."""
    # The number of variables in the private user_ns_hidden is not zero, but it
    # should be constant regardless of what we do
    nvars_config_ns = len(ip.user_ns_hidden)

    # Check that reset runs without error
    ip.reset()

    # Once we've reset it (to clear of any junk that might have been there from
    # other tests, we can count how many variables are in the user's namespace
    nvars_user_ns = len(ip.user_ns)

    # Now add a few variables to user_ns, and check that reset clears them
    ip.user_ns['x'] = 1
    ip.user_ns['y'] = 1
    ip.reset()
    
    # Finally, check that all namespaces have only as many variables as we
    # expect to find in them:
    for ns in ip.ns_refs_table:
        if ns is ip.user_ns:
            nvars_expected = nvars_user_ns
        elif ns is ip.user_ns_hidden:
            nvars_expected = nvars_config_ns
        else:
            nvars_expected = 0
            
        yield nt.assert_equals(len(ns), nvars_expected)


# Tests for reporting of exceptions in various modes, handling of SystemExit,
# and %tb functionality.  This is really a mix of testing ultraTB and interactiveshell.

def doctest_tb_plain():
    """
In [18]: xmode plain
Exception reporting mode: Plain

In [19]: run simpleerr.py
Traceback (most recent call last):
  ...line 32, in <module>
    bar(mode)
  ...line 16, in bar
    div0()
  ...line 8, in div0
    x/y
ZeroDivisionError: integer division or modulo by zero
    """


def doctest_tb_context():
    """
In [3]: xmode context
Exception reporting mode: Context

In [4]: run simpleerr.py
---------------------------------------------------------------------------
ZeroDivisionError                         Traceback (most recent call last)
<BLANKLINE>
... in <module>()
     30         mode = 'div'
     31 
---> 32     bar(mode)
<BLANKLINE>
... in bar(mode)
     14     "bar"
     15     if mode=='div':
---> 16         div0()
     17     elif mode=='exit':
     18         try:
<BLANKLINE>
... in div0()
      6     x = 1
      7     y = 0
----> 8     x/y
      9 
     10 def sysexit(stat, mode):
<BLANKLINE>
ZeroDivisionError: integer division or modulo by zero
"""


def doctest_tb_verbose():
    """
In [5]: xmode verbose
Exception reporting mode: Verbose

In [6]: run simpleerr.py
---------------------------------------------------------------------------
ZeroDivisionError                         Traceback (most recent call last)
<BLANKLINE>
... in <module>()
     30         mode = 'div'
     31 
---> 32     bar(mode)
        global bar = <function bar at ...>
        global mode = 'div'
<BLANKLINE>
... in bar(mode='div')
     14     "bar"
     15     if mode=='div':
---> 16         div0()
        global div0 = <function div0 at ...>
     17     elif mode=='exit':
     18         try:
<BLANKLINE>
... in div0()
      6     x = 1
      7     y = 0
----> 8     x/y
        x = 1
        y = 0
      9 
     10 def sysexit(stat, mode):
<BLANKLINE>
ZeroDivisionError: integer division or modulo by zero
      """


def doctest_tb_sysexit():
    """
In [17]: %xmode plain
Exception reporting mode: Plain

In [18]: %run simpleerr.py exit
An exception has occurred, use %tb to see the full traceback.
SystemExit: (1, u'Mode = exit')

In [19]: %run simpleerr.py exit 2
An exception has occurred, use %tb to see the full traceback.
SystemExit: (2, u'Mode = exit')

In [20]: %tb
Traceback (most recent call last):
  File ... in <module>
    bar(mode)
  File ... line 22, in bar
    sysexit(stat, mode)
  File ... line 11, in sysexit
    raise SystemExit(stat, 'Mode = %s' % mode)
SystemExit: (2, u'Mode = exit')

In [21]: %xmode context
Exception reporting mode: Context

In [22]: %tb
---------------------------------------------------------------------------
SystemExit                                Traceback (most recent call last)
<BLANKLINE>
...<module>()
     30         mode = 'div'
     31 
---> 32     bar(mode)
<BLANKLINE>
...bar(mode)
     20         except:
     21             stat = 1
---> 22         sysexit(stat, mode)
     23     else:
     24         raise ValueError('Unknown mode')
<BLANKLINE>
...sysexit(stat, mode)
      9 
     10 def sysexit(stat, mode):
---> 11     raise SystemExit(stat, 'Mode = %s' % mode)
     12 
     13 def bar(mode):
<BLANKLINE>
SystemExit: (2, u'Mode = exit')

In [23]: %xmode verbose
Exception reporting mode: Verbose

In [24]: %tb
---------------------------------------------------------------------------
SystemExit                                Traceback (most recent call last)
<BLANKLINE>
... in <module>()
     30         mode = 'div'
     31 
---> 32     bar(mode)
        global bar = <function bar at ...>
        global mode = u'exit'
<BLANKLINE>
... in bar(mode=u'exit')
     20         except:
     21             stat = 1
---> 22         sysexit(stat, mode)
        global sysexit = <function sysexit at ...>
        stat = 2
        mode = u'exit'
     23     else:
     24         raise ValueError('Unknown mode')
<BLANKLINE>
... in sysexit(stat=2, mode=u'exit')
      9 
     10 def sysexit(stat, mode):
---> 11     raise SystemExit(stat, 'Mode = %s' % mode)
        global SystemExit = undefined
        stat = 2
        mode = u'exit'
     12 
     13 def bar(mode):
<BLANKLINE>
SystemExit: (2, u'Mode = exit')
    """


def test_run_cell():
    import textwrap
    ip.run_cell('a = 10\na+=1')
    ip.run_cell('assert a == 11\nassert 1')

    nt.assert_equals(ip.user_ns['a'], 11)
    complex = textwrap.dedent("""
    if 1:
        print "hello"
        if 1:
            print "world"
        
    if 2:
        print "foo"

    if 3:
        print "bar"

    if 4:
        print "bar"
    
    """)
    # Simply verifies that this kind of input is run
    ip.run_cell(complex)
    

def test_db():
    """Test the internal database used for variable persistence."""
    ip.db['__unittest_'] = 12
    nt.assert_equals(ip.db['__unittest_'], 12)
    del ip.db['__unittest_']
    assert '__unittest_' not in ip.db
