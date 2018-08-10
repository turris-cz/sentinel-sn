Non-abstract boxes
==================

**Terminology** for boxes:

* **in-out** box - box receives messages, processes messages and sends (typically modified/enriched) them out.
* **out-only** box - box doesn't receive messages, but generates messages by another mechanism - from redis/DB/etc.
* **in-only** box - box only receives messages and stores them to DB or something elsewhere.


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
