// TODO nf-core: If in doubt look at other nf-core/subworkflows to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/subworkflows
//               You can also ask for help via your pull request or on the #subworkflows channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A subworkflow SHOULD import at least two modules

include { EXPANDFEATUREDRUGCOMBINATIONSFILE } from '../../../modules/local/expandfeaturedrugcombinationsfile'
include{ TRAINANDEVAL } from '../../../modules/local/trainandeval'
workflow TRAIN_AND_EVAL {

    take:
    loaded_inputs
    params_json
    synergy_df
    drug_features
    cell_features
    drug_cell_features_combinations
    split_bundle
    cell_line_2_idx
    drug_2_idx
    

    main:
    // TODO nf-core: substitute modules here for the modules of your subworkflow
    ch_versions = Channel.empty()
    
    // This module will take the drug_cell_features_combinations.pkl file and expand it to a channel that prints all possible combinations of drug and cell features. Each line will contain one drug feature and one cell feature, separated by a tab character.
    EXPANDFEATUREDRUGCOMBINATIONSFILE(
    drug_cell_features_combinations
    )
    // a channel that emits all possible combinations of drug and cell features
    feature_combination_ch =
    EXPANDFEATUREDRUGCOMBINATIONSFILE.out.combinations
        .splitText() // one line contains one drug feature and one cell feature, splitText() make nextflow see each line as a seperate channel item
        .map { line -> // loop over each line in the channel

            def (drug_feat, cell_feat) = line.trim().split('\t') // split the line into drug feature and cell feature, separated by a tab character

            tuple(drug_feat, cell_feat)
        }


// Create one TRAINANDEVAL job for each run, split, and drug/cell feature combination.
// Each emitted tuple includes split metadata, train/test/validation files, selected
// feature files, model parameters, and cell-line/drug index mappings.
   training_jobs =
    split_bundle
        .combine(feature_combination_ch)
        .combine(params_json)
        .combine(cell_line_2_idx)
        .combine(drug_2_idx)
        .map {

            run_no,
            split_type,
            test_frac,
            val_frac,
            seed,

            test_file,
            train_file,
            train_idx_file,
            val_idx_file,

            dfeat_file,
            cfeat_file,

            drug_feat,
            cell_feat,
            params_json,
            cell_line_2_idx,
            drug_2_idx
             ->

            tuple(
                run_no,

                split_type,
                test_frac,
                val_frac,

                seed,

                test_file,
                train_file,
                train_idx_file,
                val_idx_file,

                dfeat_file, // the drug feature dictionary pickle file that contains the drug features
                cfeat_file,

                drug_feat, // the drug feature name that will be used to select the drug feature from the drug feature dictionary
                cell_feat,
                params_json,
                cell_line_2_idx,
                drug_2_idx
            )
        }

    TRAINANDEVAL(
        training_jobs
    )
    ch_versions = ch_versions.mix(TRAINANDEVAL.out.versions)
    emit:
    versions  = ch_versions

   
}
