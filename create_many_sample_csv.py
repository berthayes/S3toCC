import csv
import random
import time

urls = 'shorter_urls.txt'


# create a urls[] array
with open(urls, 'rt') as urls:
    url_list = []
    for line in urls:
        line = line.strip()
        url_list.append(line)
urls.close()

fields = ['timestamp', 'url']

for i in range(100):
    file_name = 'data-' + str(time.time()) + '.csv'
    with open(file_name, 'w') as csv_out:
        csvwriter = csv.writer(csv_out)
        csvwriter.writerow(fields)
        for i in range(20):
            url = random.choice(url_list)
            now_millis = (time.time())
            row = [now_millis, url]
            csvwriter.writerow(row)
#        time.sleep(.5)

