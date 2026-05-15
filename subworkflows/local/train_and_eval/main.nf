// TODO nf-core: If in doubt look at other nf-core/subworkflows to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/subworkflows
//               You can also ask for help via your pull request or on the #subworkflows channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A subworkflow SHOULD import at least two modules



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
 

    emit:
    versions  = ch_versions

   
}
