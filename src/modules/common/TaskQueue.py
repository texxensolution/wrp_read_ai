from dataclasses import dataclass, field
from queue import Queue
from typing import List, Dict, Any
from .Task import Task
from datetime import datetime, timedelta

@dataclass
class TaskQueue:
    tasks: Queue = Queue()
    failed_tasks: List[Task] = field(default_factory=list)

    def push(self, task: Task) -> None:
        self.tasks.put(task)

    def pop(self) -> Task:
        return self.tasks.get()
    
    def enqueue_many(self, tasks: List[Dict[str, Any]]):
        for task in tasks:
            type = task['assessment_type']
            created_task = Task(payload=task, type=type)
            self.tasks.put(created_task)
    
    # after 5 mins
    def can_reprocess_again(self, task: Task) -> bool:
        # Calculate the current time
        current_time = datetime.now()

        # Calculate the time 5 minutes after the stored timestamp
        five_minutes_after = task.failed_at + timedelta(minutes=5)

        # Check if the current time is equal to 5 minutes after the stored timestamp
        return current_time >= five_minutes_after

    def retry_failed_tasks(self) -> int:
        no_of_reinsertion = 0

        for index, failed_task in enumerate(self.failed_tasks):
            if self.can_reprocess_again(failed_task) and failed_task.no_of_retries < 5:
                failed_task.increment_retry()

                # clear failed at
                failed_task.refresh_failed_at()
                no_of_reinsertion += 1

                # remove the task from failed_tasks
                self.failed_tasks.pop(index)

                self.push(failed_task)
                print(f"retry {failed_task.uuid}")
        
        return no_of_reinsertion
            
    def failed_items_len(self) -> int:
        return len(self.failed_tasks)

    def is_empty(self) -> bool:
        return self.tasks.empty()


