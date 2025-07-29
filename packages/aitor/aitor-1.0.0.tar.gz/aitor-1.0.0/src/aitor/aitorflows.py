import concurrent.futures
from typing import Any, Dict, List, Set, Optional
from collections import deque
import inspect
import logging
from aitor.task import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Aitorflow:
    """Manages a directed acyclic graph (DAG) of tasks."""
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize a workflow.
        
        Args:
            name: Optional name for the workflow
        """
        self.name = name or "Aitorflow"
        self.tasks: Set[Task] = set()
        
    def _add_task(self, task: Task) -> 'Aitorflow':
        """Add a task to the workflow and return self for chaining."""
        self.tasks.add(task)
        # Also add connected tasks
        queue = deque([task])
        visited = set()
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
                
            visited.add(current)
            self.tasks.add(current)
            
            # Add all connected tasks
            for upstream in current.upstream_tasks:
                if upstream not in visited:
                    queue.append(upstream)
            
            for downstream in current.downstream_tasks:
                if downstream not in visited:
                    queue.append(downstream)
                    
        return self
    
    def get_entry_tasks(self) -> List[Task]:
        """Return tasks with no upstream dependencies."""
        return [task for task in self.tasks if not task.upstream_tasks]
    
    def get_exit_tasks(self) -> List[Task]:
        """Return tasks with no downstream dependencies."""
        return [task for task in self.tasks if not task.downstream_tasks]
    
    def validate(self) -> bool:
        """
        Validate the workflow structure and input/output compatibility.
        
        Raises:
            ValueError: If validation fails
        
        Returns:
            True if validation succeeds
        """
        if not self.tasks:
            raise ValueError("Workflow has no tasks")
            
        # Check for cycles using DFS
        for task in self.tasks:
            visited = set()
            path = set()
            
            def check_cycle(current: Task) -> bool:
                visited.add(current)
                path.add(current)
                
                for downstream in current.downstream_tasks:
                    if downstream in path:
                        return True
                    if downstream not in visited:
                        if check_cycle(downstream):
                            return True
                
                path.remove(current)
                return False
            
            if task not in visited:
                if check_cycle(task):
                    raise ValueError(f"Cycle detected in workflow involving task: {task.name}")
        
        # Validate input/output compatibility
        for task in self.tasks:
            if task.upstream_tasks:
                # Count required parameters
                parameters = list(task.signature.parameters.values())
                required_params = sum(1 for p in parameters 
                                    if p.default == inspect.Parameter.empty and 
                                    p.kind != inspect.Parameter.VAR_POSITIONAL)
                has_var_positional = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in parameters)
                
                # Check if parameter count matches upstream task count
                if len(task.upstream_tasks) > 1:
                    if required_params < len(task.upstream_tasks) and not has_var_positional:
                        logger.warning(
                            f"Task {task.name} has {len(task.upstream_tasks)} upstream tasks "
                            f"but only {required_params} required parameters. Make sure you have "
                            f"enough parameters or *args to receive all inputs."
                        )
                
                # NEW CHECK: More required parameters than upstream tasks
                if required_params > len(task.upstream_tasks) and not any(p.default != inspect.Parameter.empty for p in parameters):
                    logger.warning(
                        f"Task {task.name} has {required_params} required parameters "
                        f"but only {len(task.upstream_tasks)} upstream tasks. Some parameters "
                        f"may not receive values."
                    )
        
        return True
    
    def execute(self, initial_input: Any = None) -> Dict[str, Any]:
        """
        Execute the workflow with the given initial input.
        
        Args:
            initial_input: Input to pass to entry tasks
            
        Returns:
            Dictionary mapping task names to their results
        """
        self.validate()
        
        # Track task completion and results
        results: Dict[Task, Any] = {}
        completed_tasks: Set[Task] = set()
        
        # Create a copy of the task dependencies to track remaining dependencies
        remaining_deps: Dict[Task, Set[Task]] = {
            task: set(task.upstream_tasks) for task in self.tasks
        }
        
        # Start with entry tasks
        ready_tasks = self.get_entry_tasks()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures: Dict[concurrent.futures.Future, Task] = {}
            
            # Submit entry tasks
            for task in ready_tasks:
                if task.upstream_tasks:
                    raise ValueError(f"Entry task {task.name} has upstream dependencies")
                
                if initial_input is not None:
                    futures[executor.submit(task.execute, initial_input)] = task
                else:
                    futures[executor.submit(task.execute)] = task
            
            # Process tasks as they complete
            while futures:
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for future in done:
                    task = futures.pop(future)
                    try:
                        result = future.result()
                        logger.info(f"Task {task.name} completed successfully")
                        results[task] = result
                        completed_tasks.add(task)
                        
                        # Check for downstream tasks that are ready to execute
                        for downstream in task.downstream_tasks:
                            remaining_deps[downstream].discard(task)
                            
                            if not remaining_deps[downstream]:
                                # All upstream dependencies are completed
                                # Sort upstream tasks based on their position in the chain
                                sorted_upstream = sorted(downstream.upstream_tasks, 
                                                        key=lambda t: downstream.upstream_order[t])
                                # Get results in the correct order
                                upstream_results = [results[up] for up in sorted_upstream]
                                
                                if len(upstream_results) == 1:
                                    # Single input
                                    futures[executor.submit(downstream.execute, upstream_results[0])] = downstream
                                else:
                                    # Multiple inputs in the correct order
                                    futures[executor.submit(downstream.execute, *upstream_results)] = downstream
                    
                    except Exception as e:
                        logger.error(f"Task {task.name} failed with error: {str(e)}")
                        raise RuntimeError(f"Task {task.name} failed: {str(e)}") from e
        
        # Return results for all tasks
        return {task.name: results[task] for task in self.tasks if task in results}

    
    def print(self) -> None:
        """
        Print a Mermaid diagram of the workflow.
        Shows tasks and their dependencies in a visual flowchart format.
        """
        if not self.tasks:
            print(f"Workflow '{self.name}' is empty")
            return
            
        print("```mermaid")
        print("flowchart TD")
        print(f"    %% Workflow: {self.name}")
        
        # Track processed edges to avoid duplicates
        processed_edges = set()
        
        # First define all nodes
        for task in self.tasks:
            # Create node with task name
            print(f"    {task.name}[\"{task.name}\"]")
        
        # Then add all edges
        for task in self.tasks:
            for downstream in task.downstream_tasks:
                edge = (task.name, downstream.name)
                if edge not in processed_edges:
                    print(f"    {task.name} --> {downstream.name}")
                    processed_edges.add(edge)
        
        print("```")
        print(f"\nTotal tasks: {len(self.tasks)}")

    def add_root(self, task: Task) -> 'Aitorflow':
        """
        Add a task and all its connected tasks (both upstream and downstream) to the workflow.
        
        This is a convenience method that allows adding an entire task graph by
        specifying just one task in the graph.
        
        Args:
            task: A task that is part of the workflow graph
            
        Returns:
            Self for method chaining
        """
        return self._add_task(task)  # add_task already adds all connected tasks 