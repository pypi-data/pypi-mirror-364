import json
import numpy as np
def camera_inverse_files(input_path, output_path):
    with open(input_path,'r',encoding='utf8')as fp:
        s = fp.read()
        data = json.loads(s)

    total = 0
    for i in data:
        A = np.array(i["extrinsic"])
        A_inv = np.linalg.inv(A)
        output = []
        t = 0
        for j in A_inv:
            output.append([])
            for k in j:
                output[t].append(float(k))
            t += 1
        
        data[total]['extrinsic'] = output
        total += 1

    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    with open(output_path, "w+", encoding="utf-8") as file:
        file.write(json_str)

def camera_inverse_str(input_str):
    data = input_str

    total = 0
    for i in data:
        A = np.array(i["extrinsic"])
        A_inv = np.linalg.inv(A)
        output = []
        t = 0
        for j in A_inv:
            output.append([])
            for k in j:
                output[t].append(float(k))
            t += 1
        
        data[total]['extrinsic'] = output
        total += 1

    return data
                