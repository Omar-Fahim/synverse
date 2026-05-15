// TODO nf-core: If in doubt look at other nf-core/subworkflows to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/subworkflows
//               You can also ask for help via your pull request or on the #subworkflows channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A subworkflow SHOULD import at least two modules

include { EXPANDFEATUREDRUGCOMBINATIONSFILE } from '../../../modules/local/expandfeaturedrugcombinationsfile'
workflow TRAIN_AND_EVAL {

    take:
    loaded_inputs
    inputs_json
    params_json
    synergy_df
    drug_features
    cell_features
    drug_cell_features_combinations
    test
    train
    train_idx
    val_idx
    curr_dfeat_dict
    curr_cfeat_dict
    

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
    train
        .combine(test)
        .combine(train_idx)
        .combine(val_idx)
        .combine(curr_dfeat_dict)
        .combine(curr_cfeat_dict)
        .combine(feature_combination_ch)

    training_jobs.view()

    emit:
    versions  = ch_versions

   
}
