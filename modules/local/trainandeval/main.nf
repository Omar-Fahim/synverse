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

process TRAINANDEVAL {
    tag "run_${run_no}_split_${split_type}_${drug_feat}_${cell_feat}"
    label 'process_low'
    publishDir path: "${params.outdir}/trainandeval", mode: params.publish_dir_mode, saveAs: { filename -> filename.equals('versions.yml') ? null : filename }
    // TODO nf-core: See section in main README for further information regarding finding and adding container addresses to the section below.
    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'docker://python:3.13':
        'python:3.13' }"

    input:
    tuple val(run_no), val(split_type), val(test_frac), val(val_frac), val(seed), path(test_file), path(train_file), path(train_idx_file), path(val_idx_file), path(dfeat_file), path(cfeat_file), val(drug_feat), val(cell_feat), path(params_json), path(cell_line_2_idx), path(drug_2_idx)

    output:
    path "versions.yml", emit: versions
    path "results/**", emit: results
    

    

    script:
    """
    train_and_eval.py \\
        --run_no ${run_no} \\
        --split_type ${split_type} \\
        --seed ${seed} \\
        --test_file ${test_file} \\
        --train_file ${train_file} \\
        --train_idx_file ${train_idx_file} \\
        --val_idx_file ${val_idx_file} \\
        --dfeat_file ${dfeat_file} \\
        --cfeat_file ${cfeat_file} \\
        --drug_feat '${drug_feat}' \\
        --cell_feat '${cell_feat}' \\
        --params_json '${params_json}' \\
        --cell_line_2_idx '${cell_line_2_idx}' \\
        --drug_2_idx '${drug_2_idx}' \\
        --test_frac ${test_frac} \\
        --val_frac ${val_frac} \\
        --out_dir results


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
        torch: \$(python -c "import torch; print(torch.__version__)")
    END_VERSIONS
    """


}
