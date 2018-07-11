Non-abstract boxes
==================

**Terminology** for boxes:

* **in-out** box - box receives message, processes message and sends (typically modified/enriched) message.
* **out-only** box - box doesn't have sentinel input, but generates messages by another mechanism - from redis/DB/etc.
* **in-only** box - box receives message and doesn't propagate it - it stores it to DB or something else.


SNPipelineBox
-------------

.. autoclass:: sn.msgloop.SNPipelineBox
   :members:

   .. automethod:: __init__()


SNGeneratorBox
--------------

.. autoclass:: sn.msgloop.SNGeneratorBox
   :members:

   .. automethod:: __init__()


SNTerminationBox
----------------
.. autoclass:: sn.msgloop.SNTerminationBox
   :members:

   .. automethod:: __init__()


SNMultipleOutputPipelineBox
---------------------------

.. autoclass:: sn.msgloop.SNMultipleOutputPipelineBox
   :members:
