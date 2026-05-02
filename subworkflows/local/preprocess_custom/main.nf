/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { LOADINPUTS } from '../../../modules/local/loadinputs'
include { LOADDATAFRAMES } from '../../../modules/local/loaddataframes'
import groovy.json.JsonSlurper


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SUBWORKFLOW: PREPROCESS_DATA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
workflow PREPROCESS_DATA {

    take:
    synverse_config

    main:
    ch_versions = Channel.empty()

    LOADINPUTS(
        synverse_config
    )
    ch_versions = ch_versions.mix(LOADINPUTS.out.versions)

    LOADDATAFRAMES(
        LOADINPUTS.out.loaded_inputs
    )
    ch_versions = ch_versions.mix(LOADDATAFRAMES.out.versions)

    // Here I will create all possible combinations of (runs,splits,seeds).


    params_ch = LOADINPUTS.out.params_json
    .map { file -> new JsonSlurper().parse(file) }

    
    combinations_ch = params_ch.flatMap { p ->

            def runs = (p.start_run as int)..(p.end_run as int)

            runs.collectMany { run_no ->
                p.splits.collect { split ->

                    def seed = p.seeds[split.type][run_no]

                    tuple(run_no, split, seed)
                }
            }
        }
    combinations_ch.view { run_no, split, seed ->
    "Run: ${run_no} | Type: ${split.type} | Seed: ${seed}"
}
 

    


    emit:
    loaded_inputs  = LOADINPUTS.out.loaded_inputs
    inputs_json    = LOADINPUTS.out.inputs_json
    params_json    = LOADINPUTS.out.params_json
    synergy_df     = LOADDATAFRAMES.out.synergy_df
    drug_features  = LOADDATAFRAMES.out.drug_features
    cell_features  = LOADDATAFRAMES.out.cell_features
    versions       = ch_versions
}
