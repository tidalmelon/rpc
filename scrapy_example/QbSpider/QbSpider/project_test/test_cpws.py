# coding=utf-8
import requests
import json

if __name__ == "__main__":

    pay_load = {"Param":"案件类型:行政案件"}

    # r = requests.post("http://wenshu.court.gov.cn/List/TreeContent",data=pay_load)
    #
    #
    # print r.text.replace("\\","").replace('"[',"").replace(']"',"").replace(" ","")

    j_read = json.loads('{"Key":"文书类型","Value":"830003","Child":[{"Key":"判决书","Value":"173871","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":173871},{"Key":"裁定书","Value":"541214","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":541214},{"Key":"调解书","Value":"10","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":10},{"Key":"决定书","Value":"175","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":175},{"Key":"通知书","Value":"3347","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":3347},{"Key":"批复","Value":"1","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":1},{"Key":"答复","Value":"5","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":5},{"Key":"函","Value":"8","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":8},{"Key":"令","Value":"33","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":33},{"Key":"其他","Value":"2222","Child":[],"parent":"","id":"","Field":"文书类型","SortKey":100,"IntValue":2222}],"parent":"","id":"","Field":"","SortKey":100,"IntValue":830003}')

    print [k["Key"].encode("utf8") for k in j_read["Child"] if k["Key"] != ""]
