import os
import re
import json
import copy

def process(key_out_name, data_in, panel):
    panel[key_out_name] = data_in
    panel_copy = copy.deepcopy(panel)
    # list_out.append(panel_copy)
    return panel_copy

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dir_grafana = "./grafana"
    files = os.listdir(dir_grafana)
    list_data_grafana = []
    for file in files:
        # print(file)
        with open(dir_grafana + "/" + file, 'r', encoding='utf-8') as f:
            data_grafana = json.load(f)
            list_data_grafana.append(data_grafana)
            print(data_grafana)
        print(list_data_grafana)

    list_n9ev5_done = []
    with open("./n9ev5tpl.json", 'r', encoding='utf-8') as f:
        data_n9ev5 = json.load(f)
        data_n9ev5_tpl = data_n9ev5[0]
        print(data_n9ev5_tpl)
        for i in list_data_grafana:
            print("\033[1;35m file: \033[0m", i["title"])
            data_n9ev5_done = process("name", i["title"], data_n9ev5_tpl)
            list_configs_in = []
            for j in i["templating"]["list"]:
                # print(j)
                if j["name"] == "interval":
                    pass
                else:
                    if type(j["current"]["value"]) == str:
                        value_in = j["current"]["value"]
                    elif type(j["current"]["value"]) == list:
                        value_in = j["current"]["value"][0]
                    if type(j["query"]) == str:
                        configs_in = {"name": j["name"], "selected": re.sub("\$__", "", value_in), "definition": j["query"], "multi": False, "reg": "", "allOption": False}
                        # print("str")
                    else:
                        configs_in = {"name": j["name"], "selected": re.sub("\$__", "", value_in), "definition": j["query"]["query"], "multi": False, "reg": "", "allOption": False}
                    list_configs_in.append(configs_in)
            dict_configs_in = {"var": list_configs_in}
            str_configs_in = json.dumps(dict_configs_in)
            data_n9ev5_done = process("configs", str_configs_in, data_n9ev5_done)
            group_name = "Default chart group"
            count = 0
            x = 0
            y = 0
            layout = {"h": 2, "w": 6, "x": x, "y": y, "i": str(count)}
            has_group_name = False
            data_n9ev5_done_chart_groups = copy.deepcopy(data_n9ev5_done["chart_groups"][0])
            data_n9ev5_done["chart_groups"] = []
            for k in i["panels"]:
                if k["type"] == "row":
                    print("\033[1;35m k_title: \033[0m", k)
                    data_n9ev5_group_done = process("name", k["title"], data_n9ev5_done_chart_groups)
                    data_n9ev5_done["chart_groups"].append(data_n9ev5_group_done)
                    group_name = k["title"]
                    has_group_name = True
            if not has_group_name:
                data_n9ev5_done["chart_groups"].append(data_n9ev5_done_chart_groups)

            for k in i["panels"]:
                if k["type"] == "graph":
                    layout = {"h": 2, "w": 6, "x": x, "y": y, "i": str(count)}
                    count = count + 1
                    list_prom_ql = []
                    print(k)
                    for l in k["targets"]:
                        prom_ql = {"PromQL": l["expr"]}
                        list_prom_ql.append(prom_ql)
                    dict_configs_chart_in = {"name": k["title"], "QL": list_prom_ql, "legend": False, "highLevelConifg": {"shared": True, "sharedSortDirection": "desc", "precision": "short", "formatUnit": 1000}, "version": 1, "layout": layout}
                    str_configs_chart_in = json.dumps(dict_configs_chart_in)
                    data_n9ev5_chart_done = process("configs", str_configs_chart_in, data_n9ev5_done["chart_groups"][0]["charts"][0])
                    # data_n9ev5_done_chart = copy.deepcopy(data_n9ev5_done["chart_groups"][m]["charts"])
                    # data_n9ev5_done["chart_groups"][m]["charts"] = []
                    for m in range(len(data_n9ev5_done["chart_groups"])):
                        if data_n9ev5_done["chart_groups"][m]["name"] == group_name:
                            data_n9ev5_done["chart_groups"][m]["charts"].append(data_n9ev5_chart_done)
                    x = x + 6
                    if count % 4 == 3:
                        x = 0
                        y = y + 2

            for mm in data_n9ev5_done["chart_groups"]:
                del mm["charts"][0]


            list_n9ev5_done.append(data_n9ev5_done)
            print(list_n9ev5_done)

    with open('n9e_v5_dashboard.json', 'w', encoding='utf-8') as f:
        json.dump(list_n9ev5_done, f, ensure_ascii=False, indent=2)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
