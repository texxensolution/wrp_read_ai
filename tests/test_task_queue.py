from src.common import Task, TaskQueue
# Pytest test cases
def test_push_and_pop():
    queue = TaskQueue()
    task = Task(payload={"data": "sample"}, type="type1")
    queue.push(task)
    assert queue.remaining() == 1
    popped_task = queue.pop()
    assert popped_task == task
    assert queue.remaining() == 0

def test_enqueue_many():
    queue = TaskQueue()
    tasks = [
        {"assessment_type": "type1", "data": "sample1"},
        {"assessment_type": "type2", "data": "sample2"}
    ]
    queue.enqueue_many(tasks)
    assert queue.remaining() == 2
    first_task = queue.pop()
    assert first_task.type == "type1"
    assert first_task.payload == {"assessment_type": "type1", "data": "sample1"}
    second_task = queue.pop()
    assert second_task.type == "type2"
    assert second_task.payload == {"assessment_type": "type2", "data": "sample2"}
    assert queue.remaining() == 0

def test_list_queued_items():
    queue = TaskQueue()
    tasks = [
        {"assessment_type": "type1", "data": "sample1"},
        {"assessment_type": "type2", "data": "sample2"}
    ]
    queue.enqueue_many(tasks)
    queued_items = queue.list_queued_items()
    assert len(queued_items) == 2
    assert queued_items[0].type == "type1"
    assert queued_items[0].payload == {"assessment_type": "type1", "data": "sample1"}
    assert queued_items[1].type == "type2"
    assert queued_items[1].payload == {"assessment_type": "type2", "data": "sample2"}
