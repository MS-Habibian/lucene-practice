# author: mohammad sadegh habibian (msh.habibian@gmail.com)

from pathlib import Path
import xml.etree.ElementTree as ET
import pysolr
import time


# define main parts
attrs = ['DOCID', 'URL', 'TITLE', 'BODY']
input_files = list(Path('./input/').rglob('*.xml'))
# print(len(input_files)) # >> 462


solr = pysolr.Solr('http://127.0.0.1:8983/solr/IR_core/', timeout = 300, always_commit=False)


global_start_time = time.time()
# parse docs of all input files 
json_docs = []
for index, file in enumerate(input_files):
    start_reading_time = time.time()
    print(f'### start parsing file <{index}>  of 462')
    tree = ET.parse(file)
    root = tree.getroot()
    # print('number of docs in this file:', len(root))
    start_parsing_time = time.time()
    for doc in root:
        d = {}
        for attr in attrs:
            d[attr] = doc.find(attr).text
        json_docs.append(d)
    print('time to convert docs to json: ', time.time() - start_parsing_time)
    
    if index != 0 and index % 7 == 0:
        start_solr_add_time = time.time()
        solr.add(json_docs)
        print('##### time to add 7 files to solr: ', time.time() - start_solr_add_time)
        json_docs = []



if json_docs:
    start_solr_add_time = time.time()
    solr.add(json_docs)
    print('##### time to add last files to solr: ', time.time() - start_solr_add_time)
    json_docs = []
start_commit_time = time.time()
solr.commit()
print('commit time: ', time.time() - start_commit_time)

print('################# parsing finished....\n')
exec_time = time.time() - global_start_time
print( 'total execution time: ', exec_time) # first time: 4583.11248421669
print('minutes: %s, seconds: %s' %(int(exec_time) // 60, int(exec_time % 60))) # first time: minutes: 76, seconds: 23