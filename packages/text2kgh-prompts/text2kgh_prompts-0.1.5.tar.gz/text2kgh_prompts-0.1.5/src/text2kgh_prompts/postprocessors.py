# work

import os
import json
from text2kgh_prompts.asserts import validate_llm_output


# def get_aa():
#     # 生成aa
#     #TODO 校验, 
#     result = validate_llm_output(aa)
#     if result 没有通过
#         重新生成 记录生成次数



def postprocessors(main_path = "/Users/zhaoxuefeng/GitHub/obsidian/测试仓库"):
    with open('demo/result.txt','r') as f:
        content = f.read()
    x = json.loads(content)

    sections_list = [
        {"title":i.get('title'),
        "aliases":"",
        "describe":i.get('description'),
        "type":"edge",
        "ends":[f"[[{i}]]"for i in i.get("involved_entities")],
        "next":None,
        "tag":"",
        "complete":"",
        "start":"",
        "content":i.get('basic_events_in_section'),
        }
        for i in x.get("event_relations_graph").get("sections")
    ]
    for j in sections_list:
        content_ = []
        for k in j.get("content"):
            content_.append(replaces(k,x))
        j['content'] = content_

    
    basic_event_list = [
        {"title":i.get("sentence"),
        "aliases":"",
        "describe":"",
        "type":"edge",
        "ends":[f"[[{i}]]"for i in i.get("involved_entities")],
        "next":None,
        "tag":"",
        "complete":"",
        "start":"",
        "content":"",
        }
        for i in x.get("basic_events")
    ]

    entities_list = [
        {"title":i.get("name"),
        "aliases":i.get("aliases"),
        "describe":' | '.join(i.get("describe")),
        "type":"node",
        "ends":'',
        "next":None,
        "tag":"",
        "complete":"",
        "start":"",
        "content":"",
        }
        for i in x.get("entities")
    ]

    xxx = sections_list + basic_event_list + entities_list
    xxx[0]['title']  = "A" + xxx[0]['title'] 

    for jv in xxx:
        file_path = os.path.join(main_path,f"{jv.get('title')}.md")
        # print(file_path)

        md_content = convert_to_markdown_knowledge_graph(jv)
        # print(md_content)
        with open(file_path,'w') as f:
            f.write(md_content)


def convert_to_markdown_knowledge_graph(data):
    """
    将给定的字典数据转换为 Markdown 格式的知识图谱。
    - tags 字段始终存在，当原始 tag 为空时，输出为空列表形式。
    - tags 字段的输出格式为 "[[标签名]]"。
    - content 部分的每个条目为 "[[]]"，外面再加一层双引号。

    Args:
        data (dict): 包含知识图谱信息的字典。

    Returns:
        str: 转换后的 Markdown String。
    """
    markdown_output = "---\n"
    markdown_output += f"title: {data.get('title', '')}\n"
    markdown_output += f"aliases: {data.get('aliases', '')}\n"
    markdown_output += f"describe: {data.get('describe', '')}\n"
    markdown_output += f"type: {data.get('type', '')}\n"
    markdown_output += f"ends: {data.get('ends', '')}\n"
    
    # next 字段处理 None
    next_value = data.get('next')
    markdown_output += f"next: {next_value if next_value is not None else ''}\n"
    
    # tags 字段处理 - 核心改动：确保 tags 字段始终存在
    tags_to_output = []
    # 检查 data['tag'] 是否存在且有实际内容（非空字符串或空列表）
    if 'tag' in data and data['tag']: 
        if isinstance(data['tag'], str):
            # 只有当字符串非空时才添加
            if data['tag'].strip(): 
                tags_to_output.append(data['tag'])
        elif isinstance(data['tag'], list):
            # 过滤掉列表中的空字符串或None，确保只添加有效标签
            tags_to_output.extend([t for t in data['tag'] if t and t.strip()])
            
    # 始终输出 tags 字段
    markdown_output += "tags:\n"
    if tags_to_output:
        for tag_item in tags_to_output:
            markdown_output += f"  - \"[[{tag_item}]]\"\n"
    # 如果 tags_to_output 为空，则 tags: 后面没有子项，或者可以显式加 []
    # 比如：markdown_output += "tags: []\n" 也可以
    # 这里的实现是：如果列表为空，就只输出 tags: 然后换行，不输出任何子项
    # 这在 YAML 中是合法的空列表表示

    markdown_output += f"complete: {data.get('complete', '')}\n"
    markdown_output += f"start: {data.get('start', '')}\n"
    markdown_output += "content:\n"

    for item in data.get('content', []):
        markdown_output += f"  - \"{item}\"\n" 

    markdown_output += "---"
    return markdown_output

def replaces(id_,x):
    if id_.startswith("s_event"):
        for i in x.get("basic_events"):
            if i.get("id") == id_:
                return f'[[{i.get("sentence")}]]'
    else:
        for i in x['event_relations_graph'].get("sections"):
            if i.get("id") == id_:
                return f'[[{i.get("title")}]]'

if __name__ == "__main__":
    postprocessors()