// TODO nf-core: If in doubt look at other nf-core/modules to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/modules/nf-core/
//               You can also ask for help via your pull request or on the #modules channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A module file SHOULD only define input and output files as command-line parameters.
//               All other parameters MUST be provided using the "task.ext" directive, see here:
//               https://www.nextflow.io/docs/latest/process.html#ext
//               where "task.ext" is a string.
//               Any parameters that need to be evaluated in the context of a particular sample
//               e.g. single-end/paired-end data MUST also be defined and evaluated appropriately.
// TODO nf-core: Software that can be piped together SHOULD be added to separate module files
//               unless there is a run-time, storage advantage in implementing in this way
//               e.g. it's ok to have a single module for bwa to output BAM instead of SAM:
//                 bwa mem | samtools view -B -T ref.fasta
// TODO nf-core: Optional inputs are not currently supported by Nextflow. However, using an empty
//               list (`[]`) instead of a file can be used to work around this issue.
import groovy.json.JsonOutput

process SPLITDATA {
    tag { "run_${run_no}_split_${split.type}_seed_${seed}" }
    label 'process_low'
    
    publishDir path: { "${params.outdir}/splitdata/run_${run_no}_split_${split.type}_seed_${seed}" }, mode: params.publish_dir_mode, saveAs: { filename -> filename.equals('versions.yml') ? null : filename }
    // TODO nf-core: See section in main README for further information regarding finding and adding container addresses to the section below.
    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
    'docker://python:3.13':
    'python:3.13' }"

    input:
    tuple val(run_no), val(split), val(seed), path(dataset), path(parsed_config), path(dfeat_dict), path(cfeat_dict) // we convert back split to json to send it to python as python can not understand groovy objects

    output:
    path 'test.pkl',     emit: test
    path 'train.pkl',    emit: train
    path 'train_idx.pkl',emit: train_idx
    path 'val_idx.pkl',  emit: val_idx
    path 'cur_dfeat_dict.pkl', emit: cur_dfeat_dict
    path 'cur_cfeat_dict.pkl', emit: cur_cfeat_dict
    path 'versions.yml', emit: versions


    // TODO nf-core: Where possible, a command MUST be provided to obtain the version number of the software e.g. 1.10
    //               If the software is unable to output a version number on the command-line then it can be manually specified
    //               e.g. https://github.com/nf-core/modules/blob/master/modules/nf-core/homer/annotatepeaks/main.nf
    //               Each software used MUST provide the software name and version number in the YAML version file (versions.yml)
    // TODO nf-core: It MUST be possible to pass additional parameters to the tool as a command-line string via the "task.ext.args" directive
    // TODO nf-core: If the tool supports multi-threading then you MUST provide the appropriate parameter
    //               using the Nextflow "task" variable e.g. "--threads $task.cpus"
    // TODO nf-core: Please replace the example samtools command below with your module's command
    // TODO nf-core: Please indent the command appropriately (4 spaces!!) to help with readability ;)
    script:
    """
    split.py \
        --run_no ${run_no} \
        --split '${JsonOutput.toJson(split)}'\
        --seed ${seed} \
        --dataset_path ${dataset} \
        --parsed_config_path ${parsed_config}\
        --dfeat_dict ${dfeat_dict} \
        --cfeat_dict ${cfeat_dict}



    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
        pandas: \$(python -c "import pandas as pd; print(pd.__version__)")
        numpy: \$(python -c "import numpy as np; print(np.__version__)")
        torch: \$(python -c "import torch; print(torch.__version__)")
    END_VERSIONS

    """

   
}
