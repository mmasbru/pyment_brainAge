import os as os
import math as math
import csv as csv
import yaml as yaml

config='config.yaml'

with open(config) as y_file:
    proj_parameters = yaml.safe_load(y_file)

y_file.close()

nodeSize = proj_parameters['nodeSize']
nCoresPerTask = proj_parameters['nCoresPerTask']

iFile = proj_parameters['slurmDataFile'] 

oFile = iFile.replace('.data', '.array.data')

csvFile = open(iFile, 'r')
csvData = csv.reader(csvFile, delimiter=' ')

data = []
for line in csvData:
    data.append(line)

csvFile.close()
   
nTasks = len(data)
nTasksPerNode = math.ceil(nodeSize/nCoresPerTask)
nArrays = math.ceil(nTasks/nTasksPerNode)

if 'nTasksPerNode' not in proj_parameters:
    proj_parameters['nTasksPerNode'] = nTasksPerNode

if 'nArrays' not in proj_parameters:
    proj_parameters['nArrays'] = nArrays

with open(config, 'w') as y_file:
    yaml.dump(proj_parameters, y_file, explicit_start=True, default_flow_style=False)

y_file.close()

nTasksAdded=0

oData = []
while nTasksAdded < nTasks:
    for i in range(1, nArrays+1):
        for j in range(1, nTasksPerNode+1):
            try:
                tmpdata = data[nTasksAdded]
            except:
                print('array is out of data..')
                print(i,j)
                break
            tmpdata.insert(0, 'A'+str(i) + '_J'+str(j))
            oData.append(tmpdata)
            nTasksAdded+=1
            
oFile = open(oFile, 'w', newline='')
csvWriter = csv.writer(oFile, delimiter = ' ', lineterminator='\n')
csvWriter.writerows(oData)
oFile.close()
