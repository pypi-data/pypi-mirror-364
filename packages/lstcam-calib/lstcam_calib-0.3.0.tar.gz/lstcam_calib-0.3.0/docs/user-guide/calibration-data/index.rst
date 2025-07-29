
.. _calibration-data:

Calibration Data
================

Calibration data are written in files inside a specifically designed  data-tree.

In order to bookkeep all files, their quality and their usage, specific meta-data
are produced for each file and stored in a database if the option ``--db``
of the onsite tools is set to ``True``

.. note::
    A present, the option ``--db`` is set to ``False`` by default, hence the code behaves as
    the (obsolete) calibration code in cta-lschain this will change as soon as the database module
    will be validated.

In the following sections we describe the data-tree,  the database and the data models.

    .. toctree::
        :maxdepth: 1
        :titlesonly:

        data-tree
        database
        data-models
