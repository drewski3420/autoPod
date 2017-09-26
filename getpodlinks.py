import json
import ast
file = 'configs/pods.json'

with open(file,'r') as fn:
    data = fn.read()

data_dict = ast.literal_eval(data)
result = {}
i = 0
for key,value in data_dict.items():
    temp_dict = {}
    temp_dict['pod_name'] = key
    temp_dict['pod_url'] = value
    result[i] = temp_dict
    i += 1
    

j = json.dumps(result,indent=4)

with open('configs/pods2.json','w+') as f:
    f.write(j)
