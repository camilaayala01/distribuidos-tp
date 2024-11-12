import os
from typing import Any
import yaml, sys
from dotenv import load_dotenv
from aggregator.common.aggregatorTypes import AggregatorTypes
from filterer.common.filtererTypes import FiltererType
from grouper.common.grouperTypes import GrouperType
from internalCommunication.common.shardingAtribute import ShardingAttribute
from joiner.common.joinerTypes import JoinerType
from sorter.common.sorterTypes import SorterType
load_dotenv('compose.env')

def add_to_list(list, new_list):
    list.extend(new_list)
    return list

def add_client(compose: dict[str, Any]):
    return add_client_with_id(compose,'')

def add_client_with_id(compose: dict[str, Any], client_id: int):
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
            './entryParsing:/entryParsing'
    ]

def stateful_volumes(**kwargs):
    return f'./{kwargs["node_type"]}/{kwargs["name"]}:/{kwargs["name"]}'

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

def component_nodes_environment(**kwargs):
    if kwargs.get('node_id') is not None:
        return ([
            f'NEXT_NODES={kwargs["next_nodes"]}',
            f'HEADER_TYPE={kwargs["header_type"]}',
            f'ENTRY_TYPE={kwargs["entry_type"]}',
            f'NODE_ID={kwargs["node_id"]}'
        ])
    return ([
        f'NEXT_NODES={kwargs["next_nodes"]}',
        f'HEADER_TYPE={kwargs["header_type"]}',
        f'ENTRY_TYPE={kwargs["entry_type"]}',
    ])    

def joiner_nodes_environment(**kwargs):
    return ([
        f'NEXT_NODES={kwargs["next_nodes"]}',
        f'HEADER_TYPE=HeaderWithTable',
        f'GAMES_ENTRY_TYPE={kwargs["game_entry_type"]}',
        f'REVIEWS_ENTRY_TYPE={kwargs["review_entry_type"]}',
    ])
    
def default_config(compose: dict[str, Any], **kwargs):
    compose['services'][kwargs["container_name"]] ={
        'build': rabbit_node_build(kwargs["entrypoint"]),
        'environment': add_to_list(default_environment(kwargs["queue"]), add_to_list(component_nodes_environment(**kwargs), kwargs["extra_envs"])),
        'env_file': default_env_file(),
        'volumes': default_volumes(),
        'networks': default_network()
    }
    return compose
    
def default_config_with_tracker(compose: dict[str, Any], **kwargs):
    compose['services'][kwargs["name"]] = {
        'build': rabbit_node_build(kwargs["entrypoint"]),
        'environment': add_to_list(default_environment(kwargs["queue"]), add_to_list(component_nodes_environment(**kwargs), kwargs["extra_envs"])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), ['./packetTracker:/packetTracker', stateful_volumes(**kwargs)]),
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
                                    f'GAMES_NEXT_NODES={os.getenv("GROUP_OS")};{os.getenv("FILT_INDIE")};{os.getenv("FILT_ACT")}',
                                    'GAMES_NEXT_ENTRIES=EntryOSSupport;EntryAppIDNameGenresReleaseDateAvgPlaytime;EntryAppIDNameGenres',
                                    'GAMES_NEXT_HEADERS=Header;;',
                                    'REVIEWS_ENTRY_TYPE=ReviewEntry',
                                    f'REVIEWS_NEXT_NODES={os.getenv("GROUP_INDIE")};{os.getenv("JOIN_ACT")},{os.getenv("JOIN_ACT_COUNT")},{ShardingAttribute.APP_ID.value};{os.getenv("GROUP_PERC")}',
                                    'REVIEWS_NEXT_ENTRIES=EntryAppID;EntryAppIDReviewText;EntryAppID']),
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

def add_grouper(compose: dict[str, Any], **kwargs):
    container_name = f'grouper-{kwargs["name"]}'
    compose = default_config(compose, **kwargs, entrypoint='./grouper', container_name=container_name, extra_envs= [f'GROUPER_TYPE={kwargs["type"]}'])
    return compose, container_name


def add_sorter(compose: dict[str, Any], **kwargs):
    container_name = f'sorter-{kwargs["name"]}'
    kwargs["name"] = container_name
    kwargs["node_type"]='sorter'
    kwargs["entrypoint"]='./sorter'
    compose = default_config_with_tracker(compose, **kwargs)
    return compose, container_name

def add_sorter_consolidator_top(compose: dict[str, Any], **kwargs):
    container_name = f'sorter-consolidator-{kwargs["name"]}'
    kwargs["name"] = container_name
    kwargs["node_type"]='sorter-consolidator'
    kwargs["entrypoint"]='./sorter'
    compose = default_config_with_tracker(compose, **kwargs)
    return compose, [container_name]

def add_sorter_consolidator_percentile(compose: dict[str, Any], **kwargs):
    kwargs["node_type"]='sorter'
    kwargs["entrypoint"]='./sorter'
    compose = default_config_with_tracker(compose, **kwargs)
    return compose, [kwargs["name"]]

def add_joiner(compose: dict[str, Any], **kwargs):
    container_name = f'joiner-{kwargs["name"]}'
    kwargs["node_type"] = "joiner"
    compose['services'][container_name] = {
        'build': rabbit_node_build('./joiner'),
        'environment': add_to_list(default_environment(kwargs["queue"]), add_to_list(joiner_nodes_environment(**kwargs), 
                                                                                     [f'JOINER_TYPE={kwargs["type"]}', f'NODE_ID={kwargs["node_id"]}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), ['./packetTracker:/packetTracker', stateful_volumes(**kwargs)]),
        'networks': default_network()
    }
    return compose, container_name
    
def add_filterer(compose: dict[str, Any], **kwargs):
    container_name = f'filterer-{kwargs["name"]}'
    kwargs["container_name"] = container_name
    kwargs["entrypoint"] = './filterer'
    kwargs["extra_envs"] = [f'FILTERER_TYPE={kwargs["type"]}', f'NEXT_ENTRIES={kwargs["next_entries"]}']
    if kwargs.get('next_headers') is not None:
        kwargs["extra_envs"].append(f'NEXT_HEADERS={kwargs["next_headers"]}')   
    compose = default_config(compose, **kwargs)
    return compose, container_name

def add_aggregator_os(compose: dict[str, Any]): 
    name = 'aggregator-os'
    compose = default_config_with_tracker(compose, entrypoint='./aggregator', 
                                          name=name, 
                                          queue=f"{os.getenv('AGGR_OS')}", 
                                          next_nodes=f"{os.getenv('DISP')}", 
                                          header_type ='Header', 
                                          entry_type='EntryOSCount', 
                                          extra_envs=[f"AGGREGATOR_TYPE={AggregatorTypes.OS.value}", "QUERY_NUMBER=1"], node_type='aggregator')
    return compose, [name]

def add_aggregator_english(compose: dict[str, Any]):
    container_name = 'aggregator-english'
    compose = default_config_with_tracker(compose, entrypoint='./aggregator', 
                                          name=container_name, 
                                          queue=os.getenv('AGGR_ENG'), 
                                          next_nodes=os.getenv('DISP'), 
                                          header_type = 'HeaderWithSender', 
                                          entry_type = 'EntryAppIDNameReviewCount', 
                                          extra_envs=[f"AGGREGATOR_TYPE={AggregatorTypes.ENGLISH.value}", f'PRIOR_NODE_COUNT={os.getenv("JOIN_ACT_COUNT")}',"REQUIRED_REVIEWS=5000", "QUERY_NUMBER=4"], node_type='aggregator')
    return compose, [container_name]

def add_aggregator_indie(compose: dict[str, Any]):
    container_name = 'aggregator-indie'
    compose = default_config_with_tracker(compose, entrypoint='./aggregator', 
                                          name=container_name, 
                                          queue= f"{os.getenv('AGGR_INDIE')}", 
                                          next_nodes=f"{os.getenv('SORT_INDIE')},{os.getenv('SORT_INDIE_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}", 
                                          header_type='HeaderWithSender', 
                                          entry_type='EntryNameReviewCount', 
                                          extra_envs=[f"AGGREGATOR_TYPE={AggregatorTypes.INDIE.value}", f'PRIOR_NODE_COUNT={os.getenv("JOIN_INDIE_COUNT")}'], node_type='aggregator')
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

def add_multiple(compose: dict[str, Any], count, generator_func, **kwargs):
    name = kwargs["name"]

    containers = []
    for i in range(0, count):
        kwargs["name"] = f'{name}-{i}'
        compose, new_container = generator_func(compose, **kwargs)
        containers.append(new_container)
    return compose, containers

def add_one(compose, generator_func, **kwargs):
    compose, new_container = generator_func(compose, **kwargs)
    return compose, [new_container]

def add_depending_count(compose, count, generator_func, **kwargs):
    if count == 1:
        return add_one(compose, generator_func, **kwargs)
    else:
        return add_multiple(compose, count, generator_func, **kwargs)
    
def add_filterers_indie(compose: dict[str, Any]):
    # name, type, queue, next_nodes, next_entries, next_headers, header_type, entry_type
    params = [] 
    return add_depending_count(compose, int(os.getenv('FILT_INDIE_COUNT')), generator_func=add_filterer, name='indie', 
                               type=FiltererType.INDIE.value, queue=os.getenv('FILT_INDIE'),
                               next_nodes=f"{os.getenv('FILT_DEC')};{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}",
                               next_entries='EntryNameDateAvgPlaytime;EntryAppIDName',next_headers='Header;', header_type='HeaderWithTable', 
                               entry_type='EntryAppIDNameGenresReleaseDateAvgPlaytime')
    
def add_filterers_date(compose: dict[str, Any]):
    # name, type, queue, next_nodes, next_entries, header_type, entry_type
    params = []
    return add_depending_count(compose, int(os.getenv('FILT_DEC_COUNT')), generator_func=add_filterer, name='date', 
                               type=FiltererType.DECADE.value, queue=f"{os.getenv('FILT_DEC')}", next_nodes=f"{os.getenv('SORT_AVG_PT')},{os.getenv('SORT_AVG_PT_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}",
                               next_entries='EntryNameAvgPlaytime', header_type='Header', entry_type='EntryNameDateAvgPlaytime')
   
def add_filterers_action(compose: dict[str, Any]):
    # name, type, queue, next_nodes, next_entries, header_type, entry_type
    params = []
    return add_depending_count(compose, int(os.getenv('FILT_ACT_COUNT')), generator_func=add_filterer, name='action', type=FiltererType.ACTION.value,queue=f"{os.getenv('FILT_ACT')}",
              next_nodes=f"{os.getenv('JOIN_ACT')},{os.getenv('JOIN_ACT_COUNT')},{ShardingAttribute.APP_ID.value};{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}", 
              next_entries='EntryAppIDName;EntryAppIDName', header_type='HeaderWithTable',entry_type='EntryAppIDNameGenres')
    
def add_filterers_english(compose: dict[str, Any]):
   
    return add_depending_count(compose, int(os.getenv('FILT_ENG_COUNT')), generator_func=add_filterer, name='english', 
                               type=FiltererType.ENGLISH.value, queue=f"{os.getenv('FILT_ENG')}", next_nodes=f"{os.getenv('GROUP_ENG')}",
                               next_entries='EntryAppIDName', header_type='HeaderWithSender',entry_type='EntryAppIDNameReviewText')
    
def add_groupers_action_english(compose: dict[str, Any]):
    # name, type, queue, next_nodes, header_type, entry_type
    params = []
    return add_depending_count(compose, int(os.getenv('GROUP_ENG_COUNT')), generator_func=add_grouper,name='english', 
                               type=GrouperType.APP_ID_NAME_COUNT.value, queue=f"{os.getenv('GROUP_ENG')}", next_nodes=f"{os.getenv('AGGR_ENG')}", 
                               header_type='HeaderWithSender', entry_type='EntryAppIDName')

def add_groupers_indie(compose: dict[str, Any]):
    # name, type, queue, next_nodes, header_type, entry_type 
    params = []
    return add_depending_count(compose, int(os.getenv('GROUP_INDIE_COUNT')), generator_func=add_grouper,name='indie', type=GrouperType.APP_ID_COUNT.value,
              queue=f"{os.getenv('GROUP_INDIE')}", next_nodes=f"{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}", 
              header_type='HeaderWithTable', entry_type='EntryAppID')

def add_groupers_os_count(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_OS_COUNT')), add_grouper, name='os-counts', 
                               type=GrouperType.OS_COUNT.value,queue=f"{os.getenv('GROUP_OS')}", 
                               next_nodes=f"{os.getenv('AGGR_OS')}", header_type='Header', entry_type='EntryOSSupport')

def add_groupers_action_percentile(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_PERC_COUNT')), add_grouper, name='percentile', 
                               type=GrouperType.APP_ID_COUNT.value, queue=f"{os.getenv('GROUP_PERC')}", 
                               next_nodes=f"{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}", 
                               header_type='HeaderWithTable', entry_type ='EntryAppID')

def add_joiners_action_percentile(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_PERC_COUNT'))):
        compose, new_container = add_joiner(compose, name=f"percentile-{i}", type=JoinerType.PERCENTILE.value, queue=f"{os.getenv('JOIN_PERC')}", next_nodes=f"{os.getenv('CONS_SORT_PERC')}", review_entry_type='EntryAppIDReviewCount', game_entry_type='EntryAppIDName', node_id=i)
        containers.append(new_container)
    return compose, containers

def add_sorters_avg_playtime(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('SORT_AVG_PT_COUNT'))):
        compose, new_container = add_sorter(compose, name=f'playtime-{i}',
                                             queue=f"{os.getenv('SORT_AVG_PT')}", next_nodes=f"{os.getenv('CONS_SORT_AVG_PT')}", 
                                             header_type='Header', entry_type= 'EntryNameAvgPlaytime',node_id=i,
                                             extra_envs=[f'SORTER_TYPE={SorterType.PLAYTIME.value}',f'TOP_AMOUNT={os.getenv("SORT_AVG_PT_TOP")}',f'NODE_COUNT={os.getenv("SORT_AVG_PT_COUNT")}','NEXT_HEADERS=HeaderWithSender'])
        containers.append(new_container)
    return compose, containers

def add_sorters_indie(compose: dict[str, Any]):
    containers = [] 
    for i in range(0, int(os.getenv('SORT_INDIE_COUNT'))):
        compose, new_container = add_sorter(compose, name=f'indie-{i}',
                                            queue=f"{os.getenv('SORT_INDIE')}", next_nodes=f"{os.getenv('CONS_SORT_INDIE')}",node_id=i,
                                            header_type='Header', entry_type= 'EntryNameReviewCount', extra_envs=[f'SORTER_TYPE={SorterType.INDIE.value}',f'TOP_AMOUNT={os.getenv("SORT_INDIE_TOP")}',f'NODE_COUNT={os.getenv("SORT_INDIE_COUNT")}','NEXT_HEADERS=HeaderWithSender'])
        containers.append(new_container)
    return compose, containers

def add_sorter_consolidator_avg_playtime(compose: dict[str, Any]):
    return add_sorter_consolidator_top(compose, name=f'playtime',
                                       queue=f"{os.getenv('CONS_SORT_AVG_PT')}", next_nodes=f"{os.getenv('DISP')}", 
                                       header_type= 'HeaderWithSender', entry_type='EntryNameAvgPlaytime',
                                        extra_envs=[f'SORTER_TYPE={SorterType.CONSOLIDATOR_PLAYTIME.value}', f'PRIOR_NODE_COUNT={os.getenv("SORT_AVG_PT_COUNT")}', 
                                                    f'TOP_AMOUNT={os.getenv("SORT_AVG_PT_TOP")}', f'QUERY_NUMBER=2', 'NEXT_HEADERS=HeaderWithQueryNumber'])

def add_sorter_consolidator_indie(compose: dict[str, Any]):
    return add_sorter_consolidator_top(compose, name=f'indie', 
                                       queue=f"{os.getenv('CONS_SORT_INDIE')}", 
                                       next_nodes=f"{os.getenv('DISP')}", header_type='HeaderWithSender', 
                                       entry_type='EntryNameReviewCount', extra_envs=[f'SORTER_TYPE={SorterType.CONSOLIDATOR_INDIE.value}', f'PRIOR_NODE_COUNT={os.getenv("SORT_INDIE_COUNT")}', 
                                                    f'TOP_AMOUNT={os.getenv("SORT_INDIE_TOP")}', f'QUERY_NUMBER=3', 'NEXT_HEADERS=HeaderWithQueryNumber'])

def add_sorter_consolidator_action_percentile(compose: dict[str, Any]):
    
    return add_sorter_consolidator_percentile(compose, name=f'sorter-consolidator-percentile', 
                                              queue=f"{os.getenv('CONS_SORT_PERC')}", next_nodes=f"{os.getenv('DISP')}", 
                                              header_type='HeaderWithSender', entry_type='EntryAppIDNameReviewCount', 
                                              extra_envs=[f'SORTER_TYPE={SorterType.CONSOLIDATOR_PERCENTILE.value}', 
                                                          f'PRIOR_NODE_COUNT={os.getenv("JOIN_PERC_COUNT")}', 
                                                          f'PERCENTILE={os.getenv("CONS_PERC")}', f'QUERY_NUMBER=5', 'NEXT_HEADERS=HeaderWithQueryNumber'])

def add_joiners_indie(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_INDIE_COUNT'))):
        compose, new_container = add_joiner(compose, name=f'indie-{i}', type=JoinerType.INDIE.value, 
                                            queue=f"{os.getenv('JOIN_INDIE')}", next_nodes=f"{os.getenv('AGGR_INDIE')}",
                                            review_entry_type='EntryAppIDReviewCount', game_entry_type='EntryAppIDName', node_id=i )
        containers.append(new_container)
    return compose, containers


def add_joiner_action_english(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_ACT_COUNT'))):
        compose, new_container = add_joiner(compose, name=f'english-{i}', type=JoinerType.ENGLISH.value, 
                                            queue=f"{os.getenv('JOIN_ACT')}", next_nodes=f"{os.getenv('FILT_ENG')}", 
                                            review_entry_type='EntryAppIDReviewText', game_entry_type='EntryAppIDName', node_id=i)
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

    # Query 1:
    compose, containers = add_container(compose, containers, generation=add_groupers_os_count)
    compose, containers = add_container(compose, containers, generation=add_aggregator_os)

    # Query 2 :
    compose, containers = add_container(compose, containers, generation=add_filterers_indie)
    compose, containers = add_container(compose, containers, generation=add_filterers_date)
    compose, containers = add_container(compose, containers, generation=add_sorters_avg_playtime)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_avg_playtime)

    # Query 3
    #filter indie
    compose, containers = add_container(compose, containers, generation=add_groupers_indie)
    compose, containers = add_container(compose, containers, generation=add_joiners_indie) 
    compose, containers = add_container(compose, containers, generation=add_aggregator_indie)
    compose, containers = add_container(compose, containers, generation=add_sorters_indie)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_indie)

    #Query 4
    compose, containers = add_container(compose, containers, generation=add_filterers_action)
    compose, containers = add_container(compose, containers, generation=add_joiner_action_english)
    compose, containers = add_container(compose, containers, generation=add_filterers_english)
    compose, containers = add_container(compose, containers, generation=add_groupers_action_english)
    compose, containers = add_container(compose, containers, generation=add_aggregator_english)

    # Query 5
    #filter action
    compose, containers = add_container(compose, containers, generation=add_groupers_action_percentile)
    compose, containers = add_container(compose, containers, generation=add_joiners_action_percentile)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_action_percentile)


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