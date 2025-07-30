import json

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as fp:
        s = fp.read()
        data = json.loads(s)
    return data

def load_jsonl(url):
    data = []
    with open(url, 'r', encoding='utf-8') as f:
        for i in f:
            json_data = json.loads(i)
            data.append(json_data)
    return data

def write_json(data, file_path):
    output = json.dumps(data, indent=4, ensure_ascii=False)
    with open(file_path, "w+", encoding="utf-8") as file:
        file.write(output)
    return True
