import asyncio
import logging
from typing import Any

from app.execution.mission_kernel import TaskState, WorkGraph
from app.capabilities.broker import AgentRegistry, AgentHarness

logger = logging.getLogger(__name__)


class ExecutionManager:
    """Supervises the WorkGraph and assigns READY tasks to Agent cells."""

    def __init__(self, agent_registry: AgentRegistry, model_gateway: Any, tool_gateway: Any):
        self.agent_registry = agent_registry
        self._model_gateway = model_gateway
        self._tool_gateway = tool_gateway

    async def execute_graph(self, graph: WorkGraph, context: Any) -> None:
        """Run the work graph to completion."""
        logger.info(f"Starting execution of WorkGraph for mission {graph.mission_id}")
        
        while not graph.is_complete():
            ready_tasks = graph.get_ready_tasks()
            
            if not ready_tasks:
                # No tasks are ready, but graph is not complete. Check for blocks.
                graph.mark_blocked()
                if graph.is_complete():
                    break
                # If not blocked, wait and poll (simulate event-driven scheduler)
                await asyncio.sleep(1)
                continue

            for task in ready_tasks:
                task.transition(TaskState.RUNNING)
                logger.info(f"Task {task.id} ({task.name}) RUNNING")
                
                try:
                    # 1. Setup Agent Harness
                    if not task.agent_id:
                        raise ValueError("Task has no assigned agent")
                    
                    agent_def = self.agent_registry.get(task.agent_id)
                    harness = AgentHarness(agent_def, self._model_gateway, self._tool_gateway)
                    
                    # 2. Execute Task
                    result = harness.execute(task.input_data, context)
                    
                    # 3. Handle Success
                    task.output_data = result
                    task.transition(TaskState.SUCCEEDED)
                    logger.info(f"Task {task.id} SUCCEEDED")
                    
                except Exception as e:
                    logger.error(f"Task {task.id} FAILED: {str(e)}")
                    task.transition(TaskState.FAILED, error=str(e))
                    # Handle Retry Logic
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.transition(TaskState.RETRYING)
                        task.transition(TaskState.QUEUED)
                        logger.info(f"Task {task.id} queued for retry ({task.retry_count}/{task.max_retries})")

        logger.info(f"WorkGraph for mission {graph.mission_id} finished execution.")
