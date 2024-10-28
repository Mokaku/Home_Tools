import requests
import json

source_file_name = "../../json_source/16817330667316963697.json"
kakuyomu_url = "https://kakuyomu.jp"


with open(source_file_name) as f:
    j = json.load(f)

    rec01 = (j["props"]["pageProps"]["__APOLLO_STATE__"])

    work_id= (j["query"]["workId"])

for key in rec01:
    if ("Work:" in key):
        # print(key)
        if (work_id == (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])):
            work_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
        # work_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
            print (work_title, work_id)

for key in rec01:
    if ("Episode" in key):
        # print(key)
        episode_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
        episode_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
        print ("<li><a href=\"" + kakuyomu_url + "/works/" + work_id + "/episodes/" + episode_id + "\">" + episode_title + "</a><br></li>" )

for key in rec01:
    if ("Chapter" in key):
        # print(key)
        chapter_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
        chapter_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
        print (chapter_id, chapter_title)


        # https://kakuyomu.jp/works/1177354054886943247/episodes/1177354054886943594
