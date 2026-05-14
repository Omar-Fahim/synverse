/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { LOADINPUTS } from '../../../modules/local/loadinputs'
include { LOADDATAFRAMES } from '../../../modules/local/loaddataframes'
include { SPLITDATA } from '../../../modules/local/splitdata'
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


    params_ch = LOADINPUTS.out.params_json // is a channel that emits json file paths
    .map { file -> new JsonSlurper().parse(file) } // This will read the Json file and convert it into a Groovy Object

    // Here, the conversion of the params_json to groovy object so that nextflow treat as object not a single string

    combinations_ch = params_ch.flatMap { p -> // for each element in the channel, we will generate multiple outputs

            def runs = (p.start_run as int)..(p.end_run as int) // This will create a range of runs from start_run to end_run

            runs.collectMany { run_no -> // Loop over each run number
                p.splits.collect { split -> // for each run number, loop over all splits 

                    def seed = p.seeds[split.type][run_no]

                    tuple(run_no, split, seed)
                }  
            }
        }

        // A groovy object is just an instance of a class - the same core idea as in java - this is for me 
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

    // PRINT COMBINATIONS_CH
   split_jobs = (
    combinations_ch
        .map { run_no, split, seed ->
            tuple(run_no, split, seed) // As we have converted the paramters json file to a groovy object, split was converted to a groovy map
        } 
        .combine(LOADDATAFRAMES.out.synergy_df)
        .map { run_no, split, seed, synergy_df ->
            tuple(run_no, split, seed, synergy_df)
        }
        .combine(LOADINPUTS.out.loaded_inputs)
        .map { run_no, split, seed, synergy_df, loaded_inputs ->
            tuple(run_no, split, seed, synergy_df, loaded_inputs)
        }
        .combine(LOADDATAFRAMES.out.drug_features)
        .map { run_no, split, seed, synergy_df, loaded_inputs, drug_features ->
            tuple(run_no, split, seed, synergy_df, loaded_inputs, drug_features)
        }
        .combine(LOADDATAFRAMES.out.cell_features)
        .map { run_no, split, seed, synergy_df, loaded_inputs, drug_features, cell_features ->
            tuple(run_no, split, seed, synergy_df, loaded_inputs, drug_features, cell_features)
        }
    )

   
    SPLITDATA(
        split_jobs
    )
    ch_versions = ch_versions.mix(SPLITDATA.out.versions)
    


    emit:
    loaded_inputs  = LOADINPUTS.out.loaded_inputs
    inputs_json    = LOADINPUTS.out.inputs_json
    params_json    = LOADINPUTS.out.params_json
    synergy_df     = LOADDATAFRAMES.out.synergy_df
    drug_features  = LOADDATAFRAMES.out.drug_features
    cell_features  = LOADDATAFRAMES.out.cell_features
    test            = SPLITDATA.out.test
    train           = SPLITDATA.out.train
    train_idx       = SPLITDATA.out.train_idx
    val_idx         = SPLITDATA.out.val_idx
    versions       = ch_versions
}
