#!/usr/bin/env Python3.11.1
# -*- coding: utf-8 -*-

import sys
import os
import json
import pprint
from datetime import datetime as dt
import xml.etree.ElementTree as ET

def parse_json(path):
    json_info = {}
    with open(path, "r", encoding="utf-8_sig") as f:
        comment_json = json.load(f)
        json_info["thread_id"] = comment_json["data"]["threads"][0]["id"]
        json_info["comments"] = []
        for thread in comment_json["data"]["threads"]:
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

        chat_ele.set("user_id", comment.get("userId"))

        commands = comment.get("commands", [])
        if "184" in str(commands):
            chat_ele.set("anonymity", "1")
        chat_ele.set("mail", " ".join(commands))

        chat_ele.text = comment.get("body", "")
    tree = ET.ElementTree(root_ele)
    ET.indent(tree, space="  ")
    out_path = os.path.splitext(path)[0] + ".xml"
    with open(out_path, "wb") as file:
        tree.write(file, encoding="utf-8", xml_declaration=True)


def main(path):
    json_info = parse_json(path)
    xml = to_xml(json_info, path)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        if path.lower().endswith(".json"):
            main(path)