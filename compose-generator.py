import os
from typing import Any
import yaml, sys
import argparse

from filterer.common.filtererTypes import FiltererType
from grouper.common.grouperTypes import GrouperType
from joiner.common.joinerTypes import JoinerType
from joinerConsolidator.common.joinerConsolidatorTypes import JoinerConsolidatorType
from joinerCount.common.joinerCountTypes import JoinerCountType
from sendingStrategy.common.shardingAtribute import ShardingAttribute
from sorter.common.sorterTypes import SorterType

from dotenv import load_dotenv
load_dotenv('compose.env')

def add_to_list(list, new_list):
    list.extend(new_list)
    return list

def add_client(compose: dict[str, Any]):
    return add_client_with_id(compose,'')

def add_client_with_id(compose: dict[str, Any], client_id: int):
    compose['services'][f'client{client_id}']= {
        'build': zmq_node_build('./client'),
        'environment':[
            'PYTHONUNBUFFERED=1'
        ],
        'volumes':[
            './entryParsing:/entryParsing',
            '~/.kaggle/distribuidos:/datasets',
            f'./client{client_id}/responses:/responses',
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

def default_network():
    return [
            'sa_net'
    ]

def default_env_file():
    return [
            '.env'
    ]

def default_environment()-> list[str]:
    return ([
            'PYTHONUNBUFFERED=1',
            'HOST=rabbitmq'
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

def component_nodes_environment(queue, next_nodes):
    return ([
        f'LISTENING_QUEUE={queue}',
        f'NEXT_NODES={next_nodes}'
    ])
    

def component_nodes_volumes()-> list[str]:
    return ([
        './sendingStrategy:/sendingStrategy'
    ])

def add_grouper(compose: dict[str, Any], name, type, queue, next_nodes):
    container_name = f'grouper-{name}'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./grouper') ,
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes), [f'GROUPER_TYPE={type}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(),component_nodes_volumes()),
        'networks': default_network()
    }
    return compose, container_name


def add_sorter(compose: dict[str, Any], name, type, queue, next_nodes, node_id, node_count, top):
    container_name = f'sorter-{name}'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./sorter'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes),[f'SORTER_TYPE={type}', f'NODE_ID={node_id}', f'TOP_AMOUNT={top}', f'NODE_COUNT={node_count}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(),['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }
    return compose, container_name

def add_sorter_consolidator_top(compose: dict[str, Any], name, type, queue, next_nodes, prior_node_count, top, query_number):
    container_name = f'sorter-consolidator-{name}'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./sorter'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes),[f'SORTER_TYPE={type}', f'PRIOR_NODE_COUNT={prior_node_count}', f'TOP_AMOUNT={top}', f'QUERY_NUMBER={query_number}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(),['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }
    return compose, [container_name]

def add_sorter_consolidator_percentile(compose: dict[str, Any], name, type, queue, next_nodes,prior_node_count, percentile, query_number):
    compose['services'][name] ={
        'build': rabbit_node_build('./sorter'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes),[f'SORTER_TYPE={type}', f'PRIOR_NODE_COUNT={prior_node_count}', f'PERCENTILE={percentile}', f'QUERY_NUMBER={query_number}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(),['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }
    return compose, [name]

def add_joiner(compose: dict[str, Any], name, type, queue, next_nodes, node_id):
    container_name = f'joiner-{name}'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./joiner'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes),[f'JOINER_TYPE={type}', f'NODE_ID={node_id}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(),['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }
    return compose, container_name
    
def add_filterer(compose: dict[str, Any], name, type, queue, next_nodes):
    container_name = f'filterer-{name}'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./filterer'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes),[f'FILTERER_TYPE={type}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), component_nodes_volumes()),
        'networks': default_network()
    }  
    return compose, container_name


def add_joiner_consolidator(compose: dict[str, Any], name, type, queue, next_nodes, prior_node_count):
    container_name = f'{name}-consolidator'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./joinerConsolidator'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(queue, next_nodes), [f'JOINER_CONSOLIDATOR_TYPE={type}', f'PRIOR_NODE_COUNT={prior_node_count}'])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(), ['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }  
    return compose, [container_name]

def add_joiner_os_count(compose: dict[str, Any]): 
    name = 'joiner-os-counts'
    compose['services'][name] ={
        'build': rabbit_node_build('./joinerCount'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(f"{os.getenv('JOIN_OS')}", f"{os.getenv('DISP')}"), [f"JOINER_COUNT_TYPE={JoinerCountType.OS.value}", "QUERY_NUMBER=1"])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(), ['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }  
    return compose, [name]

def add_joiner_english_count(compose: dict[str, Any], name, node_id):
    container_name = f'{name}-{node_id}'
    compose['services'][container_name] ={
        'build': rabbit_node_build('./joinerCount'),
        'environment': add_to_list(default_environment(), add_to_list(component_nodes_environment(os.getenv('JOIN_ENG'), f"{os.getenv('CONS_JOIN_STREAM')}"), [f"JOINER_COUNT_TYPE={JoinerCountType.ENGLISH.value}", f"NODE_ID={node_id}", "REQUIRED_REVIEWS=5000"])),
        'env_file': default_env_file(),
        'volumes': add_to_list(default_volumes(), add_to_list(component_nodes_volumes(), ['./packetTracker:/packetTracker'])),
        'networks': default_network()
    }  
    return compose, container_name

def add_initializer(compose: dict[str, Any]):
    container_name = 'initializer'
    compose['services'][container_name] = {
        'build': rabbit_node_build('./initializer'),
        'environment':default_environment(),
        'env_file': default_env_file(),
        'volumes': default_volumes(),
        'networks': default_network()
    }
    return compose, container_name

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

def add_multiple(compose: dict[str, Any], count, generator_func, name, type, queue, next_nodes):
    containers = []
    for i in range(0, count):
        compose, new_container = generator_func(compose, f'{name}-{i}', type, queue, next_nodes)
        containers.append(new_container)
    return compose, containers

def add_one(compose, generator_func, name, type, queue, next_nodes):
    compose, new_container = generator_func(compose, name, type, queue, next_nodes)
    return compose, [new_container]

def add_depending_count(compose, count, generator_func,name, type, queue, next_nodes):
    if count == 1:
        return add_one(compose, generator_func, name, type, queue, next_nodes)
    else:
        return add_multiple(compose, count, generator_func,name, type, queue, next_nodes)
    
def add_filterers_indie(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_INDIE_COUNT')), generator_func=add_filterer, name='indie', type=FiltererType.INDIE.value, queue=os.getenv('FILT_INDIE'), next_nodes=f"{os.getenv('FILT_DEC')};{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}")
    
def add_filterers_date(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_DEC_COUNT')), generator_func=add_filterer, name='date',type = FiltererType.DECADE.value,queue=f"{os.getenv('FILT_DEC')}",next_nodes=f"{os.getenv('SORT_AVG_PT')},{os.getenv('SORT_AVG_PT_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}")
   
def add_filterers_action(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_ACT_COUNT')), generator_func=add_filterer, name='action',type=FiltererType.ACTION.value, queue=f"{os.getenv('FILT_ACT')}",
                               next_nodes=f"{os.getenv('JOIN_ACT')},{os.getenv('JOIN_ACT_COUNT')},{ShardingAttribute.APP_ID.value};{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}")
    
def add_filterers_english(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('FILT_ENG_COUNT')), generator_func=add_filterer,name='english', type=FiltererType.ENGLISH.value, queue=f"{os.getenv('FILT_ENG')}",next_nodes=f"{os.getenv('GROUP_ENG')}")
    
def add_groupers_action_english(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_ENG_COUNT')), generator_func=add_grouper,name='action-english', type=GrouperType.APP_ID_NAME_COUNT.value, queue=f"{os.getenv('GROUP_ENG')}",next_nodes=f"{os.getenv('CONS_JOIN_ENG')}")

def add_groupers_indie(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_INDIE_COUNT')), generator_func=add_grouper,name='indie', type=GrouperType.APP_ID_COUNT.value, 
                               queue=f"{os.getenv('GROUP_INDIE')}",next_nodes=f"{os.getenv('JOIN_INDIE')},{os.getenv('JOIN_INDIE_COUNT')},{ShardingAttribute.APP_ID.value}")

def add_groupers_os_count(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_OS_COUNT')), add_grouper, name='os-counts', type=GrouperType.OS_COUNT.value, queue=f"{os.getenv('GROUP_OS')}", next_nodes=f"{os.getenv('JOIN_OS')}")

def add_groupers_action_percentile(compose: dict[str, Any]):
    return add_depending_count(compose, int(os.getenv('GROUP_PERC_COUNT')), add_grouper, name='action-percentile', type=GrouperType.APP_ID_COUNT.value, queue=f"{os.getenv('GROUP_PERC')}", next_nodes=f"{os.getenv('JOIN_PERC')},{os.getenv('JOIN_PERC_COUNT')},{ShardingAttribute.APP_ID.value}")

def add_joiners_action_percentile(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_PERC_COUNT'))):
        compose, new_container = add_joiner(compose, name=f"action-percentile-{i}", type=JoinerType.PERCENTILE.value, queue=f"{os.getenv('JOIN_PERC')}", next_nodes=f"{os.getenv('CONS_SORT_PERC')}",node_id=i)
        containers.append(new_container)
    return compose, containers

def add_joiners_english_count(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_ENG_COUNT'))):
        compose, new_container = add_joiner_english_count(compose,'joiner-english-count', node_id=i)
        containers.append(new_container)
    return compose, containers

def add_sorters_avg_playtime(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('SORT_AVG_PT_COUNT'))):
        compose, new_container = add_sorter(compose, name=f'avg-playtime-{i}', type=SorterType.PLAYTIME.value,
                                             queue=f"{os.getenv('SORT_AVG_PT')}", next_nodes=f"{os.getenv('CONS_SORT_AVG_PT')}",node_id=i,node_count=f"{os.getenv('SORT_AVG_PT_COUNT')}", top=f"{os.getenv('SORT_AVG_PT_TOP')}")
        containers.append(new_container)
    return compose, containers

def add_sorters_indie(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('SORT_INDIE_COUNT'))):
        compose, new_container = add_sorter(compose, name=f'indie-positive-reviews-{i}', type=SorterType.INDIE.value, queue=f"{os.getenv('SORT_INDIE')}", next_nodes=f"{os.getenv('CONS_SORT_INDIE')}",node_id=i,node_count=f"{os.getenv('SORT_INDIE_COUNT')}", top=f"{os.getenv('SORT_INDIE_TOP')}")
        containers.append(new_container)
    return compose, containers

def add_sorter_consolidator_avg_playtime(compose: dict[str, Any]):
    return add_sorter_consolidator_top(compose, name=f'avg-playtime', type=SorterType.CONSOLIDATOR_PLAYTIME.value, queue=f"{os.getenv('CONS_SORT_AVG_PT')}", next_nodes=f"{os.getenv('DISP')}", prior_node_count=f"{os.getenv('SORT_AVG_PT_COUNT')}", top=f"{os.getenv('SORT_AVG_PT_TOP')}", query_number=2)

def add_sorter_consolidator_indie(compose: dict[str, Any]):
    return add_sorter_consolidator_top(compose, name=f'indie-top', type=SorterType.CONSOLIDATOR_INDIE.value, queue=f"{os.getenv('CONS_SORT_INDIE')}", next_nodes=f"{os.getenv('DISP')}", prior_node_count=f"{os.getenv('SORT_INDIE_COUNT')}", top=f"{os.getenv('SORT_INDIE_TOP')}", query_number=3)

def add_sorter_consolidator_action_percentile(compose: dict[str, Any]):
    return add_sorter_consolidator_percentile(compose, name=f'sorter-consolidator-action-percentile', type=SorterType.CONSOLIDATOR_PERCENTILE.value, queue=f"{os.getenv('CONS_SORT_PERC')}", next_nodes=f"{os.getenv('DISP')}", prior_node_count=f"{os.getenv('JOIN_PERC_COUNT')}", percentile=f"{os.getenv('CONS_PERC')}", query_number=5)

def add_joiners_indie(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_INDIE_COUNT'))):
        compose, new_container = add_joiner(compose, name=f'indie-positive-{i}', type=JoinerType.INDIE.value, queue=f"{os.getenv('JOIN_INDIE')}", next_nodes=f"{os.getenv('CONS_JOIN_INDIE')}",node_id=i)
        containers.append(new_container)
    return compose, containers


def add_joiner_action_english(compose: dict[str, Any]):
    containers = []
    for i in range(0, int(os.getenv('JOIN_ACT_COUNT'))):
        compose, new_container = add_joiner(compose, name=f'action-english-{i}', type=JoinerType.ENGLISH.value, queue=f"{os.getenv('JOIN_ACT')}", next_nodes=f"{os.getenv('FILT_ENG')}",node_id=i)
        containers.append(new_container)
    return compose, containers


def add_joiner_indie_consolidator(compose: dict[str, Any]):
    return add_joiner_consolidator(compose, name='joiner-indie', type=JoinerConsolidatorType.INDIE.value, 
                                   queue=f"{os.getenv('CONS_JOIN_INDIE')}", 
                                   next_nodes=f"{os.getenv('SORT_INDIE')},{os.getenv('SORT_INDIE_COUNT')},{ShardingAttribute.FRAGMENT_NUMBER.value}",
                                prior_node_count=int(os.getenv('JOIN_INDIE_COUNT')))

def add_joiner_english_consolidator(compose: dict[str, Any]):
    return add_joiner_consolidator(compose, name='joiner-english', type=JoinerConsolidatorType.ENGLISH.value, 
                                   queue=f"{os.getenv('CONS_JOIN_ENG')}", 
                                   next_nodes=f"{os.getenv('JOIN_ENG')},{os.getenv('JOIN_ENG_COUNT')},{ShardingAttribute.APP_ID.value}",
                                     prior_node_count=int(os.getenv('JOIN_ACT_COUNT')))

def add_joiner_stream_consolidator(compose: dict[str, Any]):
    return add_joiner_consolidator(compose, name='stream', type=JoinerConsolidatorType.STREAM.value, queue=f"{os.getenv('CONS_JOIN_STREAM')}", next_nodes=f"{os.getenv('DISP')}", prior_node_count=int(os.getenv('JOIN_ENG_COUNT')))

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
    compose = add_client(compose)

    #Network
    compose = add_network(compose)

    # Initializer
    compose, initializer_container = add_initializer(compose)
    
    containers = [initializer_container]

    # Query 1:
    compose, containers = add_container(compose, containers, generation=add_groupers_os_count)
    compose, containers = add_container(compose, containers, generation=add_joiner_os_count)

    # Query 2 :
    compose, containers = add_container(compose, containers, generation=add_filterers_indie)
    compose, containers = add_container(compose, containers, generation=add_filterers_date)
    compose, containers = add_container(compose, containers, generation=add_sorters_avg_playtime)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_avg_playtime)

    # Query 3
    compose, containers = add_container(compose, containers, generation=add_groupers_indie)
    compose, containers = add_container(compose, containers, generation=add_joiners_indie) 
    compose, containers = add_container(compose, containers, generation=add_joiner_indie_consolidator)
    compose, containers = add_container(compose, containers, generation=add_sorters_indie)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_indie)

    #Query 4
    compose, containers = add_container(compose, containers, generation=add_filterers_action)
    compose, containers = add_container(compose, containers, generation=add_joiner_action_english)
    compose, containers = add_container(compose, containers, generation=add_filterers_english)
    compose, containers = add_container(compose, containers, generation=add_groupers_action_english)
    compose, containers = add_container(compose, containers, generation=add_joiner_english_consolidator)
    compose, containers = add_container(compose, containers, generation=add_joiners_english_count)
    compose, containers = add_container(compose, containers, generation=add_joiner_stream_consolidator)

    # Query 5

    compose, containers = add_container(compose, containers, generation=add_groupers_action_percentile)
    compose, containers = add_container(compose, containers, generation=add_joiners_action_percentile)
    compose, containers = add_container(compose, containers, generation=add_sorter_consolidator_action_percentile)


    # Border Node
    compose = add_border_node(compose, cluster_nodes=containers)

    with open(output_file, 'w') as file:
        yaml.dump(compose, file,sort_keys=False, default_flow_style=False)


def main():
    try:
        generate_compose('docker-compose-test.yaml', 1)
    except ValueError:
        print(f"Error: second argument has to be a number (amount of clients desired)")

if __name__ == '__main__':
    main()
