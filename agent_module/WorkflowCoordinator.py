from typing import List, Dict, Any
import asyncio
from datetime import datetime
from enum import Enum
import logging


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class WorkflowCoordinator:
    def __init__(self):
        self.paper_research_agent = PaperResearchAgent()
        self.code_analysis_agent = CodeAnalysisAgent()
        self.documentation_agent = DocumentationAgent()
        self.quality_assessment_agent = QualityAssessmentAgent()

        self.task_queue = asyncio.PriorityQueue()
        self.results_cache = {}
        self.active_tasks = {}

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def process_paper(self, paper_url: str, analysis_config: Dict[str, Any]) -> str:
        """处理论文的主工作流"""
        task_id = self._generate_task_id()

        try:
            # 1. 创建工作流任务
            workflow = self._create_workflow(paper_url, analysis_config)

            # 2. 添加到任务队列
            await self._schedule_workflow(workflow, TaskPriority.MEDIUM)

            # 3. 执行工作流
            results = await self._execute_workflow(workflow)

            # 4. 存储结果
            self.results_cache[task_id] = results

            return task_id

        except Exception as e:
            self.logger.error(f"Error processing paper {paper_url}: {str(e)}")
            raise

    async def _execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流程"""
        results = {
            'start_time': datetime.now(),
            'status': TaskStatus.RUNNING,
            'steps': {}
        }

        try:
            # 1. 论文分析
            self.logger.info("Starting paper analysis...")
            paper_analysis = await self._execute_step(
                self.paper_research_agent.analyze_paper_section,
                workflow['paper_url']
            )
            results['steps']['paper_analysis'] = paper_analysis

            # 2. 代码仓库提取
            self.logger.info("Extracting code repositories...")
            repositories = await self._execute_step(
                self.paper_research_agent.extract_code_repositories,
                paper_analysis
            )
            results['steps']['repositories'] = repositories

            # 3. 代码分析
            self.logger.info("Analyzing code...")
            code_analysis = await self._execute_step(
                self.code_analysis_agent.analyze_module_structure,
                repositories
            )
            results['steps']['code_analysis'] = code_analysis

            # 4. 质量评估
            self.logger.info("Assessing code quality...")
            quality_report = await self._execute_step(
                self.quality_assessment_agent.assess_code_quality,
                code_analysis
            )
            results['steps']['quality_assessment'] = quality_report

            # 5. 文档生成
            self.logger.info("Generating documentation...")
            documentation = await self._execute_step(
                self.documentation_agent.generate_api_documentation,
                code_analysis,
                quality_report
            )
            results['steps']['documentation'] = documentation

            results['status'] = TaskStatus.COMPLETED
            results['end_time'] = datetime.now()

            return results

        except Exception as e:
            results['status'] = TaskStatus.FAILED
            results['error'] = str(e)
            results['end_time'] = datetime.now()
            self.logger.error(f"Workflow execution failed: {str(e)}")
            raise

    async def _execute_step(self, func, *args, **kwargs) -> Any:
        """执行单个工作流步骤"""
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise
                await asyncio.sleep(2 ** retry_count)  # 指数退避

    async def _schedule_workflow(self, workflow: Dict[str, Any], priority: TaskPriority):
        """调度工作流"""
        await self.task_queue.put((priority.value, workflow))

    def _create_workflow(self, paper_url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建工作流配置"""
        return {
            'paper_url': paper_url,
            'config': config,
            'created_at': datetime.now(),
            'status': TaskStatus.PENDING,
            'steps': [
                {
                    'name': 'paper_analysis',
                    'agent': 'paper_research_agent',
                    'status': TaskStatus.PENDING
                },
                {
                    'name': 'code_extraction',
                    'agent': 'paper_research_agent',
                    'status': TaskStatus.PENDING
                },
                {
                    'name': 'code_analysis',
                    'agent': 'code_analysis_agent',
                    'status': TaskStatus.PENDING
                },
                {
                    'name': 'quality_assessment',
                    'agent': 'quality_assessment_agent',
                    'status': TaskStatus.PENDING
                },
                {
                    'name': 'documentation',
                    'agent': 'documentation_agent',
                    'status': TaskStatus.PENDING
                }
            ]
        }

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id in self.results_cache:
            return self.results_cache[task_id]
        return {'status': 'not_found'}

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()
            del self.active_tasks[task_id]
            return True
        return False

    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"