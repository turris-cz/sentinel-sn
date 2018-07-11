SNBox class
===========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. autoclass:: sn.msgloop.SNBox


There are 4 types of programmes interested in ``SNBox`` class:

#. Programmer making changes in ``SNBox`` itself
#. Programmer of non-abstract box
#. Programmer of final-box for particular usage
#. Final code user

SNBox programmer
----------------

Please, refer source code directly.

Non-abstract box programmer
---------------------------

.. automethod:: sn.msgloop.SNBox.__init__

   **Do not forget** to call ancesor of the method if you need to overload it.

.. automethod:: sn.msgloop.SNBox.check_configuration
.. automethod:: sn.msgloop.SNBox.get_processed_message
.. automethod:: sn.msgloop.SNBox.process_result
.. automethod:: sn.msgloop.SNBox.teardown_box

   **Do not forget** to call ancesor of the method if you need to overload it.

Final-box programmer
--------------------

.. automethod:: sn.msgloop.SNBox.setup
.. automethod:: sn.msgloop.SNBox.teardown
.. automethod:: sn.msgloop.SNBox.before_first_request
.. automethod:: sn.msgloop.SNBox.process

Final code user
---------------

.. automethod:: sn.msgloop.SNBox.run
