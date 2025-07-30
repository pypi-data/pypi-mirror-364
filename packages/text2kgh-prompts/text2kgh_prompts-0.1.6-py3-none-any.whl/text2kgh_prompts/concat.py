

prompt = """
**[系统提示词版本: 马克思主义知识图谱抽取V1.0]**

**1. 目标 (OBJECTIVE):**
   从非结构化文本片段中抽取、整合并分类实体及其关系三元组，严格遵循一套预定义的、受马克思主义哲学启发的关爱类型。最终目标是生成结构化的知识图谱（KG）表示。

**2. 输入规范 (INPUT_SPECIFICATION):**
   *   **ENTITY_LIST_原始数据 (ENTITY_LIST_RAW):** 字典列表，每个字典代表一个原始实体，包含 `name`（名称）、`aliases`（别名列表，字符串类型）和 `describe`（描述列表，字符串类型）。示例：`[{'name': '实体A', 'aliases': ['A'], 'describe': ['描述A']}]`。可能提供多个此类列表，需要进行初步整合。

**3. 处理阶段 (PROCESSING_PHASES):**

   **3.1. 阶段1: 实体整合 (ENTITY_CONSOLIDATION) (主键: `name` | 副键: `aliases`)**
      *   **输入 (INPUT):** `ENTITY_LIST_原始数据`（可能为多个列表）。
      *   **逻辑 (LOGIC):**
          1.  初始化一个空的 `CONSOLIDATED_ENTITIES` 字典（键：规范名称，值：整合后的实体对象）。
          2.  遍历所有 `ENTITY_LIST_原始数据` 中的每个原始实体。
          3.  对于每个原始实体 `R_E`:
              a.  **尝试直接匹配:** 检查 `R_E.name` 是否作为键存在于 `CONSOLIDATED_ENTITIES` 中。如果存在，跳至步骤 3.1.3.1。
              b.  **尝试别名匹配:** 遍历 `R_E.aliases` 中的每个别名 `A`:
                  i.  检查 `A` 是否作为 `name` 键存在于 `CONSOLIDATED_ENTITIES` 中。
                  ii. 检查 `A` 是否存在于 `CONSOLIDATED_ENTITIES` 中任何现有实体的 `aliases` 列表中。
                  iii. 如果找到匹配（例如，`CONSOLIDATED_ENTITIES` 中的 `C_E`）：跳至步骤 3.1.3.1。`R_E.name` 将成为 `C_E` 的新别名，除非 `R_E.name` 基于预定义偏好或启发式（例如：首次遇到、名称更长等 - **默认：优先保留 `C_E.name` 作为规范名称**）被选为新的规范名称。
              c.  **无匹配:** 如果没有直接或别名匹配，将 `R_E` 作为新条目添加到 `CONSOLIDATED_ENTITIES` 中，以 `R_E.name` 作为其规范键。
          4.  **整合逻辑 (针对匹配):** 如果 `R_E` 与 `C_E` 匹配（通过名称或别名）：
              a.  将 `R_E.aliases` 合并到 `C_E.aliases` 中（去重）。
              b.  将 `R_E.describe` 合并到 `C_E.describe` 中（去重）。
              c.  **记录名称变更:** 如果 `R_E.name` 与 `C_E.name` 不同（即通过别名匹配，`R_E.name` 被整合），则将条目添加到 `NAME_CHANGE_MAPPING` 中：`NAME_CHANGE_MAPPING[R_E.name] = C_E.name`。此映射用于追踪已整合的旧名称（现为别名）及其新的规范名称。
      *   **输出 (OUTPUT):**
          *   `CONSOLIDATED_ENTITIES`: 唯一且整合后的实体字典列表。
          *   `NAME_CHANGE_MAPPING`: 原始非规范名称到其整合后规范名称的字典。`{ "旧名称": "新规范名称" }`。

   **3.2. 阶段2: 关系抽取 (RELATION_EXTRACTION) (利用马克思主义启发的分类法)**
      *   **输入 (INPUT):** `CONSOLIDATED_ENTITIES`（来自阶段1）。
      *   **逻辑 (LOGIC):**
          1.  定义 `马克思主义知识图谱关系分类法 (MARXIST_KG_RELATION_TAXONOMY)`:
              *   **本质-现象/具象化 (ESSENCE_OF / MANIFESTS_AS):** (X, MANIFESTS_AS, Y) / (Y, IS_ESSENCE_OF, X)。语义：X 是 Y 的具体表达/实例；Y 是 X 的根本性质/抽象概念。关键词："是", "一种", "系统", "方法", "表现", "本质"。
              *   **内容-形式/构成 (CONTAINS / IS_COMPONENT_OF):** (X, CONTAINS, Y) / (Y, IS_COMPONENT_OF, X)。语义：X 包含 Y；Y 是 X 的一部分/要素。关键词："包含", "由...构成", "存在", "具有"。
              *   **矛盾-对立/互补 (CONTRADICTS / COMPLEMENTS):** (X, CONTRADICTS, Y) / (X, COMPLEMENTS, Y)。语义：X 与 Y 对立/不同；X 与 Y 协同/增强。关键词："与...不同", "对立", "互补", "协同"。
              *   **原因-结果/目的 (CAUSES / RESULTS_IN / AIMS_TO_ACHIEVE):** (X, CAUSES, Y) / (X, RESULTS_IN, Y) / (X, AIMS_TO_ACHIEVE, Y)。语义：X 导致 Y；X 产生 Y；X 的目的是 Y。关键词："导致", "产生", "用于", "旨在", "实现", "为了"。
              *   **实践-理论/应用 (APPLIES_TO / IS_APPLIED_BY / GUIDES):** (X, APPLIES_TO, Y) / (X, IS_APPLIED_BY, Y) / (X, GUIDES, Y)。语义：X 在 Y 中应用/相关；Y 使用 X；X 为 Y 提供指导。关键词："应用于", "使用", "指导", "针对"。
              *   **发展-历史/创造 (DEVELOPED_BY / PROPOSED_IN / DISCOVERED_IN):** (X, DEVELOPED_BY, Y) / (X, PROPOSED_IN, Y) / (X, DISCOVERED_IN, Y)。语义：X 的起源/创造；X 在 Y 时间被提出/发现。关键词："由...开发", "提出", "发现", "于...年"。
          2.  **关系抽取策略:**
              a.  遍历 `CONSOLIDATED_ENTITIES` 中的每个 `实体 (entity)`。
              b.  对于每个 `实体`，分析其 `describe` 列表。
              c.  对于 `entity.describe` 中的每个 `描述字符串 (description_string)`:
                  i.  执行关键词匹配和浅层语义解析（例如，如果可用，进行依存句法分析，否则使用基于规则的模式匹配）以识别潜在的主语-关系-宾语三元组。
                  ii. **主语 (Subject):** 默认设置为当前 `entity.name`。
                  iii. **宾语 (Object):** 尝试在 `描述字符串` 中识别其他 `CONSOLIDATED_ENTITIES.name` 或 `CONSOLIDATED_ENTITIES.aliases`。如果未找到其他实体，则从描述中提取与关系类型对齐的重要短语或概念。
                  iv. **关系 (Relation):** 将识别到的关键词/模式映射到 `MARXIST_KG_RELATION_TAXONOMY`。优先考虑特异性匹配。通过推断处理双向关系（例如，如果 X MANIFESTS_AS Y，则推断 Y IS_ESSENCE_OF X，除非已明确抽取）。
                  v.  确保抽取的三元组的唯一性（主语、关系、宾语的组合）。
              d.  **三元组结构:** 每个三元组将是一个字典：`{"subject": "实体名称A", "relation": "关系类型", "object": "实体名称B_或_概念", "description": "支持该关系的原始文本片段"}`。
      *   **输出 (OUTPUT):** `EXTRACTED_RELATIONS`: 结构化关系三元组字典列表。

**4. 最终输出格式 (FINAL_OUTPUT_FORMAT):**
   *   包含以下内容的JSON对象：
      *   `consolidated_entities`: 字典列表（来自阶段1）。
      *   `name_change_mapping`: 字典（来自阶段1）。
      *   `extracted_relations`: 字典列表（来自阶段2）。

"""

from text2kgh_prompts.utils import extract_python_code
from llmada.core import BianXieAdapter

def concats():
    import json
    with open('demo/result1.txt','r') as f:
        aa = f.read()
        a = json.loads(aa)

    with open('demo/result2.txt','r') as f:
        bb = f.read()
        b = json.loads(bb)


    bx = BianXieAdapter()

    result = bx.product(prompt + f"{a.get('entities')} {b.get('entities')}")

    with open('demo/concat.txt','w') as f:
        f.write(extract_python_code(result))