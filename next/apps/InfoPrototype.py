def get_info_object(get_implemented_algs):
    info = {}
    
    info['initExp'] = {'description': 'Dictionary for initialization of experiment.',
                                 'type': 'dict',
                                 'values': {}}
    initExp = info['initExp']['values']
    
    # app_id
    initExp['app_id'] = {'description':'PoolBasedTripletMDS',
                         'type':'string',
                         'values':['PoolBasedTripletMDS']}
    
    # Top level args
    initExp['args'] = {'description':'Arguments for initExp' ,
                       'type':'dict',
                       'values':{}}
    args =  initExp['args']['values']
    args['n'] = {'description':'Number of items.',
                 'type':'num'}
    
    args['participant_to_algorithm_management'] = {'description':'How particpants are routed to algorithms.',
                                                   'type':'string',
                                                   'values':['one-to-one', 'one-to-many']}
    # Alg list declaration
    args['alg_list'] = {'description':'A list of algorithms you plan to use in this experiment.',
                        'type':'list',
                        'values':{'type':'dict','values':{}}}
    
    alg_list = args['alg_list']['values']['values']
    alg_list['alg_label'] = {'description':'A name for this algorithm of your choosing.',
                             'type':'string'}

    alg_list['alg_id'] = {'description':'A supported algorithm type in the system.',
                          'type':'string',
                          'values':get_implemented_algs()}
    
    alg_list['test_alg_label'] = {'description':'Which algorithm to test against.',
                                  'type':'string'}
    
    # algorithm management settings
    args['algorithm_management_settings'] = {'description':'',
                                             'type':'dict',
                                             'values':{}}
    
    algorithm_management_settings = args['algorithm_management_settings']['values']
    algorithm_management_settings['mode'] = {'description':'',
                                             'type':'string',
                                             'values':['fixed_proportions']}
    algorithm_management_settings['params'] = {'description':'',
                                               'type':'dict',
                                               'values':{}}
    params = algorithm_management_settings['params']['values']
    params['proportions'] = {'description':'List of proportions per app type.',
                             'type':'list',
                             'values':{'type':'dict','values':{}}}
    params['proportions']['values']['values']['alg_label'] = {'description':'An alg label, matching one of the ones declared in alg_list.',
                                                    'type':'string'}
    params['proportions']['values']['values']['proportion'] = {'description':'Proportion of queries to give to this algorithm.',
                                                     'type':'num'}
    return info
