from typing import Dict, List

import kink
import loguru
from kink import inject, di
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from scheduler.core.Thought import Thought
from scheduler.core.mcp_client.mcp_client import McpClient
from scheduler.core.schemas.schemas import TaskModel, NeedBranchModel, TaskExecuteStatusModel, \
    TaskModelOut, TaskStatus
from scheduler.core.schemas.structure.ToT import TaskObject
from scheduler.core.schemas.structure.task_relation_manager import Node, TaskRelationManager, Direction
from scheduler.core.schemas.works.PydanticSafetyParser import chat_with_safety_pydantic_output_parser
from scheduler.core.tasks.exceptions.task_exceptions import TaskNeedTurningException, TaskImpossibleException
from tools.func.retry_decorator import retry
from tools.logging import logging


class TaskNode(Node):
    @kink.inject
    def __init__(
            self,
            task_model: TaskModel,
            trm: TaskRelationManager,
            mcp_client: McpClient,
            graph_name: str = 'default_graph_name',
            taskId: str = None,
    ):
        """
        Task class's init func.
        :param task_model: TaskModel
        :param trm: TRM obj.
        """

        super().__init__()
        self.task_pydantic_model = TaskObject(
            task_model=task_model,
            task_out_model=None,
            task_status_model=TaskStatus.PENDING
        )
        self.taskId = taskId
        self._trm = trm
        self.task = task_model
        self.mcp_client = mcp_client
        self.abstract = task_model.abstract
        self.description = task_model.description
        self.verification = task_model.verification
        loguru.logger.debug(f"Task: `{self.abstract}` has been created.")
        self._trm.add_task(self)
        self.graph_name = graph_name

        self._replan_counter = 0

    def __str__(self):
        return f"Task:{self.task_pydantic_model}\n"

    def _flush_graph(self):
        """
        Flush the graph.
        :return:
        """
        self._trm.draw_graph(self.graph_name)

    @logging.function_logging(-1)
    def branch_and_execute(self, branch_requirement) -> TaskModelOut:
        """
        The worker need to do the branch task.
        :return:
        """

        task_chain = branch_requirement.task_chain

        tasks_classed = []
        task_chain_output: TaskModelOut | None = None
        for subtask in task_chain.tasks:
            subtask = TaskNode(task_model=subtask, trm=self._trm, mcp_client=self.mcp_client,
                               graph_name=self.graph_name)
            tasks_classed.append(subtask)
        self._trm.add_sub_tasks(current_task=self, sub_task=tasks_classed)
        for subtask in tasks_classed:
            try:
                # 一个链上的任务中最后一个节点的结果是整个链的最终结果
                # 所以栈中的任务结果依次覆盖，最终出循环时，结果就是最后一个节点的结果
                task_chain_output = subtask.execute()
            except TaskImpossibleException as e:
                if self._replan_counter > 3:
                    raise e

                loguru.logger.warning(f"Task {self.task_pydantic_model} is impossible, replan it.")
                self._replan_counter += 1
                # 重新规划任务并执行, 这里只需要直接重新调用execute, ai会规划的
                self.execute(f'任务:{self.task_pydantic_model}执行失败，失败原因:{e}，需要更改任务规划')
            except Exception as e:
                raise e
        return task_chain_output

    @logging.function_logging(-1)
    def direct_execute(self, advices, articles) -> TaskModelOut:
        """
        The worker do the task.
        :return:
        """
        loguru.logger.info(f"Task {self.task_pydantic_model} is working, articles: {articles}")
        self.task_pydantic_model = self.task_pydantic_model.copy(update={
            "task_status_model": TaskStatus.WORKING
        })

        max_try = 3
        for i in range(max_try):
            try:
                result = self.run_mcp_agent(articles=articles, advices=advices)
                if self.check_task_result(result):
                    result: TaskModelOut = self.digest_result_to_abstract(result=result)
                    self.task_pydantic_model = self.task_pydantic_model.copy(update={
                        "task_status_model": TaskStatus.SUCCESS,
                        "task_out_model": result
                    })
                    loguru.logger.success(f"Task {self.task_pydantic_model} is successful, result: {result}")
                    return result
            except TaskNeedTurningException as e:
                advices += f"此任务你已经尝试过了，但是没有成功，以下是给此次执行的建议:{e}"
            except TaskImpossibleException as e:
                self._trm.remove_node(self)
                raise e
            except Exception as e:
                self._trm.remove_node(self)
                raise e
        self._trm.remove_node(self)
        raise TaskImpossibleException(f"此任务已经尝试{max_try}次了，均没有成功")

    def execute(self, rebranch_prompt='') -> TaskModelOut:
        """
        The task's core.
        There are lots of thoughts in the villager.
        :return:
        """
        loguru.logger.warning(f'task_id: {self.id}')
        articles = ''
        advices = ''
        upper_chain: List[Node] = self._trm.get_upper_import_node_simple(self, window_n=3, window_m=3)

        if len(upper_chain) > 0:
            # 含有上级或平级的前置任务
            advices = f'作为你的执行参考，你的上级或平级的前置任务如下(仅供参考，不要执行):'  # 覆盖
            upper_chain.reverse()  # 栈序翻转
            for upper_node in upper_chain:
                advices += f'\n{upper_node.task_pydantic_model}'
        advices += f'\n{rebranch_prompt}'

        branch_requirement: NeedBranchModel = self.check_branching_requirement(advice=advices)
        self._flush_graph()
        if len(branch_requirement.task_chain.tasks) > 1:
            try:
                return self.branch_and_execute(branch_requirement)
            except TaskImpossibleException as e:
                # 若下级任务产生任务不可能的错误，在此级捕获并重新分配任务分支
                return self.execute()
        else:
            return self.direct_execute(advices, articles)

    @retry(max_retries=5, delay=1)
    @inject
    @logging.function_logging(-1)
    def digest_result_to_abstract(self, result: str, llm):
        """
        Focus on summary of mission results.
        :return:
        """
        pydantic_object = TaskModelOut
        model = llm
        parser = PydanticOutputParser(pydantic_object=pydantic_object)
        promptTemplate = ChatPromptTemplate.from_messages([
            ("system", "{format_instructions};"
                       "你是一名摘要员，负责将下文的结果报告摘要为有价值的(task所关注的)内容，返回格式请严格遵循以上要求;"
                       "只允许摘要文章中出现过的事实内容, 不允许添加任何假设或二级推断的内容;"
                       "(不要尝试去实际执行此任务!)"
             ),
            ("user", "结果报告:{result_report};此结果的对应任务:{task}")
        ])
        input_args = {"result_report": result,
                      "task": self.task,
                      "format_instructions": parser.get_format_instructions(),
                      }
        return chat_with_safety_pydantic_output_parser(model=model, input_args=input_args,
                                                       promptTemplate=promptTemplate,
                                                       schemas_model=pydantic_object)

    @retry(max_retries=5, delay=1)
    @inject
    @logging.function_logging(-1)
    def check_branching_requirement(self, llm, advice=''):
        """
        The thought think about do we need branch for this task.
        :param llm: Dependency Injection's llm object
        :param advice:
        :return:
        """
        pydantic_object = NeedBranchModel
        model = llm
        parser = PydanticOutputParser(pydantic_object=pydantic_object)
        promptTemplate = ChatPromptTemplate.from_messages([
            ("system", "{format_instructions};"
                       "你是一名规划师，请根据用户的问题综合判断，我们是否需要细分该任务才能完成这个任务"
                       "(不要尝试去实际执行任务!)"
                       "如果需要，按照顺序提供任务链，并保证任务链的连续性，让上一个任务的结果可以直接被下一个任务使用，如果不需要，请提供一个长度为1的任务链。"
                       "每个任务仅在简单到只包含一个具体动作且前置信息充分时才能被认为不需要被细分"
             ),
            ("user",
             "任务简述:{abstract};任务描述:{description};作为你的执行参考，你的上级或平级的前置任务如下(仅供参考，不要执行):{advice};")
        ])
        input_args = {"abstract": self.abstract,
                      "description": self.description,
                      "format_instructions": parser.get_format_instructions(),
                      "advice": advice,
                      }
        res = chat_with_safety_pydantic_output_parser(model=model, input_args=input_args,
                                                      promptTemplate=promptTemplate,
                                                      schemas_model=pydantic_object)
        loguru.logger.debug(f"Task chain {res}")
        return res

    @logging.function_logging(-1)
    def run_mcp_agent(self, articles: str = '', advices: str = '',
                      prompt='请你帮我完成以下任务，并返回应返回的信息，在过程中请遵从事实，不要假设，以下是需要完成的内容:'):
        return self.mcp_client.execute(
            f'{prompt}任务摘要:{self.abstract}\n'
            f'任务描述:{self.description}\n'
            f'{articles};{advices};')

    @logging.function_logging(-1)
    def check_task_result(self, result: str):
        """
        Check the task's result is correct or not.
        :return:
        """
        pydantic_object = TaskExecuteStatusModel
        model = di['llm']
        parser = PydanticOutputParser(pydantic_object=pydantic_object)
        promptTemplate = ChatPromptTemplate.from_messages([
            ("system", "你是一名助手，请根据用户的问题和另一位工人的执行结果综合判断此任务状态如何，返回格式请严格遵循以下要求{format_instructions};"
                       "请注意:"
                       "1. 不要尝试去实际执行任务!"
                       "2. 你有权限调用一些函数，另一位工人和你有同等权限，这有助于你判断其状态，下文会给你函数列表;"
             ),
            ("user",
             "任务简述:```{abstract}```;任务描述:```{description}```;执行结果:```{result}```;验收标准:{verification}")
        ])
        input_args = {
            "format_instructions": parser.get_format_instructions(),
            "abstract": self.abstract,
            "description": self.description,
            "result": result,
            "verification": self.verification,
        }
        task_status_model = chat_with_safety_pydantic_output_parser(model=model, input_args=input_args,
                                                                    promptTemplate=promptTemplate,
                                                                    schemas_model=pydantic_object)
        if task_status_model.is_task_successful == 0:
            if task_status_model.is_task_impossible == 0:
                raise TaskNeedTurningException(task_status_model.explain)
            else:
                explain_str = f"任务:{self.abstract}执行失败，失败原因:{task_status_model.explain}"
                # 只有不可能的任务才会向父任务抛出异常，所以需要明确任务简述
                raise TaskImpossibleException(explain_str)
        else:
            return True
