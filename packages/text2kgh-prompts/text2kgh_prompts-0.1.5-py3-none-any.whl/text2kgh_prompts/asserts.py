import json
import re

def validate_llm_output(output_json_str: str) -> dict:
    """
    校验LLM输出的JSON字符串是否符合预定义的Schema和业务规则。

    Args:
        output_json_str: LLM输出的JSON字符串。

    Returns:
        一个字典，包含校验结果和任何发现的错误信息。
        {'status': 'success'/'failure', 'errors': [...]}
    """
    errors = []

    # 1. JSON格式校验
    try:
        data = json.loads(output_json_str)
    except json.JSONDecodeError as e:
        errors.append(f"JSON格式错误: {e}")
        return {'status': 'failure', 'errors': errors}

    # 2. 顶级字段校验
    required_top_level_fields = ["article_title", "basic_events", "event_relations_graph", "relationship_types_glossary"]
    for field in required_top_level_fields:
        if field not in data:
            errors.append(f"缺少顶级字段: '{field}'")
            return {'status': 'failure', 'errors': errors} # 结构性错误，立即返回

    # 3. article_title 校验
    if not isinstance(data["article_title"], str):
        errors.append("article_title 类型错误，必须是字符串。")
    if re.search(r"[^\w\s.,!?'\"():;]", data["article_title"]): # 允许字母、数字、空格、基本标点
        errors.append("article_title 包含特殊字符。")

    # 4. relationship_types_glossary 校验 (为了后续关系类型查找)
    defined_relation_types = set()
    if not isinstance(data["relationship_types_glossary"], list):
        errors.append("relationship_types_glossary 类型错误，必须是列表。")
    else:
        for item in data["relationship_types_glossary"]:
            if not isinstance(item, dict) or "type" not in item or "meaning" not in item:
                errors.append("relationship_types_glossary 中的元素格式不正确，应包含'type'和'meaning'字段。")
                continue
            if not isinstance(item["type"], str) or not isinstance(item["meaning"], str):
                 errors.append(f"relationship_types_glossary 中关系类型 '{item.get('type', '未知')}' 或含义类型错误。")
            defined_relation_types.add(item["type"])
    
    if not defined_relation_types:
        errors.append("relationship_types_glossary 中未定义任何关系类型。")

    # 5. basic_events 校验
    if not isinstance(data["basic_events"], list):
        errors.append("basic_events 类型错误，必须是列表。")
    else:
        seen_event_ids = set()
        prev_id_num = 0
        for i, event in enumerate(data["basic_events"]):
            if not isinstance(event, dict):
                errors.append(f"basic_events[{i}] 元素类型错误，必须是字典。")
                continue

            # 字段存在性
            required_event_fields = ["id", "sentence", "involved_entities"]
            for field in required_event_fields:
                if field not in event:
                    errors.append(f"basic_events[{i}] (ID: {event.get('id', '未知')}) 缺少字段: '{field}'。")

            # id 格式和唯一性
            if not isinstance(event.get("id"), str) or not re.fullmatch(r"s_event_\d{3}", event.get("id", "")):
                errors.append(f"basic_events[{i}] ID '{event.get('id')}' 格式错误，应为 's_event_NNN'。")
            elif event["id"] in seen_event_ids:
                errors.append(f"basic_events[{i}] ID '{event['id']}' 重复。")
            else:
                seen_event_ids.add(event["id"])
                # 检查ID递增
                current_id_num = int(event["id"].split('_')[2])
                if current_id_num != prev_id_num + 1:
                    errors.append(f"basic_events[{i}] ID '{event['id']}' 未按顺序递增。期望 '{prev_id_num + 1:03d}'。")
                prev_id_num = current_id_num

            # sentence 校验
            if not isinstance(event.get("sentence"), str):
                errors.append(f"basic_events[{i}] (ID: {event.get('id', '未知')}) sentence 类型错误，必须是字符串。")
            # 允许字母、数字、空格、基本标点符号（包括中文全角符号），不允许图片链接或其他Markdown语法
            if re.search(r"(\!\[.*?\]\(.*?\)|\*\*|__|\*|_|#|`|\[.*?\]\(.*?\)|<.*?>)", event.get("sentence", "")):
                 errors.append(f"basic_events[{i}] (ID: {event.get('id', '未知')}) sentence 包含不允许的特殊字符或Markdown语法。")

            # involved_entities 校验
            if not isinstance(event.get("involved_entities"), list):
                errors.append(f"basic_events[{i}] (ID: {event.get('id', '未知')}) involved_entities 类型错误，必须是列表。")
            else:
                if len(event["involved_entities"]) > 2:
                    errors.append(f"basic_events[{i}] (ID: {event.get('id', '未知')}) involved_entities 数量超过2个。")
                for entity in event["involved_entities"]:
                    if not isinstance(entity, str):
                        errors.append(f"basic_events[{i}] (ID: {event.get('id', '未知')}) involved_entities 中包含非字符串元素。")

    # 6. event_relations_graph 校验
    if not isinstance(data["event_relations_graph"], dict):
        errors.append("event_relations_graph 类型错误，必须是字典。")
    else:
        # 6.1 sections 校验
        if "sections" not in data["event_relations_graph"] or not isinstance(data["event_relations_graph"]["sections"], list):
            errors.append("event_relations_graph 缺少或 sections 类型错误。")
        else:
            seen_section_ids = set()
            prev_sec_id_num = 0
            for i, section in enumerate(data["event_relations_graph"]["sections"]):
                if not isinstance(section, dict):
                    errors.append(f"sections[{i}] 元素类型错误，必须是字典。")
                    continue

                # 字段存在性
                required_section_fields = ["id", "title", "description", "involved_entities", "basic_events_in_section"]
                for field in required_section_fields:
                    if field not in section:
                        errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) 缺少字段: '{field}'。")

                # id 格式和唯一性
                if not isinstance(section.get("id"), str) or not re.fullmatch(r"sec_\d{3}", section.get("id", "")):
                    errors.append(f"sections[{i}] ID '{section.get('id')}' 格式错误，应为 'sec_NNN'。")
                elif section["id"] in seen_section_ids:
                    errors.append(f"sections[{i}] ID '{section['id']}' 重复。")
                else:
                    seen_section_ids.add(section["id"])
                    # 检查ID递增
                    current_sec_id_num = int(section["id"].split('_')[1])
                    if current_sec_id_num != prev_sec_id_num + 1:
                        errors.append(f"sections[{i}] ID '{section['id']}' 未按顺序递增。期望 '{prev_sec_id_num + 1:03d}'。")
                    prev_sec_id_num = current_sec_id_num

                # title 校验
                if not isinstance(section.get("title"), str):
                    errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) title 类型错误，必须是字符串。")
                if re.search(r"[^\w\s.,!?'\"():;]", section.get("title", "")):
                    errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) title 包含特殊字符。")

                # description 校验
                if not isinstance(section.get("description"), str):
                    errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) description 类型错误，必须是字符串。")
                if len(section.get("description", "")) > 30:
                    errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) description 长度超过30字。")

                # section involved_entities 校验
                if not isinstance(section.get("involved_entities"), list):
                    errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) involved_entities 类型错误，必须是列表。")
                else:
                    for entity in section["involved_entities"]:
                        if not isinstance(entity, str):
                            errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) involved_entities 中包含非字符串元素。")
                        # 检查与 basic_events 实体命名一致性 (粗略检查，更精确需要收集所有基本事件实体)
                        # 这里可以添加更复杂的逻辑，比如检查该实体是否在任何 basic_events 的 involved_entities 中出现过
                        # 暂时不强制，因为需要收集所有基本事件实体，放到后面统一检查
                
                # basic_events_in_section 校验
                if not isinstance(section.get("basic_events_in_section"), list):
                    errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) basic_events_in_section 类型错误，必须是列表。")
                else:
                    for event_id in section["basic_events_in_section"]:
                        if not isinstance(event_id, str) or not re.fullmatch(r"s_event_\d{3}", event_id):
                            errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) basic_events_in_section 中包含格式错误的事件ID: '{event_id}'。")
                        elif event_id not in seen_event_ids:
                             errors.append(f"sections[{i}] (ID: {section.get('id', '未知')}) basic_events_in_section 中包含未在basic_events中定义的事件ID: '{event_id}'。")


        # 6.2 relationships 校验
        if "relationships" not in data["event_relations_graph"] or not isinstance(data["event_relations_graph"]["relationships"], list):
            errors.append("event_relations_graph 缺少或 relationships 类型错误。")
        else:
            for i, rel in enumerate(data["event_relations_graph"]["relationships"]):
                if not isinstance(rel, dict):
                    errors.append(f"relationships[{i}] 元素类型错误，必须是字典。")
                    continue
                
                # 字段存在性
                required_rel_fields = ["source_id", "relation_type", "target_id", "section_id"]
                for field in required_rel_fields:
                    if field not in rel:
                        errors.append(f"relationships[{i}] (Source: {rel.get('source_id', '未知')}) 缺少字段: '{field}'。")

                # source_id/target_id 格式和存在性
                valid_ids = seen_event_ids.union(seen_section_ids) # 允许指向基本事件或section
                if not isinstance(rel.get("source_id"), str) or rel["source_id"] not in valid_ids:
                    errors.append(f"relationships[{i}] source_id '{rel.get('source_id')}' 格式错误或未定义。")
                if not isinstance(rel.get("target_id"), str) or rel["target_id"] not in valid_ids:
                    errors.append(f"relationships[{i}] target_id '{rel.get('target_id')}' 格式错误或未定义。")

                # relation_type 校验
                if not isinstance(rel.get("relation_type"), str) or rel["relation_type"] not in defined_relation_types:
                    errors.append(f"relationships[{i}] relation_type '{rel.get('relation_type')}' 未在 relationship_types_glossary 中定义或类型错误。")

                # section_id 校验 (允许为null或sec_NNN)
                if rel.get("section_id") is not None and (not isinstance(rel["section_id"], str) or not re.fullmatch(r"sec_\d{3}", rel["section_id"])):
                    errors.append(f"relationships[{i}] section_id '{rel.get('section_id')}' 格式错误或类型错误，应为 'sec_NNN' 或 null。")
                if rel.get("section_id") is not None and rel["section_id"] not in seen_section_ids:
                     errors.append(f"relationships[{i}] section_id '{rel.get('section_id')}' 未在 sections 中定义。")
                     
                # 业务逻辑：如果 source_id 和 target_id 都是 s_event 且在同一个 section，那么 section_id 必须是该 section 的 ID
                # 这种逻辑比较复杂，需要知道每个 s_event 属于哪个 section
                # 先简单检查 section_id 是有效的section或null

    # 最终结果
    if errors:
        return {'status': 'failure', 'errors': errors}
    else:
        return {'status': 'success', 'errors': []}

if __name__ == "__main__":
    with open('result.txt','r') as f:
        content = f.read()

    print(validate_llm_output(content))