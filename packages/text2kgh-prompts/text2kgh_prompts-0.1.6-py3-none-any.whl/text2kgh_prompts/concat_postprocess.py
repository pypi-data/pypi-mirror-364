import json

def replace(jsn, maps):
    json_str = json.dumps(jsn,ensure_ascii=False)
    for k, v in maps.items():
        json_str = json_str.replace(k,v)
    return json.loads(json_str)

def load_json(file_path = ""):
    with open(file_path,'r') as f:
        x = f.read()
        return json.loads(x)



def concat_postproces():
    a = load_json("demo/concat.txt")
    b1 = load_json("demo/result2.txt")
    b2 = load_json("demo/result1.txt")

    b1 = replace(b1,a.get('name_change_mapping'))

    b2 = replace(b2,a.get('name_change_mapping'))

    b2 = replace(b2,{"sec_0":"sec_5"})
    b2 = replace(b2,{"s_event_0":"s_event_5"})

    xx = {
        "entities":a.get('consolidated_entities'),
        "article_title":b1.get("article_title"),
        "basic_events":b1.get("basic_events") + b2.get("basic_events"),
        "event_relations_graph":{"sections":b1.get("event_relations_graph")["sections"] + b2.get("event_relations_graph")["sections"],
                                "relationships":b1.get("event_relations_graph")["relationships"] + b2.get("event_relations_graph")["relationships"]},
        "relationship_types_glossary":b1.get("relationship_types_glossary") + b2.get("relationship_types_glossary"),
        "extracted_relations":a.get('extracted_relations'),
    }

    with open('demo/concat_result.txt','w') as f:
        f.write(json.dumps(xx,ensure_ascii = False))

if __name__ == "__main__":
    concat_postproces()