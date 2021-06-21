  
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
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
from .models import tests_to_run
import csv
from os import walk
import yaml
from django.template.response import TemplateResponse

def upload_tests(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['tests_csv']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        delete_everything()
        load_tests()
        return render(request, 'main/upload.html')
    else:
        # form = UploadFileForm()
        load_tests()
    return render(request, 'main/upload.html', {'form': form})

def load_tests():
    mypath = '/source/nautobatfishbot/network_tests'
    # mypath = 'C:\\Users\\dhime\\Downloads\\Install\\image'
    files = []
    all_tests = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        files.extend(filenames)
        break
    for file in files:
        file = os.path.join(mypath, file)
        with open(file) as fd:
            tests = yaml.safe_load(fd)
        for test in tests:
            all_tests.append(test)
    return all_tests
        # test, created = tests_to_run.objects.update_or_create(
        #     name=test['test_name'],
        #     defaults={'dest_ip':test['dest_ip'],
        #     'dest_port':test['dest_port'],
        #     'source_ip':test['source_ip'],
        #     'source_port':test['source_port'],            
        #     })
    # job_result.log(
    #         "Successfully created/updated animal",
    #         obj=animal_record,
    #         level_choice=LogLevelChoices.LOG_SUCCESS,
    #         grouping="animals",
    #     )
        



def delete_everything():
    tests_to_run.objects.all().delete()

# def load_tests():
#     path = '/opt/nautobot/media/test.csv'
#     with open(path) as f:
#         reader = csv.reader(f)
#         for row in reader:
#             to_skip=False
#             for cell in row:
#                 if 'ip' in cell:
#                     to_skip = True
#             if to_skip == True:
#                 continue
#             _, created = tests_to_run.objects.get_or_create(
#                 test_name=row[0],
#                 source_ip=row[1],
#                 source_port=row[2],
#                 dest_ip=row[3],
#                 dest_port=row[4],
#                 )

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
    port_tests= load_tests()
    results = test_port_flows(port_tests)
    for result in results:
        data = result.to_json()
        data = json.loads(data)
        all_output = all_output + pprint_reachability(result)
    print ('\n\n\n\n\n\n')
    print (all_output)
    
    print ('\n\n\n\n\n\n')
    pprint (HttpResponse("BUG"))
    # return HttpResponse(all_output)
    print ('\n\n\n\n\n\n')
    # return HttpResponse("Working")
    return return_tests_data(requset, template_name='main/home.html', all_output)
    # return render(request, 'main/home.html')

def return_tests_data(requset, template_name='main/home.html', all_output):
    args = {}
    text = all_output
    args['mytext'] = text
    return TemplateResponse(request, template_name, args)

def pprint_reachability(answer):
    output = "<h3>Test Name: "+  answer['test_name'].values[0]+'</h3>'
    output = output + f"Flow Summary<br>"
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


# port_tests = [
#     {'src_ip': '172.16.1.1',
#      'dst_ip': '172.19.0.12',
#      'start_device': 'office_switch',
#      'dst_port': '23'},
#     {'src_ip': '172.16.1.1',
#      'dst_ip': '172.19.0.12',
#      'start_device': 'office_switch',
#      'dst_port': '22'},
# ]


def test_port_flows(port_tests):
    all_results = []
    # port_tests= load_tests()
    for test in port_tests:
        results = port_flow_validation(bfq, test['source_ip'],
                                       test['dest_ip'], test['start_device'], test['dest_port'])
        results['test_name']=test['test_name']
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

