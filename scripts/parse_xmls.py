# author: mohammad sadegh habibian (msh.habibian@gmail.com)

from pathlib import Path
import xml.etree.ElementTree as ET
import pysolr
import time


# define main parts
attrs = ['DOCID', 'URL', 'TITLE', 'BODY']
input_files = list(Path('./input/').rglob('*.xml'))
# print(len(input_files)) # >> 462

seen_docs = set() # set of doc_ids of pages
repeated_docs_count = 0

solr = pysolr.Solr('http://127.0.0.1:8983/solr/IR_core/', always_commit=False)


global_start_time = time.time()
# parse docs of all input files 
for index, file in enumerate(input_files):
    start_reading_time = time.time()
    print(f'### start parsing file <{index}>  of 462')
    tree = ET.parse(file)
    root = tree.getroot()
    # print(f'time of parsing xml file <{index}>', time.time() - start_reading_time)
    # print('number of docs in this file:', len(root))

    start_parsing_time = time.time()
    file_docs = []
    for doc in root:
        # check if dock is not checked before
        d = {}
        for attr in attrs:
            d[attr] = doc.find(attr).text
            # print(doc.find(attr).text)

        # # check not repeated
        # if d['DOCID'] in seen_docs:
        #     repeated_docs_count += 1
        #     continue
        # seen_docs.add(d['DOCID'])

        file_docs.append(d)

    solr.add(file_docs)
    # solr.delete(q='*')
    print('time to convert docs to json and add to solr: ', time.time() - start_parsing_time)

    # start_commit_time = time.time()
    # solr.commit()
    # print('commit time for this file: ', time.time() - start_commit_time)
    # print(f'total time for parsing and indexing file {index} : ', time.time() - start_reading_time)


    # print('checked docs: ', len(seen_docs))
    # print('number of repeated docs: ', repeated_docs_count)
    # exec_time  = time.time() - start_time
    # print('exec time: ', exec_time)
    # if index == 20:
    #     break
start_commit_time = time.time()
solr.commit()
print('commit time: ', time.time() - start_commit_time)

print('################# parsing finished....\n')
print('number of repeated docs: ', repeated_docs_count)
exec_time = time.time() - global_start_time
print( 'total execution time: ', exec_time) # first time: 4583.11248421669
print('minutes: %s, seconds: %s' %(int(exec_time) // 60, int(exec_time % 60))) # first time: minutes: 76, seconds: 23