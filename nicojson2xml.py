#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import json
import pprint
from datetime import datetime as dt
import xml.etree.ElementTree as ET
import traceback

def parse_json(json_content):
    json_info = {}
    json_info["thread_id"] = json_content["data"]["threads"][0]["id"]
    json_info["comments"] = []
    
    for thread in json_content["data"]["threads"]:
        if thread["comments"]:
            json_info["comments"].extend(thread["comments"])
    
    return json_info


def to_xml(json_info, path):
    root_ele = ET.Element("packet")
    thread = json_info["thread_id"]
    for comment in json_info["comments"]:
        chat_ele = ET.SubElement(root_ele, "chat")
        chat_ele.set("thread", str(thread))
        chat_ele.set("no", str(comment.get("no")))
        chat_ele.set("vpos", str(round(comment.get("vposMs", 0) / 10)))
        chat_ele.set("date", str(round(dt.fromisoformat(comment.get("postedAt", "2000-01-01T00:00:00")).timestamp())))
        #chat_ele.set("date_usec", "") 取得方法不明

        nicoru = int(comment.get("nicoruCount", 0))
        if nicoru:
            chat_ele.set("nicoru", str(nicoru))

        score = int(comment.get("score", 0))
        if score:
            chat_ele.set("score", str(score))

        if int(comment.get("isPremium", False)):
            chat_ele.set("premium", "1")

        commands = comment.get("commands", [])
        if "184" in str(commands):
            chat_ele.set("anonymity", "1")
            
        chat_ele.set("user_id", comment.get("userId"))
            
        if commands:
            chat_ele.set("mail", " ".join(commands))

        chat_ele.text = comment.get("body", "")
    tree = ET.ElementTree(root_ele)
    ET.indent(tree, space="  ")

    return tree


def main(path):
    with open(path, "r", encoding="utf-8_sig") as f:
        json_content = json.load(f)
    
    json_comment_dict = parse_json(json_content)
    xml_tree = to_xml(json_comment_dict, path)
    
    out_path = os.path.splitext(path)[0] + ".xml"

    with open(out_path, "wb") as file:
        xml_tree.write(file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            if path.lower().endswith(".json"):
                try:
                    main(path)
                    print(f"Succcess: {path}")
                except Exception as e:
                    error_message = traceback.format_exc()
                    print(f"Error: {error_message}")
                    with open(path + "_error.txt", "w") as file:
                        file.write(error_message)
            else:
                print("it doesn't have json extension.")
    else:
        print(f"Usage: python {sys.argv[0]} comment.json")
        print(f"       (or drag and drop jsons)")
