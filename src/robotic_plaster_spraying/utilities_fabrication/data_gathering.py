import os
import json
import csv

def ReadDictFromJson(filename):
    with open(filename, 'r') as f:
        output = json.load(f)
    return output

def WriteDictToJson(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)

def WriteDictToCsv(filename, data, header):
    with open(filename, 'wb') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

def remapValues(values, targetMin, targetMax):

    """ Remap numbers into a numeric domain """

    if len(set(values)) >1:

        remappedValues = []

        # Get source domain min and max
        scrMin = min(values)
        scrMax = max(values)

        # Iterate the values and remap
        for v in values:
            rv = ((v-scrMin)/(scrMax-scrMin))*(targetMax-targetMin)+targetMin
            remappedValues.append(rv)

        return remappedValues

    # Else return targeMax for each value
    else:
        return [targetMax]*len(values)