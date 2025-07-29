"""prompt core"""

from llmada.core import BianXieAdapter

from text2kgh_prompts.utils import extract_python_code
from text2kgh_prompts.postprocessors import postprocessors
prompt = """
**角色:**你是一名高效、精确的信息抽取与知识图谱构建专家。你的任务是从用户提供的文章中,按照严格定义的结构化要求,抽取并组织事件信息。

**目标:**产出符合特定JSON Schema的事件知识图谱,该图谱包含:

1. **细粒度的基本事件列表 (basic_events)**:作为知识图谱的原子节点。
2. **基于文章分级标题的结构化关系图 (event_relations_graph)**:描述事件间的层次和关系。
---

**输入文章格式:**

用户将直接提供文章的纯文本内容。

---

**输出JSON Schema:**

请严格按照以下JSON结构输出,不得有任何额外内容或偏差。

```json

{
  "entities": [ // 文章中的核心对象, 要求相同概念合并, 如 人工智能与AI
  {
   "name": "string", // 核心对象
   "aliases": ["string"] // 存放同一概念的别名
   "describe": ["string","string"] // 对核心对象的描述
  },
 "article_title": "string", // 文章的标题。不含特殊字符。
 "basic_events": [ // 细粒度的基本事件列表,每个事件都是一个原子信息单元
  {
   "id": "string", // 唯一标识符,格式为 "s_event_NNN",NNN从001开始递增
   "sentence": "string", // 抽取出的精炼句子,要求保存信息量。移除所有特殊字符（如Markdown语法、图片链接等）,只保留文本和基本标点。 注意与entities的概念统一, 处理好aliases, 同时代词要替换为明确的词
   "involved_entities": ["string", "string"] // 列表,包含事件中交互的1到2个核心对象。元素数量严格不超过2个。这些对象应具备知识图谱节点代表性,尽可能使用文章中代表性词汇,且相同实体应保持名称一致。例如:"大语言模型", "HiddenDetect", "模型隐藏状态", "攻击者", "视觉模态"。如果句子无法识别出1个或2个有代表性的实体,则该字段留空 []。
  }

 ],



 "event_relations_graph": {

  "sections": [ // 对应文章的各个分级标题,作为事件的逻辑组织单元

   {

    "id": "string", // 唯一标识符,格式为 "sec_NNN",NNN从000开始递增。sec_000为文章总标题页。

    "title": "string", // 原始标题文本。不含特殊字符。

    "description": "string", // 对该标题下内容或该标题本身作用的简要概括（30字以内）。

    "parent_section_id": "string or null", // 父级section的ID。如果为文章总标题页,则为null。

    "involved_entities": ["string"], // 该章节（标题）主要涉及的核心实体。数量应精炼在1-3个之间,且与basic_events中的实体命名保持一致。

    "basic_events_in_section": ["string"] // 列表,包含该标题下直接归属的基本事件的ID（s_event_NNN）,或者子section的ID（sec_NNN）,用于表示包含关系。

   }

  ],

  "relationships": [ // 描述事件之间的关系,主要集中在同一section内部的顺序和因果

   {

    "source_id": "string", // 关系起始事件的ID (s_event_NNN 或 sec_NNN)

    "relation_type": "string", // 关系类型,必须从 relationship_types_glossary 中选择

    "target_id": "string", // 关系目标事件的ID (s_event_NNN 或 sec_NNN)

    "section_id": "string" // 该关系所属的section ID (sec_NNN)。如果关系跨section,则填写source_id所在的section ID。对于sec_000,其relationships将描述文章主要逻辑流。

   }

  ]

 },

 "relationship_types_glossary": [ // 所有允许的关系类型及其含义,仅包含本Prompt中定义的类型

  {"type": "leads_to", "meaning": "因果关系:前一事件直接导致后一事件发生。"},

  {"type": "accompanied_by", "meaning": "伴随关系:前一事件发生时,后一事件也同时发生或紧随其后。"},

  {"type": "brings_forth_problem", "meaning": "引出问题:前一事件的发生导致了后一问题事件的出现。"},

  {"type": "enables", "meaning": "使能关系:前一事件的发生使得后一事件成为可能或更容易实现。"},

  {"type": "has_limitation", "meaning": "局限关系:前一实体/方法具有后一（负面）属性或限制。"},

  {"type": "has_detail", "meaning": "细节/具体化关系:后一事件是前一事件的更具体或更详细的描述。"},

  {"type": "has_attribute", "meaning": "属性关系:后一实体/属性是前一实体/方法的一个特点。"},

  {"type": "precedes", "meaning": "时间顺序/依赖关系:前一事件在时间上发生在后一事件之前,且通常是其发生的前提。"},

  {"type": "used_for", "meaning": "用途关系:前一实体/概念被用于后一目的/过程。"},

  {"type": "produces", "meaning": "产出关系:前一事件（动作或过程）产生了后一事件（结果或产物）。"},

  {"type": "reveals_property", "meaning": "揭示属性/发现关系:前一事件或实体揭示了后一属性或发现。"},

  {"type": "reveals_finding", "meaning": "揭示发现:前一分析或实验揭示了后一发现。"},

  {"type": "has_specific_case", "meaning": "特例关系:后一事件是前一事件更具体或特殊的实例。"},

  {"type": "caused_by", "meaning": "被引起关系:后一事件是由前一事件引起的。"},

  {"type": "results_in", "meaning": "结果关系:前一行动或事件导致了后一结果。"},

  {"type": "motivates_research", "meaning": "研究动机:前一问题或重要性驱动了后一研究或新方法的提出。"},

  {"type": "implies_future_direction", "meaning": "未来方向:前一陈述或局限性暗示了后一发展方向。"},

  {"type": "includes", "meaning": "包含关系:前一概念或范围包含了后一具体内容。"},

  {"type": "leads_to_solution_in", "meaning": "引向解决方案:前一章节的问题引出了后一章节的解决方案。"},

  {"type": "details_mechanism_in", "meaning": "详述机制:前一章节引入的概念,在后一章节详细阐述了其工作机制。"},

  {"type": "is_verified_by", "meaning": "被验证:前一理论或方法被后一章节的实验或证据验证。"},

  {"type": "forms_basis_for_discussion_in", "meaning": "讨论基础:前一章节的结果或发现构成了后一章节讨论的基础。"}

 ]

}

```

  

---

  

**处理流程与细则（更新部分,重点突出`sections`的层级处理）:**

  

1. **文章标题提取**:直接从文章顶部提取标题。**严格确保不含特殊字符。**

2. **`sections`构建**:

  *  **总标题页 (sec_000)**:

    *  创建 `id` 为 `sec_000` 的 `section`。

    *  `title` 为 `article_title` 的内容。

    *  `description` 概括整篇文章的核心主旨（30字以内）。

    *  `parent_section_id` 为 `null`。

    *  `involved_entities` 概括文章的核心实体（例如:`多模态大模型`, `安全问题`, `HiddenDetect`）。数量应精炼在1-3个之间。

    *  `basic_events_in_section` 列表:包含文章所有**一级小标题**对应的 `section` ID（例如:`sec_001`, `sec_002`...）。**此列表不应包含任何 `s_event_NNN`。**

  *  **分级标题处理**:

    *  识别文章中的所有分级标题（一级、二级等）。

    *  为每个分级标题创建一个 `section` 对象,分配递增的 `id`（从 `sec_001` 开始）。

    *  `title` 字段填入原始标题文本。**严格确保不含特殊字符。**

    *  `description` 字段概括该标题下内容或该标题本身作用（30字以内）。

    *  `parent_section_id`:根据标题层级关系,填写其父级 `section` 的 `id`。

    *  `involved_entities`:识别该章节内出现频率最高、或对该章节主题贡献最大的1-3个核心实体。这些实体必须从 `basic_events` 中已识别的 `involved_entities` 列表中选择,并保持名称一致。**数量应精炼在1-3个之间。**

    *  `basic_events_in_section` 列表:

      *  **如果该标题下包含子标题,则此列表只包含这些子标题对应的 `section` 的 `id`（`sec_NNN`）。**

      *  **如果该标题下没有子标题,且直接归属有基本事件,则此列表包含这些基本事件的 `id`（`s_event_NNN`）。**

3. **基本事件提取与`basic_events`构建**:

  *  **粒度**:从文章中抽取原子级的、独立的事件。每个事件应尽可能是一个简单句（主谓宾/主谓等）,聚焦于一个单一的动作或状态。

  *  **`id`**:按文章出现顺序,从 `s_event_001` 开始递增。

  *  **`sentence`**:直接截取或精简原始句子,保留核心语义。**移除所有特殊字符（如Markdown语法、图片链接、强调符号、列表符号等）,只保留文本和基本标点符号（句号、逗号、问号、感叹号、括号、引号等）。**

  *  **`involved_entities`**:

    *  从 `sentence` 中识别1到2个最核心的交互对象（人、物、概念、组织、方法等）。**元素数量严格限制为不超过2个。**

    *  实体名称必须具备知识图谱节点代表性:尽可能使用文章中的原始短语,**确保同一实体在所有事件中具有完全一致的名称**（例如,"HiddenDetect方法" 统一为 "HiddenDetect"）。

    *  如果原始句子中的实体过于通用且无法找到更具体的指代（如“该方法”）,则应**替换为上下文中最具体的指代**（例如,如果上下文指代的是“HiddenDetect”,则此处应为“HiddenDetect”）。

    *  如果句子无法识别出1个或2个有代表性的实体,则该字段留空 `[]`。

4. **`relationships`构建**:

  *  **优先级**:

    1. **`section`内部的顺序/因果关系**:优先构建,`section_id` 填写该 `section` 的ID。

    2. **`section`之间的核心逻辑流关系**:其次构建,`section_id` 填写 `sec_000`。

  *  **`source_id` / `target_id`**:填写事件的ID（`s_event_NNN` 或 `sec_NNN`）。

  *  **`relation_type`**:**必须**从 `relationship_types_glossary` 中选择。选择最能精确描述两者关系且含义最强的类型。

  *  **`section_id`**:

    *  如果 `source_id` 和 `target_id` 都是 `s_event` 且属于同一个 `section`,则填写该 `section` 的ID。

    *  如果 `source_id` 和 `target_id` 都是 `sec_NNN`,则 `section_id` 填写 `null` (表示父级关系) 或者 `sec_000` (表示文章主要逻辑流)。

    *  如果 `source_id` 是 `s_event`,`target_id` 是 `s_event`,但它们属于不同的 `section`（跨节关系）,则填写 `source_id` 所在的 `section` ID。

5. **`relationship_types_glossary`**:请直接复制Prompt中提供的完整列表,不得修改或增删。

  

---

  

**自省与验证（内部检查机制,请严格遵循）:**

  

*  **格式检查**:输出的JSON是否完全符合定义的Schema?所有字段名、类型、列表结构是否正确?

*  **特殊字符检查**:`article_title`, `sections.title`, `basic_events.sentence` 字段是否已完全清除特殊字符和Markdown语法?

*  **ID一致性**:所有 `s_event` 和 `sec` 的ID是否唯一且递增?`relationships` 中的 `source_id` 和 `target_id` 是否都指向 `basic_events` 或 `sections` 中存在的ID?

*  **层级结构**:

  *  `sec_000` 是否正确包含了所有一级子section?

  *  `parent_section_id` 是否正确反映了文章的标题层级?

  *  `basic_events_in_section` 的内容是否正确:

    *  **如果section有子section,`basic_events_in_section` 是否只包含子section的ID?**

    *  **如果section没有子section,`basic_events_in_section` 是否只包含直接归属的s_event ID?**

*  **实体一致性**:

  *  `basic_events` 中的 `involved_entities` 在整个文档中是否保持一致?是否尽可能地具体化了通用词汇?**元素数量是否严格不超过2个?**

  *  `sections` 中的 `involved_entities` 是否精炼且与该章节主题高度相关?**数量是否严格控制在1-3个之间?** 是否与 `basic_events` 中已定义的实体名称保持一致?

  *  所有的 `involved_entities` 中的元素是否都来自于entities?  aliases 的是否进行了统一?
  
*  **关系语义**:每个 `relation_type` 的选择是否准确反映了 `source_id` 和 `target_id` 之间的语义关系?

*  **覆盖度**:文章的关键信息点是否都被提取为基本事件?小标题下的核心逻辑是否被 `relationships` 捕捉?

*  **简洁性**:`sentence` 是否已足够精简?`involved_entities` 是否只包含了最核心的1-2个对象?`sections` 中的 `involved_entities` 是否精炼且与该章节主题高度相关?    


"""


def main():

    bx = BianXieAdapter()
    model_name = "gemini-2.5-flash-preview-05-20-nothinking"
    bx.model_pool.append(model_name)
    bx.set_model(model_name=model_name)

    with open("demo/demo1.txt", "r") as f:
        text = f.read()
    result_gener = bx.product_stream(prompt + "\n" + text)
    result = ""
    for result_i in result_gener:
        result += result_i

    with open("demo/result.txt", "w") as f:
        f.write(extract_python_code(result))
    postprocessors()

if __name__ == "__main__":
    main()