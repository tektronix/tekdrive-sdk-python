Usage Overview
==============

Prerequisites
~~~~~~~~~~~~~
Authentication with the TekDrive API is handled through the use of access keys. You will need an access key with the appropriate claims for your use case.

You can learn more about access keys and their claims `here <https://docs.dev-drive.tekcloud.com/#api-authentication-access-key>`_.

:class:`.TekDrive` Instantiation 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All interaction with the TekDrive API is done through an instance of the :class:`.TekDrive` class.

.. code-block:: python

    from tekdrive import TekDrive

    td = TekDrive(
        access_key="MY_ACCESS_KEY",
    )

This provides a client (``td``) which has several methods and helpers, many of which return TekDrive models offering additional methods, to make it easy to interact with the TekDrive API.

For example, creating a file is as simple as:

.. code-block:: python

    td.file.create("/path/to/file.txt", name="My New File")

See the :ref:`models` section for more.
