/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { softwareVersionsToYAML } from '../subworkflows/nf-core/utils_nfcore_pipeline' //Takes version info and converts it into structured YAML
include { LOAD_INPUTS_CUSTOM     } from '../subworkflows/local/load_inputs_custom'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow SYNVERSE {

    take:
    synverse_config // channel: path to the SynVerse YAML config

    main:

    ch_versions = channel.empty() // Here I intialise an empty channel to collect software versions .

    LOAD_INPUTS_CUSTOM(
        synverse_config
    )
    ch_versions = ch_versions.mix(LOAD_INPUTS_CUSTOM.out.versions) // Combine two channels into one



// Same from Judith's code for collacting and saving software versions
    
    def topic_versions = Channel.topic("versions") // Collects all messages published under topic "versions"
        .distinct() // no duplicate versions
        .branch { entry -> // Each entry becomes either version file or version tuple
            versions_file: entry instanceof Path
            versions_tuple: true
        }

    def topic_versions_string = topic_versions.versions_tuple // Extracts version tuples (process, tool, version).
        .map { process, tool, version ->
            [ process[process.lastIndexOf(':') + 1..-1], "  ${tool}: ${version}" ] // Extract the process name and write in the format tool:version
        }
        .groupTuple(by: 0) // all tools and versions for each process are grouped together
        .map { process, tool_versions ->
            tool_versions.unique().sort()
            "${process}:\n${tool_versions.join('\n')}"
        }  
        /* final Format will be like:
            process1:
              tool1: version
              tool2: version
            process2:
              tool3: version
        */

    softwareVersionsToYAML(ch_versions.mix(topic_versions.versions_file))
        .mix(topic_versions_string)
        .collectFile(
            storeDir: "${params.outdir}/pipeline_info",
            name: 'nf_core_' + 'synverse_software_' + 'versions.yml',
            sort: true,
            newLine: true // Collects all version info into one file
        )
        .set { ch_collated_versions } // saves the output channel for later use

    emit:
    loaded_inputs = LOAD_INPUTS_CUSTOM.out.loaded_inputs // channel: /path/to/loaded_inputs.json
    versions = ch_versions                              // channel: [ path(versions.yml) ]
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
