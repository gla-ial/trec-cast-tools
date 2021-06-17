# Version 1.0
# Python 3.6
# Install tqdm for tracking progress

from tqdm import tqdm
import json
import sys
import os
import io
import codecs
from src.helpers import convert_to_trecweb
from src.PassageChunker import RegexPassageChunker, SpacyPassageChunker

def parse_sim_file(filename):
    """
    Reads the deduplicated documents file and stores the 
    duplicate passage ids into a dictionary
    """

    sim_dict = {}
    lines = open(filename).readlines()
    for line in lines:
        data = line.strip().split(':')
        if len(data[1]) > 0:
            sim_docs = data[-1].split(',')
            for docs in sim_docs:
                sim_dict[docs] = 1
                
    print("There are {} duplicates".format(len(sim_dict)))
    return sim_dict


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("USAGE: python3 marco_trecweb.py path_to_collection.tsv path_of_dumpdir duplicates_file")
        exit(0)
    
    marco_file = sys.argv[1]
    dump_dir = sys.argv[2]
    sim_file = sys.argv[3]

    # Create the directory (for dumping files) if it doesn't exists
    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)

    print("Loading similarity file.")
    sim_dict = parse_sim_file(sim_file)

    input_file = os.path.basename(marco_file)

    print("Starting processing.")
    print("Output directory: " + dump_dir)
    dumper_file = os.path.join(dump_dir, input_file + '.xml')
    print("Writing output to: " + dumper_file)
    fp = codecs.open(dumper_file, 'w', 'utf-8')

    # Read the ranking collections file
    with io.open(marco_file, "r", encoding="utf-8") as input:

        for line in tqdm(input, total=3213835):
            
            try:
                idx, url, title, text = line.strip().split('\t')
                
                # if the id is a duplicate, don't add it
                if idx in sim_dict:
                    continue
                
                
                idx = 'MARCO_' + str(idx)
                # Create a trecweb entry for a passage
                passageChunker = RegexPassageChunker(idx, title, text, url)
                passages = passageChunker.create_passages()
                
                for passage in passages:
                    trecweb_passage = convert_to_trecweb(passage['id'], passage['title'], passage['body'], passage['url'])
                    fp.write(trecweb_passage)
            except:
                #either idx, url, title, or body is missing
                continue

    input.close()
    fp.close()