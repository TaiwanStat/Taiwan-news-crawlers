"""
check if any empty columns in result data of crawlers
Usage: python check_crwal_works.py <directory of data folder>
"""
import json
import glob
import sys

def read_json(filename):
    with open(filename) as data_file:
        return json.load(data_file)

def main(directory):
    folder_dir = glob.glob("{}/*.json".format(directory))
    result = {}
    columns = ['category', 'content', 'website', 'date', 'url', 'title']
    for filename in folder_dir:
        try:
            crawl_data = read_json(filename)
        except:
            print('Cannot load file: '+filename)
            continue
        result[filename] = {}
        for news in crawl_data:
            category = news['category']
            for key, value in news.items():
                if not value:
                    if category in result[filename]:
                        result[filename][category][key] += 1
                    else:
                        result[filename][category] = {}
                        for c in columns:
                            result[filename][category][c] = 0
        # pprint(result)

    for fname, fvalue in result.items():
        # pprint(fvalue)
        for catename, catevalue in fvalue.items():
            for colname, colvalue in catevalue.items():
                if colvalue != 0:
                    print(fname + ',' + catename + ':' + str(colvalue))

    with open('crawl_work_log.json', 'w', encoding='utf-8') as outfile:
        json.dump(result, outfile)

if __name__ == '__main__':
    data_folder_dir = sys.argv[1]
    main(data_folder_dir)
