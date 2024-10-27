from typing import List, Dict, Any
import asyncio
from dataclasses import dataclass


@dataclass
class CodeComponent:
    name: str
    description: str
    usage: str
    params: List[Dict[str, str]]
    returns: Dict[str, str]
    examples: List[str]


class DocumentationAgent:
    def __init__(self, model="gpt-4"):
        self.model = model
        self.template_engine = self._init_template_engine()

    async def generate_api_documentation(self, code: str, analysis_results: Dict[str, Any]) -> str:
        """生成API文档"""
        prompt = """基于以下代码和分析结果，生成详细的API文档：

        要求：
        1. 清晰的功能描述
        2. 完整的参数说明
        3. 返回值说明
        4. 详细的使用示例
        5. 注意事项和限制
        6. 错误处理说明

        代码：
        {code}

        分析结果：
        {analysis_results}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(
                code=code,
                analysis_results=analysis_results
            ),
            temperature=0.4
        )

        return self._format_api_documentation(response.choices[0].text)

    async def generate_tutorial(self, components: List[CodeComponent]) -> str:
        """生成教程文档"""
        prompt = """为以下组件生成详细的教程文档：

        要求：
        1. 逐步的使用指南
        2. 实际的使用场景
        3. 最佳实践建议
        4. 常见问题解答
        5. 性能优化建议

        组件信息：
        {components}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(components=components),
            temperature=0.4
        )

        return self._format_tutorial(response.choices[0].text)

    async def generate_code_examples(self, component: CodeComponent) -> List[Dict[str, str]]:
        """生成代码示例"""
        prompt = """为以下组件生成多个代码示例：

        要求：
        1. 基础使用示例
        2. 高级特性示例
        3. 错误处理示例
        4. 性能优化示例
        5. 与其他组件集成示例

        组件信息：
        {component}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(component=component),
            temperature=0.4
        )

        return self._parse_code_examples(response.choices[0].text)

    async def generate_integration_guide(self, components: List[CodeComponent]) -> str:
        """生成集成指南"""
        prompt = """生成组件集成指南：

        要求：
        1. 架构整合建议
        2. 依赖管理说明
        3. 配置要求
        4. 测试策略
        5. 部署考虑

        组件列表：
        {components}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(components=components),
            temperature=0.4
        )

        return self._format_integration_guide(response.choices[0].text)

    async def generate_migration_guide(
            self,
            old_version: str,
            new_version: str,
            breaking_changes: List[Dict[str, str]]
    ) -> str:
        """生成迁移指南"""
        prompt = """生成版本迁移指南：

        要求：
        1. 破坏性变更说明
        2. 迁移步骤
        3. 兼容性说明
        4. 迁移脚本
        5. 回滚方案

        旧版本：{old_version}
        新版本：{new_version}
        破坏性变更：{breaking_changes}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(
                old_version=old_version,
                new_version=new_version,
                breaking_changes=breaking_changes
            ),
            temperature=0.4
        )

        return self._format_migration_guide(response.choices[0].text)

    def _format_api_documentation(self, text: str) -> str:
        """格式化API文档"""
        # 实现文档格式化逻辑
        return self.template_engine.render('api_template.md', {'content': text})

    def _format_tutorial(self, text: str) -> str:
        """格式化教程文档"""
        # 实现教程格式化逻辑
        return self.template_engine.render('tutorial_template.md', {'content': text})

    def _parse_code_examples(self, text: str) -> List[Dict[str, str]]:
        """解析代码示例"""
        examples = []
        # 实现示例解析逻辑
        return examples

    def _format_integration_guide(self, text: str) -> str:
        """格式化集成指南"""
        # 实现集成指南格式化逻辑
        return self.template_engine.render('integration_template.md', {'content': text})

    def _format_migration_guide(self, text: str) -> str:
        """格式化迁移指南"""
        # 实现迁移指南格式化逻辑
        return self.template_engine.render('migration_template.md', {'content': text})

    def _init_template_engine(self):
        """初始化模板引擎"""
        # 实现模板引擎初始化逻辑
        return TemplateEngine()