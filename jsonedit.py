import json
import re

# 读取数据
with open('blank.json', 'r', encoding = 'utf-8') as f:
    data_n9e = json.load(f)
with open('grafana.json', 'r', encoding = 'utf-8') as f:
    data = json.load(f)
    sum = 0
    sum2 = 0
    k = 0
    l = 0
    # list1 = []
    for i in range(len(data["panels"])):
        if data["panels"][i]["datasource"]:
            x = (k%4)*6
            y = int(k/4)*2
            k = k + 1
            print("title:\n", data["panels"][k]["title"])
            print("promql:")
            print(x,y)
            dict1 = {"id": 0, "group_id": 5,
                     "configs": "{\"name\":\"1\",\"mode\":\"prometheus\",\"prome_ql\":[\"123\"],\"layout\":{\"h\":2,\"w\":6,\"x\":12,\"y\":2,\"i\":\"6\"}}",
                     "weight": 0}
            dict2 = eval(dict1["configs"])
            dict1["id"] = i
            dict2["name"] = data["panels"][i]["title"]
            dict2["layout"]["x"] = x
            dict2["layout"]["y"] = y
            dict2["layout"]["i"] = i
            # print("12312321312312321312312123:", dict1)
            sum2 = sum2 + 1
            # list1.append(dict1)
            # print("1111111111111111111111111111", list1)
            list_prome_ql = []
            for j in range(len(data["panels"][i]["targets"])):
                try:
                    print(data["panels"][i]["targets"][j]["expr"])
                    print(re.sub('\{.*?\}', '', data["panels"][i]["targets"][j]["expr"]))
                    print(re.sub("podname", "pod_name", data["panels"][i]["targets"][j]["expr"]))
                    print(re.sub("\"", "\\"+"\"", data["panels"][i]["targets"][j]["expr"]))
                    # dict2["prome_ql"] = [data["panels"][i]["targets"][j]["expr"]]
                    dict2["prome_ql"] = re.sub("podname", "pod_name", data["panels"][i]["targets"][j]["expr"])
                    str_dict2 = re.sub("\"", "\\"+"\"", dict2["prome_ql"])
                    str_dict2 = re.sub("\$__interval", "2m", str_dict2)
                    # list_prome_ql = []
                    list_prome_ql.append(str_dict2)
                    print("list_prome_ql.append(str_dict2):_________", list_prome_ql)
                    dict2["prome_ql"] = list_prome_ql
                    sum = sum + 1
                    print("123123h12ehjhjddisdfiaifuhsdfibadsbfiuadsf", j)
                except:
                    pass

            dict1["configs"] = str(dict2)
            dict1["configs"] = re.sub("'", "\"", dict1["configs"])
            print("dict1", dict1)
            data_n9e[0]["chart_groups"][l]["charts"].append(dict1)
        else:
            dict3 = {"id": l, "dashboard_id": 0, "name": data["panels"][i]["title"], "weight": 0, "charts": []}
            data_n9e[0]["chart_groups"].append(dict3)
            l = l+1
    print("sum", sum)
    print("sum2", sum2)
    print("data_n9e", data_n9e)
    print(data_n9e[0]["chart_groups"][0]["charts"])

# 写入 JSON 数据
with open('n9e.json', 'w', encoding ='utf-8') as f:
    json.dump(data_n9e, f, ensure_ascii=False, indent = 4)