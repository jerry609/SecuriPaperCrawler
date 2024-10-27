class CodeAnalysisAgent:
    def __init__(self, model="gpt-4"):
        self.model = model
        self.code_quality_metrics = {
            'complexity': self._analyze_complexity,
            'maintainability': self._analyze_maintainability,
            'reusability': self._analyze_reusability,
            'security': self._analyze_security
        }

    async def analyze_module_structure(self, code: str) -> Dict[str, Any]:
        """分析代码模块结构"""
        prompt = """分析以下代码的模块结构：
        1. 核心类和函数的职责
        2. 模块间的依赖关系
        3. 设计模式的使用
        4. 代码组织方式
        5. 可能的改进建议

        代码：
        {code}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(code=code),
            temperature=0.3
        )

        return self._parse_module_analysis(response.choices[0].text)

    async def extract_reusable_components(self, code: str) -> List[Dict[str, Any]]:
        """提取可复用组件"""
        prompt = """识别以下代码中的可复用组件：
        1. 通用工具函数
        2. 设计良好的类
        3. 独立的模块
        4. 算法实现
        5. 设计模式模板

        对每个组件，说明：
        - 功能描述
        - 使用场景
        - 依赖要求
        - 复用建议

        代码：
        {code}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(code=code),
            temperature=0.3
        )

        return self._parse_reusable_components(response.choices[0].text)

    async def analyze_code_quality(self, code: str) -> Dict[str, float]:
        """分析代码质量"""
        results = {}
        for metric, analyzer in self.code_quality_metrics.items():
            results[metric] = await analyzer(code)
        return results

    async def generate_improvement_suggestions(self, analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成改进建议"""
        prompt = """基于以下代码分析结果，提供改进建议：
        1. 代码质量提升
        2. 架构优化
        3. 性能改进
        4. 安全加强
        5. 可维护性提升

        分析结果：
        {analysis_results}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(analysis_results=analysis_results),
            temperature=0.4
        )

        return self._parse_suggestions(response.choices[0].text)

    async def _analyze_complexity(self, code: str) -> float:
        """分析代码复杂度"""
        prompt = """评估以下代码的复杂度，考虑：
        1. 循环嵌套
        2. 条件分支
        3. 函数调用深度
        4. 代码行数
        5. 变量作用域

        返回0-1之间的复杂度分数，越低越好。

        代码：
        {code}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(code=code),
            temperature=0.1
        )

        return float(response.choices[0].text.strip())

    async def _analyze_maintainability(self, code: str) -> float:
        """分析代码可维护性"""
        prompt = """评估以下代码的可维护性，考虑：
        1. 代码结构
        2. 命名规范
        3. 注释完整性
        4. 模块化程度
        5. 测试覆盖

        返回0-1之间的可维护性分数，越高越好。

        代码：
        {code}"""

        response = await self.llm.create_completion(
            model=self.model,
            prompt=prompt.format(code=code),
            temperature=0.1
        )

        return float(response.choices[0].text.strip())

    def _parse_module_analysis(self, text: str) -> Dict[str, Any]:
        """解析模块分析结果"""
        analysis = {
            'core_components': [],
            'dependencies': {},
            'design_patterns': [],
            'organization': {},
            'improvements': []
        }
        # 实现解析逻辑
        return analysis

    def _parse_reusable_components(self, text: str) -> List[Dict[str, Any]]:
        """解析可复用组件"""
        components = []
        # 实现解析逻辑
        return components

    def _parse_suggestions(self, text: str) -> List[Dict[str, str]]:
        """解析改进建议"""
        suggestions = []
        # 实现解析逻辑
        return suggestions