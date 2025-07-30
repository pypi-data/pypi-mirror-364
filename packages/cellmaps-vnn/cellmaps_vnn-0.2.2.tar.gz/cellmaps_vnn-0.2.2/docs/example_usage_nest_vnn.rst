Example Usage for NeST VNN
---------------------------

This tool can be used to run the `NeST VNN <https://github.com/idekerlab/nest_vnn>`__ model. The inputs needed for
training the model and performing predictions are described in the `NeST VNN inputs <inputs_nestvnn.html>`_ section
and are located in `examples <https://github.com/idekerlab/cellmaps_vnn/tree/main/examples>`__ directory
in ``cellmaps_vnn`` repository.

Training
~~~~~~~~~

The flow of training NeST VNN

.. image:: images/nest_vnn.png
  :alt: Overview of Cell Maps VNN training flow for NeST VNN

Example run of NeST VNN training using example data provided
in `examples <https://github.com/idekerlab/cellmaps_vnn/tree/main/examples>`__ directory:

.. code-block::

    cellmaps_vnncmd.py train ./outdir_training --inputdir examples --gene2id examples/gene2ind.txt \
        --cell2id examples/cell2ind.txt --training_data examples/training_data.txt --mutations examples/cell2mutation.txt \
        --cn_deletions examples/cell2cndeletion.txt --cn_amplifications examples/cell2cnamplification.txt --epoch 20

Same example, but using configuration file set via `--config_file`

.. code-block::

    cellmaps_vnncmd.py train ./outdir_training --inputdir examples --config_file examples/config.yaml

Prediction
~~~~~~~~~~~

The flow of prediction and interpretation process using NeST VNN

.. image:: images/nestvnn_pred_int.png
  :alt: Overview of Cell Maps VNN prediction flow for NeST VNN

Example run of NeST VNN prediction and interpretation:

.. code-block::

    cellmaps_vnncmd.py predict ./outdir_prediction --inputdir ./outdir_training --gene2id examples/gene2ind.txt \
        --cell2id examples/cell2ind.txt --predict_data examples/test_data.txt --mutations examples/cell2mutation.txt \
        --cn_deletions examples/cell2cndeletion.txt --cn_amplifications examples/cell2cnamplification.txt

Same example, but using configuration file set via `--config_file`

.. code-block::

    cellmaps_vnncmd.py predict ./outdir_prediction --inputdir ./outdir_training --config_file examples/config.yaml

Annotation
~~~~~~~~~~~

The flow of annotation process from  NeST VNN

.. image:: images/nestvnn_annot.png
  :alt: Overview of Cell Maps VNN annotation flow for NeST VNN

.. code-block::

    cellmaps_vnncmd.py annotate ./outdir_annotation --model_predictions ./outdir_prediction

Same example but with upload to NDEx:

If using NeST hierarchy provided in ``examples`` directory in the GitHub repo, you can upload it with its interactome
that is available on ndexbio.org with this uuid: ``0b7b8aee-332f-11ef-9621-005056ae23aa``.

.. code-block::

    cellmaps_vnncmd.py annotate ./outdir_annotation --model_predictions ./outdir_prediction --ndexuser USERNAME --ndexpassword - --parent_network 0b7b8aee-332f-11ef-9621-005056ae23aa --visibility
