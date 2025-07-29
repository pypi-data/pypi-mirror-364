#! /usr/scripts/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: http://netkiller.github.io
# Author: Neo <netkiller@msn.com>
# Data: 2025-07-20
##############################################
try:
    import re
    import json
except ImportError as err:
    print("Import Error: %s" % (err))


class Markdown:
    def __init__(self, markdown: str = None):
        self.markdown = markdown
        pass

    def parse(self, md_text):
        """
        解析Markdown列表为嵌套字典结构，确保同级节点正确识别
        修复AlmaLinux的层级问题
        """
        # 按行分割文本，保留原始缩进信息（不strip()）
        lines = [line for line in md_text.split('\n') if line.strip()]

        # 提取根标题（以#开头的行）
        title = ""
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
            lines = lines[1:]  # 移除根标题行

        # 解析每一行的缩进级别和内容
        parsed_lines = []
        for line in lines:
            # 匹配列表项（-/*/+ 开头），精确捕获缩进
            match = re.match(r'^(\s*)([-*+])\s+(.*)$', line)
            if match:
                indent = len(match.group(1))  # 原始缩进空格数
                content = match.group(3).strip()

                # 计算缩进级别（2个空格为一级）
                level = max(0, indent // 2)
                parsed_lines.append((level, content))

        # 递归构建嵌套结构
        def build_hierarchy(lines, start_idx, parent_level):
            nodes = []
            i = start_idx

            while i < len(lines):
                current_level, current_content = lines[i]

                # 如果当前级别小于等于父级别，说明不属于当前父节点的子节点
                if current_level <= parent_level:
                    return i, nodes  # 返回当前索引和已构建的节点列表

                # 创建当前节点
                node = {"text": current_content, "children": []}

                # 递归处理子节点（下一行开始，父级别为当前级别）
                next_i, children = build_hierarchy(lines, i + 1, current_level)
                node["children"] = children
                nodes.append(node)

                # 移动到下一个待处理节点
                i = next_i

            return i, nodes

        # 从第0行开始构建，根节点的父级别为-1
        _, children = build_hierarchy(parsed_lines, 0, -1)

        # 构建根节点
        root = children.pop()
        # print(title)
        root["title"] = title

        return root

    def dumps(self):
        result = self.parse(self.markdown)
        json_output = json.dumps(result, ensure_ascii=False, indent=2)
        return json_output

    def debug(self):
        print(self.dumps())

    def jsonData(self):
        return self.parse(self.markdown)

    def main(self):
        # 示例 Markdown 文本
        self.markdown = """# 测试标题
- 一级标题
  - 内容段落1
  - 内容段落2
  - 列表项1
  - 列表项2
    - 子列表项1
      - 孙列表项1
  - 三级标题
    - 更多内容 1
    - AAA
    - AAA
    - 更多内容 1
  - 另一个二级标题
    - 列表A
    - 子列表A1
    - 列表B
      - 子列表B1
        - 孙列表B1-1
      - 子列表B2
"""

        # 解析并转换为 JSON
        # result = self.parser(markdown_text)
        # json_output = json.dumps(result, ensure_ascii=False, indent=2)
        self.debug()
        # 打印 JSON 输出


if __name__ == "__main__":
    markdown = Markdown()
    markdown.main()
