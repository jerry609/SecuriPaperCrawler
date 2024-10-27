# securipaperbot/core/context.py

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json


class AnalysisStage(Enum):
    """分析阶段枚举"""
    INIT = "initialization"
    RESEARCH = "research"
    CODE_ANALYSIS = "code_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    DOCUMENTATION = "documentation"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisContext:
    """分析上下文管理器"""

    def __init__(self):
        # 基本信息
        self.conference: str = ""
        self.year: str = ""
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None

        # 状态信息
        self.current_stage: AnalysisStage = AnalysisStage.INIT
        self.progress: float = 0.0
        self.errors: List[Dict[str, Any]] = []

        # 分析结果
        self.research_results: Dict[str, Any] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.quality_results: Dict[str, Any] = {}
        self.documentation: Dict[str, Any] = {}

        # 缓存数据
        self._cache: Dict[str, Any] = {}

    def update_stage(self, stage: AnalysisStage, progress: float = None):
        """更新当前阶段"""
        self.current_stage = stage
        if progress is not None:
            self.progress = progress

    def update_research_results(self, results: Dict[str, Any]):
        """更新研究结果"""
        self.research_results = results
        self.update_stage(AnalysisStage.CODE_ANALYSIS, 0.25)

    def update_analysis_results(self, paper_title: str, results: Dict[str, Any]):
        """更新代码分析结果"""
        self.analysis_results[paper_title] = results
        # 根据已分析的论文数量更新进度
        total_papers = len(self.research_results.get('papers', []))
        if total_papers > 0:
            progress = 0.25 + (len(self.analysis_results) / total_papers) * 0.25
            self.update_stage(AnalysisStage.CODE_ANALYSIS, progress)

    def update_quality_results(self, results: Dict[str, Any]):
        """更新质量评估结果"""
        self.quality_results = results
        self.update_stage(AnalysisStage.DOCUMENTATION, 0.75)

    def update_documentation(self, documentation: Dict[str, Any]):
        """更新文档生成结果"""
        self.documentation = documentation
        self.update_stage(AnalysisStage.COMPLETED, 1.0)
        self.end_time = datetime.now()

    def add_error(self, error: Exception, stage: AnalysisStage, context: Dict[str, Any] = None):
        """添加错误信息"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage.value,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        self.errors.append(error_info)

        if stage != self.current_stage:
            self.update_stage(stage)

    def set_cache(self, key: str, value: Any):
        """设置缓存数据"""
        self._cache[key] = value

    def get_cache(self, key: str, default: Any = None) -> Any:
        """获取缓存数据"""
        return self._cache.get(key, default)

    def clear_cache(self):
        """清除缓存数据"""
        self._cache.clear()

    def to_dict(self) -> Dict[str, Any]:
        """将上下文转换为字典格式"""
        return {
            'basic_info': {
                'conference': self.conference,
                'year': self.year,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat() if self.end_time else None
            },
            'status': {
                'current_stage': self.current_stage.value,
                'progress': self.progress,
                'errors': self.errors
            },
            'results': {
                'research': self.research_results,
                'analysis': self.analysis_results,
                'quality': self.quality_results,
                'documentation': {
                    k: v for k, v in self.documentation.items()
                    if k != 'content'  # 避免存储大型内容
                }
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisContext':
        """从字典创建上下文实例"""
        context = cls()

        # 恢复基本信息
        basic_info = data.get('basic_info', {})
        context.conference = basic_info.get('conference', '')
        context.year = basic_info.get('year', '')
        context.start_time = datetime.fromisoformat(basic_info.get('start_time', ''))
        if basic_info.get('end_time'):
            context.end_time = datetime.fromisoformat(basic_info['end_time'])

        # 恢复状态信息
        status = data.get('status', {})
        context.current_stage = AnalysisStage(status.get('current_stage', AnalysisStage.INIT.value))
        context.progress = status.get('progress', 0.0)
        context.errors = status.get('errors', [])

        # 恢复结果数据
        results = data.get('results', {})
        context.research_results = results.get('research', {})
        context.analysis_results = results.get('analysis', {})
        context.quality_results = results.get('quality', {})
        context.documentation = results.get('documentation', {})

        return context

    def validate(self) -> bool:
        """验证上下文数据的完整性"""
        try:
            # 检查必要字段
            assert self.conference, "Conference is missing"
            assert self.year, "Year is missing"
            assert self.start_time, "Start time is missing"

            # 检查阶段一致性
            if self.current_stage == AnalysisStage.COMPLETED:
                assert self.end_time, "End time is missing for completed analysis"
                assert self.progress == 1.0, "Progress should be 100% for completed analysis"

            # 检查结果一致性
            if self.current_stage >= AnalysisStage.RESEARCH:
                assert self.research_results, "Research results are missing"

            if self.current_stage >= AnalysisStage.CODE_ANALYSIS:
                assert self.analysis_results, "Analysis results are missing"

            if self.current_stage >= AnalysisStage.QUALITY_ASSESSMENT:
                assert self.quality_results, "Quality results are missing"

            if self.current_stage >= AnalysisStage.DOCUMENTATION:
                assert self.documentation, "Documentation is missing"

            return True

        except Exception as e:
            return False

    def __str__(self) -> str:
        """字符串表示"""
        return f"AnalysisContext({self.conference} {self.year}, {self.current_stage.value}, {self.progress:.1%})"