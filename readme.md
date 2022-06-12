## run scripts/parse_xmls.py to read xml files and inserts its data to solr

## set scoring algorithm in `/data/IR_core/conf/managed-schema.xml` file inside solr container( it is mounted in `./data/data/IR_core/conf/managed-schema.xml`)
    - <similarity class="org.apache.lucene.search.similarities.BM25Similarity" />
    - <similarity class="org.apache.lucene.search.similarities.ClassicSimilarity" />
    - reload IR_CORE in solr admin, after any change.

# TODO:

    - write script to read Query Files, run each query
    - compare results of solr with query file.
    - calculate @n accuracy for n in 1,5,10,20,100 ??
    - 
    - index all input files / time...
    - redo all steps above
    