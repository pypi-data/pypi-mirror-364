.. _readme:

.. image:: https://codecov.io/gh/neuropycon/ephypype/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/neuropycon/ephypype

.. image:: https://circleci.com/gh/neuropycon/ephypype.svg?style=svg
    :target: https://circleci.com/gh/neuropycon/ephypype
    
.. image:: https://zenodo.org/badge/92522975.svg
   :target: https://zenodo.org/badge/latestdoi/92522975

.. image:: https://badge.fury.io/py/ephypype.svg
    :target: https://badge.fury.io/py/ephypype

   
README
******

Description
===========

Neuropycon package of functions for electrophysiology analysis, can be used from
graphpype and nipype

Documentation
=============

https://neuropycon.github.io/ephypype

Installation
=============

Requirements
------------

ephypype works with **python3**

The dependencies (mne, nipype) are automatically installed during ephypype installation (see :ref:`ephy_install`). 

We also recommend to install MNE python by following the `installation instructions <http://martinos.org/mne/dev/install_mne_python.html#check-your-installation>`_


.. _ephy_install:

Install ephypype
---------------

To install ephypype, use the following command:

.. code-block:: bash

    $ pip install ephypype
    
or alternatively, you can download from github the last version and install it:

.. code-block:: bash

    $ git clone https://github.com/neuropycon/ephypype.git
    $ cd ephypype
    $ python setup.py develop


.. comment: 
    .. _conda_install:
   
    Install dependencies with conda
    +++++++++++++++++++++++++++++++

    .. code-block:: bash 

        conda install pandas
        conda install matplotlib


Software
--------

Freesurfer
++++++++++
1. Download Freesurfer software:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

2. Follow the Installation instructions

https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall


.. comment:
    MNE
    +++

    1. Download MNE software:

    http://martinos.org/mne/dev/install_mne_c.html
