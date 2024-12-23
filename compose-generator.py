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
            'AMOUNT_OF_EXECUTIONS=1',
            f'BORDER_NODE_ADDR=tcp://border-node:{os.getenv("CLIENT_PORT")}',
            'MAX_TIMEOUTS=10',
            'TIMEOUT=2000'
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
            './healthcheckAnswerController:/healthcheckAnswerController'
    ]

def stateful_volumes(node_type, queue, node_id: str=None):
    if node_id is not None:
        return f'./{node_type}/{queue}{node_id}:/{queue}'
    
    return f'./{node_type}/{queue}:/{queue}'

def default_network():
    return [
            'sa_net'
    ]

def default_env_file():
    return [
            '.env'
    ]

def default_environment(queue, prefetch_count: int = 1)-> list[str]:
    return ([
            'PYTHONUNBUFFERED=1',
            f'PREFETCH_COUNT={prefetch_count}',
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
    envs = []
    for key, value in kwargs.items():
        envs.append(f"{key.upper()}={value}")

    return envs  

    
def default_config(compose: dict[str, Any], container_name, entrypoint, queue, prefetch_count: int=1, **kwargs):
    compose['services'][container_name] ={
        'build': rabbit_node_build(entrypoint),
        'environment': add_to_list(default_environment(queue, prefetch_count), component_nodes_environment(**kwargs)) + [f'NODE_NAME={container_name}'],
        'env_file': default_env_file(),
        'volumes': default_volumes(),
        'networks': default_network()
    }
    return compose
    
def default_config_with_tracker(compose: dict[str, Any], container_name, entrypoint, queue, node_type, prefetch_count: int=1, **kwargs):
    compose = default_config(compose, container_name, entrypoint, queue, prefetch_count, **kwargs)
    compose['services'][container_name]['volumes'].extend([
        './packetTracker:/packetTracker', 
        './statefulNode:/statefulNode',
        './eofController:/eofController',
        stateful_volumes(node_type, queue, kwargs.get('node_id'))
    ])
    return compose

def add_initializer(compose: dict[str, Any], id):
    container_name = f'initializer-{id}' 
    compose = default_config(compose, container_name, './initializer', os.getenv('INIT'), 40,
                             header_type='HeaderWithTable',
                             games_next_nodes=f'{os.getenv("GROUP_OS")};{os.getenv("FILT_INDIE")};{os.getenv("FILT_ACT")}',
                             games_next_entries='EntryOSSupport;EntryAppIDNameGenresReleaseDateAvgPlaytime;EntryAppIDNameGenres',
                             games_next_headers='Header;;',
                             reviews_next_nodes=f'{os.getenv("GROUP_INDIE")};{os.getenv("JOIN_ACT")},{os.getenv("JOIN_ACT_COUNT")},{ShardingAttribute.APP_ID.value};{os.getenv("GROUP_PERC")}',
                             reviews_next_entries='EntryAppID;EntryAppIDReviewText;EntryAppID',
                             storage='clients')
    
    compose['services'][container_name]['volumes'].extend([
        './packetTracker:/packetTracker',
        './initializer/clients:/clients',       
    ])
    return compose, container_name

def add_initializers(compose: dict[str, Any]):
    containers = []
    for i in range(0, 1):
        compose, new_container = add_initializer(compose, i)
        containers.append(new_container)
    return compose, containers

def add_grouper(compose: dict[str, Any], name, queue, **kwargs):
    container_name = f'grouper-{name}'
    compose = default_config(compose, container_name, './grouper', queue, **kwargs)
    return compose, container_name


def add_sorter(compose: dict[str, Any], name, queue, **kwargs):
    container_name = f'sorter-{name}'
    compose = default_config_with_tracker(compose, container_name, './sorter', queue, 'sorter', **kwargs)
    return compose, container_name

def add_sorter_consolidator(compose: dict[str, Any], name, queue, **kwargs):
    container_name = f'sorter-consolidator-{name}'
    compose = default_config_with_tracker(compose, container_name, './sorter', queue, 'sorter', **kwargs)
    return compose, [container_name]

def add_sorter_consolidator_percentile(compose: dict[str, Any], **kwargs):
    return add_sorter_consolidator(compose, 'percentile', os.getenv('CONS_SORT_PERC'), **kwargs)

def add_joiner(compose: dict[str, Any], name, queue, **kwargs):
    container_name = f'joiner-{name}'
    compose = default_config_with_tracker(compose, container_name, './joiner', queue, 'joiner', 50, **kwargs)
    return compose, container_name
    
def add_filterer(compose: dict[str, Any], name, queue, **kwargs):
    container_name = f'filterer-{name}'
    compose = default_config(compose, container_name, queue=queue, entrypoint='./filterer', **kwargs)
    return compose, container_name

def add_aggregator_os(compose: dict[str, Any]): 
    name = 'aggregator-os'
    compose = default_config_with_tracker(compose, name, './aggregator', os.getenv('AGGR_OS'), 'aggregator',
                                          next_nodes=f"{os.getenv('DISP')}", 
                                          header_type ='Header', 
                                          entry_type='EntryOSCount', 
                                          aggregator_type=AggregatorTypes.OS.value,
                                          query_number=1)
    return compose, [name]

def add_aggregator_english(compose: dict[str, Any]):
    container_name = 'aggregator-english'
    compose = default_config_with_tracker(compose, container_name, './aggregator', os.getenv('AGGR_ENG'), 'aggregator',
                                          next_nodes=f"{os.getenv('DISP')}", 
                                          next_entries="EntryName",
                                          header_type ='HeaderWithSender', 
                                          entry_type='EntryAppIDNameReviewCount', 
                                          aggregator_type=AggregatorTypes.ENGLISH.value,
                                          query_number=4,
                                          required_reviews=5000)
    return compose, [container_name]

def add_aggregator_indie(compose: dict[str, Any]):
    container_name = 'aggregator-indie'
    compose = default_config_with_tracker(compose, container_name, './aggregator', os.getenv('AGGR_INDIE'), 'aggregator',
                                          next_nodes=f"{os.getenv('SORT_INDIE')},{os.getenv('SORT_INDIE_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}", 
                                          header_type ='HeaderWithSender', 
                                          entry_type='EntryNameReviewCount', 
                                          aggregator_type=AggregatorTypes.INDIE.value)

    return compose, [container_name]

def add_border_node(compose: dict[str, Any]):
    container_name = "border-node"
    compose['services'][container_name]= {
        'build': {
            'context': './borderNode',
            'dockerfile': '../zmqUser.Dockerfile'
        },
        'environment': default_environment(os.getenv("DISP")) +
          ['NODE_NAME=border-node',
           'STORAGE_PATH=/data/', 
           f'CLIENT_PORT={os.getenv("CLIENT_PORT")}',
           ],
        'env_file': default_env_file(),
        'volumes': default_volumes() + ['./borderNode/data:/data'],
        'networks': default_network()
    }
    return compose, [container_name]

def add_multiple(compose: dict[str, Any], count, generator_func, name, queue, **kwargs):
    containers = []
    for i in range(0, count):
        cont_name = f'{name}-{i}'
        compose, new_container = generator_func(compose, cont_name, queue, **kwargs)
        containers.append(new_container)
    return compose, containers

def add_one(compose, generator_func, name, queue, **kwargs):
    compose, new_container = generator_func(compose, name, queue, **kwargs)
    return compose, [new_container]

def add_depending_count(compose, count, generator_func, name, queue, **kwargs):
    if count == 1:
        return add_one(compose, generator_func, name, queue, **kwargs)
    else:
        return add_multiple(compose, count, generator_func, name, queue, **kwargs)
    
def add_filterers_indie(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_INDIE_COUNT')), add_filterer, 'indie', os.getenv('FILT_INDIE'), 
                               filterer_type=FiltererType.INDIE.value,
                               next_nodes=f"{os.getenv('FILT_DEC')};{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}",
                               next_entries='EntryNameDateAvgPlaytime;EntryAppIDName',
                               next_headers='Header;', 
                               header_type='HeaderWithTable', 
                               entry_type='EntryAppIDNameGenresReleaseDateAvgPlaytime')
    
def add_filterers_date(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_DEC_COUNT')), add_filterer, 'date', os.getenv('FILT_DEC'),
                               filterer_type=FiltererType.DECADE.value, 
                               next_nodes=f"{os.getenv('SORT_AVG_PT')},{os.getenv('SORT_AVG_PT_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}",
                               next_entries='EntryNameAvgPlaytime', 
                               header_type='Header', 
                               entry_type='EntryNameDateAvgPlaytime')
   
def add_filterers_action(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_ACT_COUNT')), add_filterer, 'action', os.getenv('FILT_ACT'),
                               filterer_type=FiltererType.ACTION.value,
                               next_nodes=f"{os.getenv('JOIN_ACT')},{os.getenv('JOIN_ACT_COUNT')},{ShardingAttribute.APP_ID.value};{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}", 
                               next_entries='EntryAppIDName;EntryAppIDName', 
                               header_type='HeaderWithTable',
                               entry_type='EntryAppIDNameGenres')
    
def add_filterers_english(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_ENG_COUNT')), add_filterer, 'english', os.getenv('FILT_ENG'),
                               filterer_type=FiltererType.ENGLISH.value, 
                               next_nodes=f"{os.getenv('GROUP_ENG')}",
                               next_entries='EntryAppIDName', 
                               header_type='HeaderWithSender',
                               entry_type='EntryAppIDNameReviewText')
    
def add_groupers_action_english(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_ENG_COUNT')), add_grouper, 'english', os.getenv('GROUP_ENG'),
                               grouper_type=GrouperType.APP_ID_NAME_COUNT.value, 
                               next_nodes=f"{os.getenv('AGGR_ENG')}", 
                               header_type='HeaderWithSender', 
                               entry_type='EntryAppIDName')

def add_groupers_indie(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_INDIE_COUNT')), add_grouper, 'indie', os.getenv('GROUP_INDIE'), 
                               grouper_type=GrouperType.APP_ID_COUNT.value, next_nodes=f"{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}", 
                               header_type='HeaderWithTable', 
                               entry_type='EntryAppID')

def add_groupers_os_count(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_OS_COUNT')), add_grouper, 'os', os.getenv('GROUP_OS'), 
                               grouper_type=GrouperType.OS_COUNT.value,
                               next_nodes=f"{os.getenv('AGGR_OS')}", 
                               header_type='Header', 
                               entry_type='EntryOSSupport')

def add_groupers_action_percentile(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_PERC_COUNT')), add_grouper, 'percentile', os.getenv('GROUP_PERC'), 
                                grouper_type=GrouperType.APP_ID_COUNT.value,
                                next_nodes=f"{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}", 
                                header_type='HeaderWithTable', entry_type ='EntryAppID')

def add_joiners_action_percentile(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_PERC_COUNT'))):
        compose, new_container = add_joiner(compose, f"percentile-{i}", f"{os.getenv('JOIN_PERC')}",
                                            joiner_type=JoinerType.REGULAR.value, 
                                            next_nodes=f'{os.getenv("CONS_SORT_PERC")}', 
                                            next_headers="HeaderWithSender",
                                            reviews_entry_type='EntryAppIDReviewCount', 
                                            games_entry_type='EntryAppIDName', 
                                            header_type='HeaderWithTable',
                                            node_id=i,
                                            node_count=int(os.getenv('JOIN_PERC_COUNT')))
        containers.append(new_container)
    return compose, containers

def add_sorters_avg_playtime(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('SORT_AVG_PT_COUNT'))):
        compose, new_container = add_sorter(compose, f'playtime-{i}', os.getenv("SORT_AVG_PT"), 
                                            next_nodes=f"{os.getenv('CONS_SORT_AVG_PT')}", 
                                            header_type='Header', 
                                            entry_type= 'EntryNameAvgPlaytime',
                                            node_id=i,
                                            sorter_type=SorterType.PLAYTIME.value, 
                                            top_amount=os.getenv("SORT_AVG_PT_TOP"),
                                            node_count=os.getenv("SORT_AVG_PT_COUNT"),
                                            next_headers="HeaderWithSender")
        containers.append(new_container)
    return compose, containers

def add_sorters_indie(compose: dict[str, Any]):
    containers = [] 
    for i in range(0, int(os.getenv('SORT_INDIE_COUNT'))):
        compose, new_container = add_sorter(compose, f'indie-{i}', os.getenv('SORT_INDIE'), 
                                            next_nodes=f"{os.getenv('CONS_SORT_INDIE')}",
                                            node_id=i,
                                            header_type='Header', 
                                            entry_type= 'EntryNameReviewCount', 
                                            sorter_type=f'{SorterType.INDIE.value}',
                                            top_amount=f'{os.getenv("SORT_INDIE_TOP")}',
                                            node_count=f'{os.getenv("SORT_INDIE_COUNT")}', 
                                            next_headers="HeaderWithSender")
        containers.append(new_container)
    return compose, containers

def add_sorter_consolidator_avg_playtime(compose: dict[str, Any]):
    return add_sorter_consolidator(compose, 'playtime', os.getenv('CONS_SORT_AVG_PT'), 
                                   next_nodes=f"{os.getenv('DISP')}", 
                                   next_headers='HeaderWithQueryNumber',
                                   header_type= 'HeaderWithSender', 
                                   entry_type='EntryNameAvgPlaytime',
                                   sorter_type=f'{SorterType.CONSOLIDATOR_PLAYTIME.value}',
                                   top_amount=f'{os.getenv("SORT_AVG_PT_TOP")}',
                                   query_number=2)

def add_sorter_consolidator_indie(compose: dict[str, Any]):
    return add_sorter_consolidator(compose, 'indie', os.getenv('CONS_SORT_INDIE'),
                                   next_nodes=f"{os.getenv('DISP')}", 
                                   next_headers='HeaderWithQueryNumber',
                                   header_type='HeaderWithSender',
                                   entry_type='EntryNameReviewCount', 
                                   sorter_type=f'{SorterType.CONSOLIDATOR_INDIE.value}',
                                   top_amount=f'{os.getenv("SORT_INDIE_TOP")}', 
                                   query_number=3)

def add_sorter_consolidator_action_percentile(compose: dict[str, Any]):
    return add_sorter_consolidator_percentile(compose, 
                                              next_nodes=f"{os.getenv('DISP')}", 
                                              header_type='HeaderWithSender', entry_type='EntryAppIDNameReviewCount', 
                                              sorter_type=f'{SorterType.CONSOLIDATOR_PERCENTILE.value}',
                                              percentile=f'{os.getenv("CONS_PERC")}', 
                                              query_number=5, 
                                              next_headers='HeaderWithQueryNumber')

def add_joiners_indie(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_INDIE_COUNT'))):
        compose, new_container = add_joiner(compose, f'indie-{i}', os.getenv('JOIN_INDIE'),
                                            joiner_type=JoinerType.REGULAR.value,
                                            next_nodes=f"{os.getenv('AGGR_INDIE')}", 
                                            next_headers="HeaderWithSender",
                                            next_entries="EntryNameReviewCount",
                                            reviews_entry_type='EntryAppIDReviewCount',
                                            games_entry_type='EntryAppIDName', 
                                            header_type='HeaderWithTable',
                                            node_id=i,
                                            node_count=int(os.getenv('JOIN_INDIE_COUNT')))
        containers.append(new_container)
    return compose, containers


def add_joiner_action_english(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_ACT_COUNT'))):
        compose, new_container = add_joiner(compose, f'english-{i}', os.getenv('JOIN_ACT'),
                                            joiner_type=JoinerType.ENGLISH.value, 
                                            next_nodes=f"{os.getenv('FILT_ENG')}", 
                                            next_headers="HeaderWithSender",
                                            reviews_entry_type='EntryAppIDReviewText',
                                            header_type='HeaderWithTable',
                                            games_entry_type='EntryAppIDName', 
                                            node_id=i,
                                            node_count=int(os.getenv('JOIN_ACT_COUNT')))
        containers.append(new_container)
    return compose, containers

def add_monitor(compose: dict[str, Any], cluster_nodes: list[str], id, monitors_amount):
    container_name = f'monitor-{id}'
    compose['services'][container_name]= {
        'build': {
            'context': './monitor',
            'dockerfile': '../monitor.Dockerfile'
        },
        'environment':[
            'PYTHONUNBUFFERED=1',
            'PREFETCH_COUNT=1',
            f'ID={id}',
            f'TO_CHECK={";".join(cluster_nodes)}',
            'RETRIES=2',
            'TIMER_DURATION=4',
            'CONTAINER_NAME=distribuidos-tp',
            'ELECTION_PORT=9500',
            f'MONITOR_COUNT={monitors_amount}',
        ],
        'env_file': default_env_file(),
        'volumes':[
            '/var/run/docker.sock:/var/run/docker.sock',
            './healthcheckAnswerController:/healthcheckAnswerController',
            './entryParsing:/entryParsing'
        ],
        'networks': default_network(),
        'depends_on': cluster_nodes
    }
    return compose, container_name

def add_all_monitors(compose: dict[str, Any], containers):
    monitors_amount = 4
    monitors = []
    for id in range(1, monitors_amount + 1):
        compose, new_container = add_monitor(compose, containers, id, monitors_amount)
        monitors.append(new_container)

    monitors.extend(containers)
    return compose, monitors

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
    # filter action
    compose, containers = add_container(compose, containers, generation=add_groupers_action_percentile)
    compose, containers = add_container(compose, containers, generation=add_joiners_action_percentile)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_action_percentile)


    # Border Node
    compose, containers = add_container(compose, containers, generation=add_border_node)

    # Monitors
    compose, containers = add_all_monitors(compose, containers=containers)

    with open(output_file, 'w') as file:
        yaml.dump(compose, file, sort_keys=False, default_flow_style=False)
    
    with open("chaos.env", "w+") as file:
        file.write(f'TO_CHECK={";".join(containers)}\n')
        file.write(f'CONTAINER_NAME=distribuidos-tp')


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