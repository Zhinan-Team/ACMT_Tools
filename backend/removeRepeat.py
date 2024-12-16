import json

# 打开 JSON 文件
with open('8293.json', 'rb') as f:
    json_Data = json.load(f)

# 初始化计数器
missing_count = 0

# 遍历 JSON 数组
print(len(json_Data))
RESULT=[]
validateKeyMessageValue ={}
for item in json_Data:
    if "MessageIndex" in  item["Data"] and "ValidationTargetIndex" in item["Data"] :
         validateKeyMessageValue[item["Data"]["ValidationTargetIndex"]] = item["Data"]["MessageIndex"]
     
print(len(validateKeyMessageValue))

for item in json_Data:
    if "ValidationTargetIndex" in item["Data"] and item["Tag"]=="ParameterV" and item["Index"] in validateKeyMessageValue :
         
         validateKeyMessageValue[item["Data"]["ValidationTargetIndex"]] = validateKeyMessageValue[item["Index"]]
print(len(validateKeyMessageValue))

# 有一些重复找的
res_set = set()
 

for item in json_Data:
    if item["Tag"]=="ParameterV":
        if item["Index"] in validateKeyMessageValue:
             item["Tag"] = "Parameter"
             item["Data"]["MessageIndex"]  = validateKeyMessageValue[item["Index"]]
             if item["Index"] not in res_set:
                RESULT.append(item)
                res_set.add(item["Index"])
    else:
      if item["Index"] not in res_set:
        RESULT.append(item)
        res_set.add(item["Index"])
print(len(RESULT))

newIdCount = 1
newIdMap ={}
for item in RESULT:
    newIdMap[item["Index"]] = newIdCount
    newIdCount = newIdCount+1
# 递归替换id
# 递归函数，用于替换 JSON 对象中所有键为 "Index" 的值
def replace_index(obj, newIdMap):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "Index":  # 修改判断条件为 "Index"
                obj[key] = newIdMap.get(value, value)
            else:
                replace_index(value, newIdMap)
    elif isinstance(obj, list):
        for item in obj:
            replace_index(item, newIdMap)

def replace_double_quotes(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) or isinstance(value, list):
                data[key] = replace_double_quotes(value)
            elif isinstance(value, str):
                data[key] = value.replace('\"', "^")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict) or isinstance(item, list):
                data[i] = replace_double_quotes(item)
            elif isinstance(item, str):
                data[i] = item.replace('\"', "^")
    return data




for item in RESULT:
    if "MessageIndex" in item["Data"]:
        item["Data"]["MessageIndex"] = newIdMap[item["Data"]["MessageIndex"]]
    if "ValidationTargetIndex" in item["Data"]:
        item["Data"]["ValidationTargetIndex"] = newIdMap[item["Data"]["ValidationTargetIndex"]]
    if "FailureMessage" in item["Data"]:
        item["Data"]["FailureMessage"] = item["Data"]["FailureMessage"].replace('\"', "^")
    if "MaintenanceText" in item["Data"]:
         item["Data"]["MaintenanceText"] = item["Data"]["MaintenanceText"].replace('\"', "^")
    if "Preconditions" in item["Data"]: 
         item["Data"]["Preconditions"] = [precondition.replace('\"', "^") for precondition in item["Data"]["Preconditions"]]
    if "Screens" in item["Data"]:
          item = replace_double_quotes(item)
   
replace_index(RESULT, newIdMap)


def remove_quotes_around_values(json_data):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, str):
                # Try converting to boolean
                if value.lower() == "true":
                    json_data[key] = True
                elif value.lower() == "false":
                    json_data[key] = False
                else:
                    try:
                        # Try converting to integer first
                        json_data[key] = int(value)
                    except ValueError:
                        try:
                            # Try converting to float next
                            json_data[key] = float(value)
                        except ValueError:
                            # If it's not numeric, leave it as it is
                            pass
            elif isinstance(value, (dict, list)):
                json_data[key] = remove_quotes_around_values(value)
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            json_data[i] = remove_quotes_around_values(item)
    return json_data

RESULT = remove_quotes_around_values(RESULT)

with open("8294.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(RESULT,ensure_ascii=False,indent=4))
    
