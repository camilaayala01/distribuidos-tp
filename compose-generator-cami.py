import os
from typing import Any
import yaml, sys
from dotenv import load_dotenv
from aggregator.common.aggregatorTypes import AggregatorTypes
from filterer.common.filtererTypes import FiltererType
from grouper.common.grouperTypes import GrouperType
from joiner.common.joinerTypes import JoinerType
from sendingStrategy.common.shardingAtribute import ShardingAttribute
from sorter.common.sorterTypes import SorterType
load_dotenv('compose.env')

def add_to_list(list, new_list):
    list.extend(new_list)
    return list

def add_client(compose: dict[str, Any]):
    return add_client_with_id(compose,'')

def add_client_with_id(compose: dict[str, Any], client_id: int,):
    compose['services'][f'client-{client_id}']= {
        'build': zmq_node_build('./client'),
        'environment':[
            'PYTHONUNBUFFERED=1',
            'MAX_DATA_BYTES=51200',
            'REVIEWS_STORAGE_FILEPATH=./datasets/reviews-reducido.csv',
            'GAMES_STORAGE_FILEPATH=./datasets/games-reducido.csv',
            'AMOUNT_OF_EXECUTIONS=1'
        ],
        'volumes':[
            './entryParsing:/entryParsing',
            '~/.kaggle/distribuidos:/datasets',
            f'./client-{client_id}/responses:/responses',
        ],
        'networks': default_network(),
        'depends_on':
        ['border-node']
    }
    return compose

def add_all_clients(compose: dict[str, Any], client_number: int):
    for i in range(1, client_number + 1):
        compose = add_client_with_id(compose, i)
    return compose

def add_network(compose: dict[str, Any]):
    compose['networks']['sa_net'] = {
        'ipam': {
            'driver': 'default',
            'config': [
                {'subnet': '172.25.125.0/24'}
            ]
        }
    }
    return compose

def default_volumes():
    return [
            './internalCommunication:/internalCommunication',
            './entryParsing:/entryParsing',
            './sendingStrategy:/sendingStrategy'
    ]

def stateful_volumes(type, name):
    return f'./{type}/{name}:/state'

def default_network():
    return [
            'sa_net'
    ]

def default_env_file():
    return [
            '.env'
    ]

def default_environment(queue)-> list[str]:
    return ([
            'PYTHONUNBUFFERED=1',
            f'LISTENING_QUEUE={queue}',
    ])

def rabbit_node_build(context):
    return {
        'context': context,
        'dockerfile': '../rabbitUser.Dockerfile'
    }

def zmq_node_build(context)-> dict[str, Any]:
    return ({
        'context': context,
        'dockerfile': '../zmqUser.Dockerfile'
    })

def component_nodes_environment(next_nodes, header_type, entry_type):
    return ([
        f'NEXT_NODES={next_nodes}',
        f'HEADER_TYPE={header_type}',
        f'ENTRY_TYPE={entry_type}',
    ])

def joiner_nodes_environment(next_nodes, review_entry_type, game_entry_type):
    return ([
        f'NEXT_NODES={next_nodes}',
        f'HEADER_TYPE=HeaderWithTable',
        f'GAMES_ENTRY_TYPE={game_entry_type}',
        f'REVIEWS_ENTRY_TYPE={review_entry_type}',
    ])
    
def default_config(compose: dict[str, Any], entrypoint: str, container_name: str, queue: str, next_nodes: str, header_type: str, entry_type: str, extra_envs: list[str]):
    compose['services'][container_name] ={
        'build': rabbit_node_build(entrypoint),
        'environment': add_to_list(default_environment(queue), add_to_list(component_nodes_environment(next_nodes, header_type, entry_type), extra_envs)),
        'env_file': default_env_file(),
        'volumes': default_volumes(),
        'networks': default_network()
    }
    return compose
    
def default_config_with_tracker(compose: dict[str, Any], entrypoint: str, container_name: str, queue: str, next_nodes: str, header_type: str, entry_type: str, extra_envs: list[str], type: str):
    compose['services'][container_name] = {
        'build': rabbit_node_build(entrypoint),
        'environment': add_to_list(default_environment(queue), add_to_list(component_nodes_environment(next_nodes, header_type, entry_type), extra_envs)),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), ['./packetTracker:/packetTracker', stateful_volumes(type, container_name)]),
        'networks': default_network()
    }
    return compose

def add_initializer(compose: dict[str, Any], id):
    container_name = f'initializer-{id}' 
    compose['services'][container_name] ={
        'build': rabbit_node_build('./initializer'),
        'environment': add_to_list(default_environment(os.getenv('INIT')),
                                   ['HEADER_TYPE=HeaderWithTable',
                                    'GAMES_ENTRY_TYPE=ReducedGameEntry',
                                    f'GAMES_NEXT_NODES={os.getenv("FILT_INDIE")}',
                                    'GAMES_NEXT_ENTRIES=EntryAppIDNameGenresReleaseDateAvgPlaytime',
                                    'GAMES_NEXT_HEADERS=',
                                    'REVIEWS_ENTRY_TYPE=ReviewEntry',
                                    f'REVIEWS_NEXT_NODES={os.getenv("GROUP_INDIE")}',
                                    'REVIEWS_NEXT_ENTRIES=EntryAppID']),
        'env_file': default_env_file(),
        'volumes': default_volumes(),
        'networks': default_network()
    }
    return compose, container_name

def add_initializers(compose: dict[str, Any]):
    count = int(os.getenv('INIT_COUNT'))
    containers = []
    for i in range(0, count):
        compose, new_container = add_initializer(compose, i)
        containers.append(new_container)
    return compose, containers

def add_grouper(compose: dict[str, Any], params):
    name, type, queue, next_nodes, header_type, entry_type = params
    container_name = f'grouper-{name}'
    compose = default_config(compose, entrypoint='./grouper', container_name=container_name, queue=queue, next_nodes=next_nodes, header_type=header_type, entry_type=entry_type, extra_envs= [f'GROUPER_TYPE={type}'])
    return compose, container_name


def add_sorter(compose: dict[str, Any], name, type, queue, next_nodes, header_type, entry_type, node_id, node_count, top):
    container_name = f'sorter-{name}'
    compose = default_config_with_tracker(compose, entrypoint='./sorter', container_name=container_name, queue= queue, next_nodes=next_nodes, header_type=header_type, entry_type=entry_type, extra_envs=[f'SORTER_TYPE={type}', f'NODE_ID={node_id}', f'TOP_AMOUNT={top}', f'NODE_COUNT={node_count}'], type='sorter')
    return compose, container_name

def add_sorter_consolidator_top(compose: dict[str, Any], name, type, queue, next_nodes,header_type, entry_type, prior_node_count, top, query_number):
    container_name = f'sorter-consolidator-{name}'
    compose = default_config_with_tracker(compose, entrypoint='./sorter', container_name=container_name, queue=queue, next_nodes=next_nodes, header_type=header_type, entry_type=entry_type, extra_envs=[f'SORTER_TYPE={type}', f'PRIOR_NODE_COUNT={prior_node_count}', f'TOP_AMOUNT={top}', f'QUERY_NUMBER={query_number}'], type='sorter')
    return compose, [container_name]

def add_sorter_consolidator_percentile(compose: dict[str, Any], name, type, queue, next_nodes, header_type, entry_type, prior_node_count, percentile, query_number):
    compose = default_config_with_tracker(compose, entrypoint='./sorter', container_name=name, queue=queue, next_nodes=next_nodes, header_type=header_type, entry_type=entry_type, extra_envs=[f'SORTER_TYPE={type}', f'PRIOR_NODE_COUNT={prior_node_count}', f'PERCENTILE={percentile}', f'QUERY_NUMBER={query_number}'], type='sorter')
    return compose, [name]

def add_joiner(compose: dict[str, Any], params):
    name, type, queue, next_nodes, review_entry_type, game_entry_type, node_id = params
    container_name = f'joiner-{name}'
    compose['services'][container_name] = {
        'build': rabbit_node_build('./joiner'),
        'environment': add_to_list(default_environment(queue), add_to_list(joiner_nodes_environment(next_nodes, review_entry_type, game_entry_type), [f'JOINER_TYPE={type}', f'NODE_ID={node_id}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), ['./packetTracker:/packetTracker', stateful_volumes('joiner', container_name)]),
        'networks': default_network()
    }
    return compose, container_name
    
def add_filterer(compose: dict[str, Any], params):
    if len(params) == 7:
        name, type, queue, next_nodes, next_entries, header_type, entry_type = params
        container_name = f'filterer-{name}'
        compose = default_config(compose, entrypoint='./filterer', container_name=container_name, queue=queue, next_nodes=next_nodes, header_type=header_type, entry_type=entry_type, extra_envs=[f'FILTERER_TYPE={type}', f'NEXT_ENTRIES={next_entries}'])
    if len(params) == 8:
        name, type, queue, next_nodes, next_entries, next_headers, header_type, entry_type = params
        container_name = f'filterer-{name}'
        compose = default_config(compose, entrypoint='./filterer', container_name=container_name, queue=queue, next_nodes=next_nodes, header_type=header_type, entry_type=entry_type, extra_envs=[f'FILTERER_TYPE={type}', f'NEXT_ENTRIES={next_entries}', f'NEXT_HEADERS={next_headers}'])
    return compose, container_name

def add_aggregator_os(compose: dict[str, Any]): 
    name = 'aggregator-os'
    compose = default_config_with_tracker(compose, entrypoint='./aggregator', 
                                          container_name=name, 
                                          queue=f"{os.getenv('AGGR_OS')}", 
                                          next_nodes=f"{os.getenv('DISP')}", 
                                          header_type ='Header', 
                                          entry_type='EntryOSCount', 
                                          extra_envs=[f"AGGREGATOR_TYPE={AggregatorTypes.OS.value}", "QUERY_NUMBER=1"], type='aggregator')
    return compose, [name]

def add_aggregator_english(compose: dict[str, Any]):
    container_name = 'aggregator-english'
    compose = default_config_with_tracker(compose, entrypoint='./aggregator', 
                                          container_name=container_name, 
                                          queue=os.getenv('AGGR_ENG'), 
                                          next_nodes=os.getenv('DISP'), 
                                          header_type = 'HeaderWithSender', 
                                          entry_type = 'EntryAppIDNameReviewCount', 
                                          extra_envs=[f"AGGREGATOR_TYPE={AggregatorTypes.ENGLISH.value}", f'PRIOR_NODE_COUNT={os.getenv("JOIN_ACT_COUNT")}',"REQUIRED_REVIEWS=5000", "QUERY_NUMBER=4"], type='aggregator')
    return compose, [container_name]

def add_aggregator_indie(compose: dict[str, Any]):
    container_name = 'aggregator-indie'
    compose = default_config_with_tracker(compose, entrypoint='./aggregator', 
                                          container_name=container_name, 
                                          queue= f"{os.getenv('AGGR_INDIE')}", 
                                          next_nodes=f"{os.getenv('SORT_INDIE')},{os.getenv('SORT_INDIE_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}", 
                                          header_type='HeaderWithSender', 
                                          entry_type='EntryNameReviewCount', 
                                          extra_envs=[f"AGGREGATOR_TYPE={AggregatorTypes.INDIE.value}", f'PRIOR_NODE_COUNT={os.getenv("JOIN_INDIE_COUNT")}'], type='aggregator')
    return compose, [container_name]

def add_border_node(compose: dict[str, Any], cluster_nodes):
    compose['services']['border-node']= {
        'build': {
            'context': './borderNode',
            'dockerfile': '../zmqUser.Dockerfile'
        },
        'environment':[
            'PYTHONUNBUFFERED=1'
        ],
        'env_file': default_env_file(),
        'volumes':[
        './internalCommunication:/internalCommunication',
        './entryParsing:/entryParsing'
        ],
        'networks': default_network(),
        'depends_on': cluster_nodes
    }
    return compose

def add_multiple(compose: dict[str, Any], count, generator_func, params):
    name = params[0]

    containers = []
    for i in range(0, count):
        params[0] = f'{name}-{i}'
        compose, new_container = generator_func(compose, params)
        containers.append(new_container)
    return compose, containers

def add_one(compose, generator_func, params):
    compose, new_container = generator_func(compose, params)
    return compose, [new_container]

def add_depending_count(compose, count, generator_func, params):
    if count == 1:
        return add_one(compose, generator_func, params)
    else:
        return add_multiple(compose, count, generator_func, params)
    
def add_filterers_indie(compose: dict[str, Any]):
    # name, type, queue, next_nodes, next_entries, next_headers, header_type, entry_type
    params = ['indie', FiltererType.INDIE.value, os.getenv('FILT_INDIE'),
               f"{os.getenv('FILT_DEC')};{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}",
               'EntryNameDateAvgPlaytime;EntryAppIDName','Header;' ,'HeaderWithTable', 'EntryAppIDNameGenresReleaseDateAvgPlaytime'] 
    return add_depending_count(compose, int(os.getenv('FILT_INDIE_COUNT')), generator_func=add_filterer, params=params)
    
def add_filterers_date(compose: dict[str, Any]):
    # name, type, queue, next_nodes, next_entries, header_type, entry_type
    params = ['date',FiltererType.DECADE.value, f"{os.getenv('FILT_DEC')}",
               f"{os.getenv('SORT_AVG_PT')},{os.getenv('SORT_AVG_PT_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}",
               'EntryNameAvgPlaytime', 'Header', 'EntryNameDateAvgPlaytime']
    return add_depending_count(compose, int(os.getenv('FILT_DEC_COUNT')), generator_func=add_filterer, params=params)
   
def add_filterers_action(compose: dict[str, Any]):
    # name, type, queue, next_nodes, next_entries, header_type, entry_type
    params = ['action', FiltererType.ACTION.value, f"{os.getenv('FILT_ACT')}",
              f"{os.getenv('JOIN_ACT')},{os.getenv('JOIN_ACT_COUNT')},{ShardingAttribute.APP_ID.value};{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}", 
              'EntryAppIDName;EntryAppIDName', 'HeaderWithTable','EntryAppIDNameGenres']
    return add_depending_count(compose, int(os.getenv('FILT_ACT_COUNT')), generator_func=add_filterer, params=params)
    
def add_filterers_english(compose: dict[str, Any]):
    #  name, type, queue, next_nodes, next_entries, header_type, entry_type
    params = ['english', FiltererType.ENGLISH.value, 
              f"{os.getenv('FILT_ENG')}", f"{os.getenv('GROUP_ENG')}",
              'EntryAppIDName', 'HeaderWithSender','EntryAppIDNameReviewText']
    return add_depending_count(compose, int(os.getenv('FILT_ENG_COUNT')), generator_func=add_filterer, params=params)
    
def add_groupers_action_english(compose: dict[str, Any]):
    # name, listening queue, next nodes, next entries, header type, entry type
    params = ['english', GrouperType.APP_ID_NAME_COUNT.value, f"{os.getenv('GROUP_ENG')}", f"{os.getenv('AGGR_ENG')}", 
              'HeaderWithSender', 'EntryAppIDName']
    return add_depending_count(compose, int(os.getenv('GROUP_ENG_COUNT')), generator_func=add_grouper,params=params)

def add_groupers_indie(compose: dict[str, Any]):
    # name, type, queue, next_nodes, header_type, entry_type 
    params = ['indie', GrouperType.APP_ID_COUNT.value,
              f"{os.getenv('GROUP_INDIE')}",f"{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}", 
              'HeaderWithTable', 'EntryAppID']
    return add_depending_count(compose, int(os.getenv('GROUP_INDIE_COUNT')), generator_func=add_grouper,params=params)

def add_groupers_os_count(compose: dict[str, Any]):
    # name, type, queue, next_nodes, header_type, entry_type 
    params = ['os-counts', GrouperType.OS_COUNT.value, f"{os.getenv('GROUP_OS')}", 
                               f"{os.getenv('AGGR_OS')}", 'Header', 'EntryOSSupport']
    return add_depending_count(compose, int(os.getenv('GROUP_OS_COUNT')), add_grouper, params=params)

def add_groupers_action_percentile(compose: dict[str, Any]):
    # name, type, queue, next_nodes, header_type, entry_type 
    params = ['percentile', GrouperType.APP_ID_COUNT.value, f"{os.getenv('GROUP_PERC')}", f"{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}",
              'HeaderWithTable', 'EntryAppID']
    return add_depending_count(compose, int(os.getenv('GROUP_PERC_COUNT')), add_grouper, params=params)

def add_joiners_action_percentile(compose: dict[str, Any]):
    # name, type, queue, next_nodes, review_entry_type, game_entry_type, node_id 
    containers = []
    for i in range(0, int(os.getenv('JOIN_PERC_COUNT'))):
        params = [f"percentile-{i}", JoinerType.PERCENTILE.value, f"{os.getenv('JOIN_PERC')}", f"{os.getenv('CONS_SORT_PERC')}", 'EntryAppIDReviewCount', 
                  'EntryAppIDName',i]
        compose, new_container = add_joiner(compose, params)
        containers.append(new_container)
    return compose, containers

def add_sorters_avg_playtime(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('SORT_AVG_PT_COUNT'))):
        compose, new_container = add_sorter(compose, name=f'playtime-{i}', type=SorterType.PLAYTIME.value,
                                             queue=f"{os.getenv('SORT_AVG_PT')}", next_nodes=f"{os.getenv('CONS_SORT_AVG_PT')}", header_type='Header', entry_type= 'EntryNameAvgPlaytime',
                                             node_id=i,node_count=f"{os.getenv('SORT_AVG_PT_COUNT')}", top=f"{os.getenv('SORT_AVG_PT_TOP')}")
        containers.append(new_container)
    return compose, containers

def add_sorters_indie(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('SORT_INDIE_COUNT'))):
        compose, new_container = add_sorter(compose, name=f'indie-{i}', type=SorterType.INDIE.value, queue=f"{os.getenv('SORT_INDIE')}", next_nodes=f"{os.getenv('CONS_SORT_INDIE')}",node_id=i,
                                            header_type='Header', entry_type= 'EntryNameReviewCount', node_count=f"{os.getenv('SORT_INDIE_COUNT')}", top=f"{os.getenv('SORT_INDIE_TOP')}")
        containers.append(new_container)
    return compose, containers

def add_sorter_consolidator_avg_playtime(compose: dict[str, Any]):
    return add_sorter_consolidator_top(compose, name=f'playtime', type=SorterType.CONSOLIDATOR_PLAYTIME.value, queue=f"{os.getenv('CONS_SORT_AVG_PT')}", next_nodes=f"{os.getenv('DISP')}", 
                                       header_type= 'HeaderWithSender', entry_type='EntryNameAvgPlaytime',prior_node_count=f"{os.getenv('SORT_AVG_PT_COUNT')}", top=f"{os.getenv('SORT_AVG_PT_TOP')}", query_number=2)

def add_sorter_consolidator_indie(compose: dict[str, Any]):
    return add_sorter_consolidator_top(compose, name=f'indie', type=SorterType.CONSOLIDATOR_INDIE.value, queue=f"{os.getenv('CONS_SORT_INDIE')}", next_nodes=f"{os.getenv('DISP')}", header_type='HeaderWithSender', entry_type='EntryNameReviewCount', prior_node_count=f"{os.getenv('SORT_INDIE_COUNT')}", top=f"{os.getenv('SORT_INDIE_TOP')}", query_number=3)

def add_sorter_consolidator_action_percentile(compose: dict[str, Any]):
    return add_sorter_consolidator_percentile(compose, name=f'sorter-consolidator-percentile', type=SorterType.CONSOLIDATOR_PERCENTILE.value, queue=f"{os.getenv('CONS_SORT_PERC')}", next_nodes=f"{os.getenv('DISP')}", header_type='HeaderWithSender', entry_type='EntryAppIDNameReviewCount', prior_node_count=f"{os.getenv('JOIN_PERC_COUNT')}", percentile=f"{os.getenv('CONS_PERC')}", query_number=5)

def add_joiners_indie(compose: dict[str, Any]):
    # name, type, queue, next_nodes, review_entry_type, game_entry_type, node_id 
    containers = []
    for i in range(0, int(os.getenv('JOIN_INDIE_COUNT'))):
        params = [f'indie-{i}', JoinerType.INDIE.value, f"{os.getenv('JOIN_INDIE')}", f"{os.getenv('AGGR_INDIE')}", 'EntryAppIDReviewCount', 'EntryAppIDName', i]
        compose, new_container = add_joiner(compose, params)
        containers.append(new_container)
    return compose, containers


def add_joiner_action_english(compose: dict[str, Any]):
    # name, type, queue, next_nodes, review_entry_type, game_entry_type, node_id 
    containers = []
    for i in range(0, int(os.getenv('JOIN_ACT_COUNT'))):
        params = [f'english-{i}', JoinerType.ENGLISH.value, f"{os.getenv('JOIN_ACT')}", f"{os.getenv('FILT_ENG')}", 'EntryAppIDReviewText', 'EntryAppIDName', i]
        compose, new_container = add_joiner(compose, params)
        containers.append(new_container)
    return compose, containers

def add_container(compose, containers, generation):
    compose, new_containers = generation(compose)
    containers.extend(new_containers)
    return compose, containers

def generate_compose(output_file: str, client_number: int):
    compose = {
        'services': {
        },
        'networks': {
        }
    }
    containers = [] #para agregarle todas las dependencias al border node

    #Client
    compose = add_all_clients(compose, client_number)

    #Network
    compose = add_network(compose)

    # Initializer
    compose, initializers_containers = add_initializers(compose)
    
    containers.extend(initializers_containers)

    # Query 3
    compose, containers = add_container(compose, containers, generation=add_filterers_indie)
    compose, containers = add_container(compose, containers, generation=add_groupers_indie)
    compose, containers = add_container(compose, containers, generation=add_joiners_indie) 
    compose, containers = add_container(compose, containers, generation=add_aggregator_indie)
    compose, containers = add_container(compose, containers, generation=add_sorters_indie)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_indie)


    # Border Node
    compose = add_border_node(compose, cluster_nodes=containers)

    with open(output_file, 'w') as file:
        yaml.dump(compose, file,sort_keys=False, default_flow_style=False)


def main():
    if len(sys.argv) != 3:
        print("run with: python3 compose-generator.py <output_file> <client_number>")
        return
    
    try:
        client_number = int(sys.argv[2])
        generate_compose(sys.argv[1], client_number)
    except ValueError as e:
        print(f"Error: second argument has to be a number (amount of clients desired)")
        raise e

if __name__ == '__main__':
    main()