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


    params_ch = LOADINPUTS.out.params_json // is a channel that emits the file path for the params.json file
    .map { file -> new JsonSlurper().parse(file) } // This will read the Json file and convert it into a Groovy Object

    // Here, the conversion of the params_json to groovy object so that nextflow treat as object not a single string
    // A groovy object is just an instance of a class - the same core idea as in java - comment for me 
    combinations_ch = params_ch.flatMap { p -> // This will take the groovy object and create a new channel that emits all combinations of (runs,splits,seeds)

            def runs = (p.start_run as int)..(p.end_run as int) // This will create a range of runs from start_run to end_run

            runs.collectMany { run_no -> // Loop over each run number
                p.splits.collect { split -> // for each run number, loop over all splits 

                    def seed = p.seeds[split.type][run_no]

                    tuple(run_no, split, seed)
                }  
            }
        }

       

    // Here, I will create a new channel that emits all combinations of (run_no, split_type, test_frac, val_frac, seed, synergy_df, loaded_inputs, drug_features, cell_features).
split_jobs = combinations_ch

    .map { run_no, split, seed ->

        tuple(
            run_no,
            split.type,
            split.test_frac,
            split.val_frac,
            seed
        )
    }

    .combine(LOADDATAFRAMES.out.synergy_df)
    .combine(LOADINPUTS.out.loaded_inputs)
    .combine(LOADDATAFRAMES.out.drug_features)
    .combine(LOADDATAFRAMES.out.cell_features)

    .map {
        run_no,
        split_type,
        test_frac,
        val_frac,
        seed,
        synergy_df,
        loaded_inputs,
        drug_features,
        cell_features ->

        tuple(
            run_no,
            split_type,
            test_frac,
            val_frac,
            seed,
            synergy_df,
            loaded_inputs,
            drug_features, // the picke file that contains dfeat_dict
            cell_features
        )
    }

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
    drug_cell_features_combinations = LOADDATAFRAMES.out.drug_cell_feat_combs
    split_bundle   = SPLITDATA.out.split_bundle // this contains dfeat_dict and cfeat_dict after splitting.
    cell_line_2_idx = LOADDATAFRAMES.out.cell_line_2_idx
    drug_2_idx = LOADDATAFRAMES.out.drug_2_idx
    versions       = ch_versions





}
