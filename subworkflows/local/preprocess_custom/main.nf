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
    .map { file -> new JsonSlurper().parse(file) } // This will convert the Json file into a Groovy Object

    
    combinations_ch = params_ch.flatMap { p -> // for each element in the channel, we will generate multiple outputs

            def runs = (p.start_run as int)..(p.end_run as int) // This will create a range of runs from start_run to end_run

            runs.collectMany { run_no -> // Loop over each run number
                p.splits.collect { split -> // for each run number, loop over all splits 

                    def seed = p.seeds[split.type][run_no]

                    tuple(run_no, split, seed)
                }  
            }
        }
                    /* 
                        Run Output 
                        [
                            (1, splitA, seed1A),
                            (1, splitB, seed1B),
                            (2, splitA, seed2A),
                            (2, splitB, seed2B)
                        ]

                    */
                    
                    
                    
                    /*  
                    Split Output
                        [
                        (run_no, splitA, seed),
                        (run_no, splitB, seed)
                        ] */

 

    


    emit:
    loaded_inputs  = LOADINPUTS.out.loaded_inputs
    inputs_json    = LOADINPUTS.out.inputs_json
    params_json    = LOADINPUTS.out.params_json
    synergy_df     = LOADDATAFRAMES.out.synergy_df
    drug_features  = LOADDATAFRAMES.out.drug_features
    cell_features  = LOADDATAFRAMES.out.cell_features
    versions       = ch_versions
}
