# author: mohammad sadegh habibian (msh.habibian@gmail.com)

from pathlib import Path
import xml.etree.ElementTree as ET
import pysolr
import time
from decorators import record_time


@record_time
def get_standard_query(query: str, title_weight, body_weight):
    if isinstance(query, str):
        splited_query = query.split()
    else: 
        # query is a list of words already
        splited_query = query
    title_query = ' '.join(list(map(lambda x: 'TITLE:' + x, splited_query)))
    body_query = ' '.join(list(map(lambda x: 'BODY:' + x, splited_query)))
    standard_query = f'({title_query})^{title_weight} OR ({body_query})^{body_weight}'
    return standard_query

@record_time
def search_solr(standard_query: str, solr, rows):
    res = solr.search(standard_query, **{
    # 'fq':query,
    'rows':rows,
    'q.op':'AND',
    'fl':'DOCID,score',
    })
    return res.docs

@record_time
def extract_query(file):
    # parse a query file (xml)
    tree = ET.parse(file)
    root = tree.getroot()
    # extract query phrase list, ex: ['w1', 'w2', 'w3']
    query = []
    for t in root.find('terminfo').findall('term'):
        query.append(t.find('word').text)
    return query

@record_time
def extract_query_expected_results(file):
    # parse a query file (xml)
    tree = ET.parse(file)
    root = tree.getroot()

    related_docids = []
    unrelated_docids = []
    for d in root.find('docinfo').findall('doc'):
        docid = int(d.find('docid').text)
        label = int(d.find('label').text)
        if label == 0:
            unrelated_docids.append(docid)
        elif label > 0:
            related_docids.append(docid)

    return related_docids, unrelated_docids

@record_time
def calculate_accuracy(solr_results, file):
    res, exec_time = extract_query_expected_results(file)
    related_docids, unrelated_docids = res[0], res[1]
    print('len related: ', len(related_docids))
    print('len unrelated: ', len(unrelated_docids))
    
    related_solr_results = 0
    checked_solr_results = 0
    accuracy = {}
    for index, res in enumerate(solr_results):
        if res['DOCID'] in related_docids:
            related_solr_results += 1
            checked_solr_results += 1
        elif res['DOCID'] in unrelated_docids:
            checked_solr_results += 1
        else:
            # cant compare, ignore this case
            pass
        if index == 0:
            accuracy['p@1'] = related_solr_results / (index + 1)
        elif index == 4:
            accuracy['p@5'] = related_solr_results / (index + 1)
        elif index == 9:
            accuracy['p@10'] = related_solr_results / (index + 1)
        elif index == 19:
            accuracy['p@20'] = related_solr_results / (index + 1)
        elif index == 49:
            accuracy['p@50'] = related_solr_results / (index + 1)
        elif index == 99:
            accuracy['p@100'] = related_solr_results / (index + 1)
            break
    
    # accuracy[f'p@{checked_solr_results}'] = related_solr_results / (index + 1)
    print('number of solr results: ', len(solr_results))
    return accuracy

@record_time
def strict_calculate_accuracy(solr_results, file):
    # if solr result was not in related or unrelated dont count it for accuracy
    res, exec_time = extract_query_expected_results(file)
    related_docids, unrelated_docids = res[0], res[1]
    print('len related: ', len(related_docids))
    print('len unrelated: ', len(unrelated_docids))
    
    related_solr_results = 0
    checked_solr_results = 0
    accuracy = {}
    for index, res in enumerate(solr_results):
        if res['DOCID'] in related_docids:
            related_solr_results += 1
            checked_solr_results += 1
        elif res['DOCID'] in unrelated_docids:
            checked_solr_results += 1
        else:
            # cant compare, ignore this case
            pass
        if checked_solr_results == 1:
            accuracy['p@1'] = related_solr_results / checked_solr_results
        elif checked_solr_results == 5:
            accuracy['p@5'] = related_solr_results / checked_solr_results
        elif checked_solr_results == 10:
            accuracy['p@10'] = related_solr_results / checked_solr_results
        elif checked_solr_results == 20:
            accuracy['p@20'] = related_solr_results / checked_solr_results
        elif checked_solr_results == 50:
            accuracy['p@50'] = related_solr_results / checked_solr_results
        elif checked_solr_results == 100:
            accuracy['p@100'] = related_solr_results / checked_solr_results
            break
    if 0 < checked_solr_results < 100:
        accuracy[f'p@{checked_solr_results}'] = related_solr_results / checked_solr_results
    print('number of solr results: ', len(solr_results))
    return accuracy

        


if __name__ == '__main__':
    GLOBAL_START_TIME = time.time()
    # query exec time statistics
    FIRST_QUERY_TIMES = 0
    SECOND_QUERY_TIMES = 0
    QUERIES_COUNT = 50
    # accuracy statistics
    ACCURACY_STATISTICS = dict()

    # define main parts
    query_files = list(Path('./queries/').rglob('query-*.xml'))
    print(len(query_files)) # >> 52 > remove 2...
    solr = pysolr.Solr('http://127.0.0.1:8983/solr/IR_core/', always_commit=False)
    # print (search_solr(get_standard_query('قاچاق گوشي تلفن همراه'), solr)[0:5])
    for index, file in enumerate(query_files):
        print(f'************ running query of file {file.name} **************')
        # extract list of query words from file
        query_list, exec_time = extract_query(file)
        # render query list to needed solr query
        standard_query = get_standard_query(query_list, title_weight=1, body_weight=1)

        # search in solr two times and record each exec duration
        print('first time:')
        solr_results, first_exec_time = search_solr(standard_query, solr=solr, rows=30000)
        print('second time:')
        solr_results , second_exec_time = search_solr(standard_query, solr=solr, rows=30000)
        print('NUMBER OF RESULTS: ', len(solr_results))
        # for statistics ...
        FIRST_QUERY_TIMES += first_exec_time
        SECOND_QUERY_TIMES += second_exec_time

        # calculate Accuracy
        accuracy, exec_time = strict_calculate_accuracy(solr_results, file)
        # accuracy, exec_time = calculate_accuracy(solr_results, file)
        print(accuracy)

        # add accuracy data for later statistics analysis
        for key in accuracy.keys():
            if not ACCURACY_STATISTICS.get(key):
                d = {
                    'sum': accuracy[key],
                    'count': 1
                }
                ACCURACY_STATISTICS[key] = d

            else:
                ACCURACY_STATISTICS[key]['sum'] += accuracy[key]
                ACCURACY_STATISTICS[key]['count'] += 1
        
        # if index == 6:
        #     break
    print('################# statistics ##############')
    first_avg = FIRST_QUERY_TIMES / QUERIES_COUNT
    second_avg = SECOND_QUERY_TIMES / QUERIES_COUNT
    print('Average First Query Time: ', first_avg) # 0.054198174476623534
    print('Average Second Query Time: ', second_avg) # 0.006664748191833496

    ut = (1 - (second_avg / first_avg)) * 100
    print('utilization percentage: ', ut) # 87.70300244206915

    print('Accuracy statistics:')
    for key in ACCURACY_STATISTICS:
        print('%s: { count: %s, percentage: %s }' %(key, ACCURACY_STATISTICS[key]['count'], ACCURACY_STATISTICS[key]['sum'] / ACCURACY_STATISTICS[key]['count']))
    print('TOTAL EXECUTION TIME FOR ALL QUERIES: ', time.time() - GLOBAL_START_TIME)

    





