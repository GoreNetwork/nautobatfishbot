  
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq
from pprint import pprint
import json
import getpass
import os

# Ugly, clean this up!!
def nautobatfishbot(request):
    print (os.system('ls /source/nautobatfishbot/snapshots/lab/'))
    bf_session.host = "batfish"
    network_name = 'lab'
    print ("set network name var")
    snapshot_path = '/source/nautobatfishbot/snapshots/lab/'
    print (snapshot_path)
    bf_set_network(network_name)
    bf_session.init_snapshot(snapshot_path, name=network_name, overwrite=True)
    load_questions()
    # pprint(bfq.parseWarning().answer().frame())
    pprint(bfq.bgpSessionCompatibility().answer().frame())

    print(bfq.ipOwners(duplicatesOnly=True).answer().frame())
    all_output = ''
    results = test_port_flows(port_tests)
    for result in results:
        data = result.to_json()
        data = json.loads(data)
        all_output = all_output + pprint_reachability(result)
    print ('\n\n\n\n\n\n')
    print (all_output)
    
    print ('\n\n\n\n\n\n')
    pprint (HttpResponse("BUG"))
    return HttpResponse(all_output)
    print ('\n\n\n\n\n\n')
    return HttpResponse("Working")

def pprint_reachability(answer):
    output = f"Flow Summary<br>"
    # print(f"Flow Summary")
    for index, row in answer.iterrows():
        output = output+f"Flow: {row['Flow']} (Trace Count:{row['TraceCount']})<br>"
        output = output+'===========<br>'
        # print(f"Flow: {row['Flow']} (Trace Count:{row['TraceCount']})")
    # print("==========")
    for index, row in answer.iterrows():
        output = output+f"Flow: {row['Flow']} (Trace Count:{row['TraceCount']})<br>"
        # print(f"Flow: {row['Flow']} (Trace Count:{row['TraceCount']})")
        for count, trace in enumerate(row["Traces"], start=1):
            output = output+f"<br>Trace #{count}<br>{trace}<br>"
            # print(f"\nTrace #{count}")
            # print(f"{trace}")
        output = output+"----<br>"
        # print("----")
    return output

def port_flow_validation(bfq, src_ip, dst_ip, start_device, dst_port,  end_dev=""):
    pprint(src_ip)
    return bfq.reachability(
        pathConstraints=PathConstraints(
            startLocation=start_device, endLocation=end_dev),
        headers=HeaderConstraints(
            srcIps=src_ip, dstIps=dst_ip, dstPorts=dst_port,
            ipProtocols=[
                # "UDP",
                "TCP"
            ]),
        actions="SUCCESS,FAILURE"
    ).answer().frame()


port_tests = [
    {'src_ip': '172.16.1.1',
     'dst_ip': '172.19.0.12',
     'start_device': 'office_switch',
     'dst_port': '23'},
    {'src_ip': '172.16.1.1',
     'dst_ip': '172.19.0.12',
     'start_device': 'office_switch',
     'dst_port': '22'},
]


def test_port_flows(port_tests):
    all_results = []
    for test in port_tests:
        results = port_flow_validation(bfq, test['src_ip'],
                                       test['dst_ip'], test['start_device'], test['dst_port'])
        # pprint(dir(results))
        # pprint(results.dict())
        # pprint(results.dict()['status'])
        all_results.append(results)
        # pickle_data(results, 'pickle_data.pickle')
        # json_data = results.to_json()
        # json1_data = json.loads(json_data)
        # pprint(json1_data)
    return all_results

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

