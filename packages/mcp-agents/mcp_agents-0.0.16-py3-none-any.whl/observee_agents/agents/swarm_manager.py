"""
Agent Swarm Manager for orchestrating multiple agents with dynamic task decomposition
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..agents.agent import MCPAgent
from ..providers.base import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a single task in the execution plan"""
    id: str
    description: str
    type: str  # "parallel" or "sequential"
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error: Optional[str] = None
    agent_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ExecutionPlan:
    """Execution plan created by the manager"""
    tasks: List[Task]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class SwarmManager:
    """
    Orchestrates multiple agents to handle complex queries through dynamic task decomposition
    """
    
    def __init__(
        self,
        provider: Union[str, LLMProvider] = "anthropic",
        model: Optional[str] = None,
        max_parallel_agents: int = 5,
        observee_url: Optional[str] = None,
        observee_api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        server_name: str = "observee",
        enable_filtering: bool = True,
        filter_type: str = "bm25",
        manager_system_prompt: Optional[str] = None,
        agent_system_prompt: Optional[str] = None,
        **provider_kwargs
    ):
        self.provider = provider
        self.model = model
        self.max_parallel_agents = max_parallel_agents
        self.observee_url = observee_url
        self.observee_api_key = observee_api_key
        self.client_id = client_id
        self.server_name = server_name
        self.enable_filtering = enable_filtering
        self.filter_type = filter_type
        self.provider_kwargs = provider_kwargs
        
        # System prompts
        self.manager_system_prompt = manager_system_prompt or self._get_default_manager_prompt()
        self.agent_system_prompt = agent_system_prompt or "You are a helpful AI assistant with access to various tools. Complete your assigned task thoroughly."
        
        # Runtime state
        self.active_agents: Dict[str, MCPAgent] = {}
        self.execution_plan: Optional[ExecutionPlan] = None
        self.task_results: Dict[str, Any] = {}
        
        # Manager agent for task decomposition
        self.manager_agent: Optional[MCPAgent] = None
    
    def _get_default_manager_prompt(self) -> str:
        return """You are a task orchestration manager. Your job is to analyze user queries and create execution plans.

When given a query, you must:
1. Break it down into specific tasks
2. Identify which tasks can run in parallel vs sequentially
3. Determine dependencies between tasks
4. Create a structured execution plan

Output your plan as a JSON object with this structure:
{
    "tasks": [
        {
            "id": "task_1",
            "description": "Clear description of what this task should do",
            "type": "parallel",  // or "sequential"
            "dependencies": []  // list of task IDs this depends on
        }
    ],
    "reasoning": "Brief explanation of your decomposition strategy"
}

Important guidelines:
- Tasks with no dependencies can run in parallel
- Tasks that depend on others must wait for dependencies to complete
- Each task should be self-contained and completable by a single agent
- Consider the user's max_parallel_agents limit when designing the plan
- Make task descriptions detailed enough for agents to execute independently"""
    
    async def __aenter__(self):
        """Initialize the manager agent"""
        # Get observee config using the same logic as main __init__.py
        from .. import _get_observee_config
        config = _get_observee_config(self.observee_url, self.observee_api_key, self.client_id)
        
        self.manager_agent = MCPAgent(
            provider=self.provider,
            model=self.model,
            server_name=self.server_name,
            server_url=config["url"],
            auth_token=config["auth_token"],
            enable_filtering=False,  # Manager doesn't need tool filtering
            system_prompt=self.manager_system_prompt,
            **self.provider_kwargs
        )
        await self.manager_agent.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup manager and any active agents"""
        # Close manager agent
        if self.manager_agent:
            await self.manager_agent.__aexit__(exc_type, exc_val, exc_tb)
        
        # Close any remaining active agents
        for agent in self.active_agents.values():
            try:
                await agent.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing agent: {e}")
        
        self.active_agents.clear()
    
    async def create_execution_plan(self, query: str) -> ExecutionPlan:
        """Use the manager agent to create an execution plan"""
        # Get count of available tools
        tools_count = len(self.manager_agent.all_tools) if self.manager_agent else 0
        
        prompt = f"""Analyze this query and create an execution plan:

Query: {query}

Maximum parallel agents available: {self.max_parallel_agents}
Total tools available: {tools_count}

You have access to all MCP tools. Use the list_tools function if you need to see what tools are available for specific tasks.

Remember to output a valid JSON execution plan."""
        
        # Get plan from manager
        response = await self.manager_agent.chat(prompt)
        
        # Extract JSON from response
        try:
            # Find JSON in the response
            content = response.get("content", "")
            
            # Try to extract JSON block
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Create Task objects
            tasks = []
            for task_data in plan_data.get("tasks", []):
                task = Task(
                    id=task_data.get("id", f"task_{len(tasks)}"),
                    description=task_data.get("description", ""),
                    type=task_data.get("type", "sequential"),
                    dependencies=task_data.get("dependencies", [])
                )
                tasks.append(task)
            
            # Create execution plan
            plan = ExecutionPlan(
                tasks=tasks,
                metadata={
                    "reasoning": plan_data.get("reasoning", ""),
                    "original_query": query
                }
            )
            
            self.execution_plan = plan
            return plan
            
        except Exception as e:
            logger.error(f"Failed to parse execution plan: {e}")
            logger.error(f"Manager response: {content}")
            
            # Fallback: single task
            fallback_task = Task(
                id="task_0",
                description=query,
                type="sequential",
                dependencies=[]
            )
            plan = ExecutionPlan(
                tasks=[fallback_task],
                metadata={"error": str(e), "original_query": query}
            )
            self.execution_plan = plan
            return plan
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with an agent"""
        agent_id = str(uuid.uuid4())
        
        try:
            # Get observee config using the same logic as main __init__.py
            from .. import _get_observee_config
            config = _get_observee_config(self.observee_url, self.observee_api_key, self.client_id)
            
            # Create agent for this task
            agent = MCPAgent(
                provider=self.provider,
                model=self.model,
                server_name=self.server_name,
                server_url=config["url"],
                auth_token=config["auth_token"],
                enable_filtering=self.enable_filtering,
                filter_type=self.filter_type,
                system_prompt=self.agent_system_prompt,
                **self.provider_kwargs
            )
            
            await agent.__aenter__()
            self.active_agents[agent_id] = agent
            
            # Update task status
            task.agent_id = agent_id
            task.status = "running"
            task.started_at = datetime.now()
            
            # Build context-aware prompt
            prompt = f"""Execute this task: {task.description}

Context from previous tasks:
{json.dumps(context, indent=2)}

Complete the task and provide detailed results."""
            
            # Execute task
            result = await agent.chat_with_tools(prompt)
            
            # Update task with results
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result
            
            return {
                "task_id": task.id,
                "status": "success",
                "result": result,
                "duration": (task.completed_at - task.started_at).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            return {
                "task_id": task.id,
                "status": "failed",
                "error": str(e)
            }
            
        finally:
            # Cleanup agent
            if agent_id in self.active_agents:
                agent = self.active_agents.pop(agent_id)
                await agent.__aexit__(None, None, None)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies satisfied)"""
        if not self.execution_plan:
            return []
        
        ready_tasks = []
        for task in self.execution_plan.tasks:
            if task.status == "pending":
                # Check if all dependencies are completed
                deps_satisfied = all(
                    self.get_task_by_id(dep_id).status == "completed"
                    for dep_id in task.dependencies
                )
                if deps_satisfied:
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID"""
        if not self.execution_plan:
            return None
        
        for task in self.execution_plan.tasks:
            if task.id == task_id:
                return task
        return None
    
    def build_task_context(self, task: Task) -> Dict[str, Any]:
        """Build context for a task from its dependencies"""
        context = {}
        
        for dep_id in task.dependencies:
            dep_task = self.get_task_by_id(dep_id)
            if dep_task and dep_task.status == "completed":
                context[dep_id] = {
                    "description": dep_task.description,
                    "result": dep_task.result.get("content", "") if dep_task.result else ""
                }
        
        return context
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute the full swarm workflow:
        1. Create execution plan
        2. Execute tasks respecting dependencies and parallelism limits
        3. Return aggregated results
        """
        start_time = datetime.now()
        
        # Create execution plan
        plan = await self.create_execution_plan(query)
        logger.info(f"Created execution plan with {len(plan.tasks)} tasks")
        
        # Execute tasks
        completed_tasks = []
        
        while True:
            # Get ready tasks
            ready_tasks = self.get_ready_tasks()
            
            if not ready_tasks:
                # Check if all tasks are done
                pending_tasks = [t for t in plan.tasks if t.status == "pending"]
                running_tasks = [t for t in plan.tasks if t.status == "running"]
                
                if not pending_tasks and not running_tasks:
                    break
                
                # Wait for running tasks to complete
                await asyncio.sleep(0.1)
                continue
            
            # Determine how many tasks to run in parallel
            current_parallel = len([t for t in plan.tasks if t.status == "running"])
            available_slots = self.max_parallel_agents - current_parallel
            
            # Select tasks to run
            tasks_to_run = ready_tasks[:available_slots]
            
            # Execute tasks in parallel
            execution_tasks = []
            for task in tasks_to_run:
                context = self.build_task_context(task)
                execution_tasks.append(self.execute_task(task, context))
            
            # Wait for this batch to complete
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task execution failed: {result}")
                else:
                    completed_tasks.append(result)
        
        # Build final response
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Aggregate results
        all_results = []
        for task in plan.tasks:
            if task.result:
                all_results.append({
                    "task_id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "result": task.result.get("content", "")
                })
        
        return {
            "execution_plan": {
                "tasks": len(plan.tasks),
                "reasoning": plan.metadata.get("reasoning", "")
            },
            "results": all_results,
            "summary": self._create_summary(all_results),
            "duration": duration,
            "tasks_completed": len(completed_tasks),
            "tasks_failed": len([t for t in plan.tasks if t.status == "failed"])
        }
    
    def _create_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a summary of all task results"""
        if not results:
            return "No tasks were completed."
        
        summary_parts = []
        for result in results:
            if result["status"] == "completed":
                summary_parts.append(f"- {result['description']}: Completed successfully")
            else:
                summary_parts.append(f"- {result['description']}: Failed")
        
        return "\n".join(summary_parts)
    
    async def execute_stream(self, query: str):
        """
        Stream execution updates in real-time
        """
        start_time = datetime.now()
        
        # Stream: Starting
        yield {
            "type": "start",
            "query": query,
            "timestamp": start_time.isoformat()
        }
        
        # Stream: Planning phase
        yield {
            "type": "planning",
            "message": "Creating execution plan..."
        }
        
        plan = await self.create_execution_plan(query)
        
        yield {
            "type": "plan_created",
            "total_tasks": len(plan.tasks),
            "reasoning": plan.metadata.get("reasoning", "")
        }
        
        # Stream task details
        for task in plan.tasks:
            yield {
                "type": "task_planned",
                "task_id": task.id,
                "description": task.description,
                "dependencies": task.dependencies,
                "can_run_parallel": task.type == "parallel"
            }
        
        # Execute tasks with streaming updates
        completed_count = 0
        
        while completed_count < len(plan.tasks):
            ready_tasks = self.get_ready_tasks()
            
            if ready_tasks:
                current_parallel = len([t for t in plan.tasks if t.status == "running"])
                available_slots = self.max_parallel_agents - current_parallel
                tasks_to_run = ready_tasks[:available_slots]
                
                # Start tasks
                if len(tasks_to_run) > 1:
                    yield {
                        "type": "parallel_batch_start",
                        "count": len(tasks_to_run),
                        "task_ids": [t.id for t in tasks_to_run]
                    }
                
                for task in tasks_to_run:
                    yield {
                        "type": "task_started",
                        "task_id": task.id,
                        "description": task.description,
                        "running_in_parallel": len(tasks_to_run) > 1
                    }
                
                # Execute in parallel
                execution_tasks = []
                for task in tasks_to_run:
                    context = self.build_task_context(task)
                    execution_tasks.append(self.execute_task(task, context))
                
                results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                
                # Stream results
                for i, result in enumerate(results):
                    task = tasks_to_run[i]
                    if isinstance(result, Exception):
                        yield {
                            "type": "task_failed",
                            "task_id": task.id,
                            "error": str(result)
                        }
                    else:
                        yield {
                            "type": "task_completed",
                            "task_id": task.id,
                            "result": task.result.get("content", "") if task.result else ""
                        }
                    completed_count += 1
            else:
                await asyncio.sleep(0.1)
        
        # Stream: Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        all_results = []
        for task in plan.tasks:
            if task.result:
                all_results.append({
                    "task_id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "result": task.result.get("content", "")
                })
        
        yield {
            "type": "complete",
            "summary": self._create_summary(all_results),
            "duration": duration,
            "tasks_completed": len([t for t in plan.tasks if t.status == "completed"]),
            "tasks_failed": len([t for t in plan.tasks if t.status == "failed"])
        }