import json
import csv
from io import StringIO
 
 
def json_to_csv(data):
    # Opening JSON file and loading the data
    # into the variable data
    
    json_data=[]
    if(type(data) is json):
        json_data=data
    elif(type(data) is str):
        json_data=json.loads(data)
    else:
        json_data = json.loads(json.dumps(data))
    # now we will open a file for writing
    csv_out = StringIO("")
    
    # create the csv writer object
    csv_writer = csv.writer(csv_out)
    
    # Counter variable used for writing
    # headers to the CSV file
    count = 0
    
    for e in json_data:
        if count == 0:
    
            # Writing headers of CSV file
            header = e.keys()
            csv_writer.writerow(header)
            count += 1
    
        # Writing data of CSV file
        csv_writer.writerow(e.values())
    csv_out.seek(0)
    return csv_out.read()

if __name__=="__main__":
    with open('hack22.json') as f:
        j = json.load(f)['data']
        print(type(j))
        print(json_to_csv(j))