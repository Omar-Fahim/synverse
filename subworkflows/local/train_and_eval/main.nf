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
    

    main:
    // TODO nf-core: substitute modules here for the modules of your subworkflow
    ch_versions = Channel.empty()
    EXPANDFEATUREDRUGCOMBINATIONSFILE(
    drug_cell_features_combinations
    )

    feature_combination_ch =
    EXPANDFEATUREDRUGCOMBINATIONSFILE.out.combinations
        .splitText() // one line contains one drug feature and one cell feature, splitText() make nextflow see each line as a seperate channel item
        .map { line ->

            def (drug_feat, cell_feat) = line.trim().split('\t')

            tuple(drug_feat, cell_feat)
        }

   training_jobs =
    split_bundle
        .combine(feature_combination_ch)
        .combine(params_json)
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
            params_json
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

                dfeat_file,
                cfeat_file,

                drug_feat, // not the drug_features.pkl . this one is from combinations.
                cell_feat,
                params_json
            )
        }

    TRAINANDEVAL(
        training_jobs
    )
    ch_versions = ch_versions.mix(TRAINANDEVAL.out.versions)
    emit:
    versions  = ch_versions

   
}
