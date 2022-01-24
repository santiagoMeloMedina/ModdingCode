from argument_tasks import Interface
import tasks.methods as task_methods


if __name__ == "__main__":
    try:
        Interface(source=open("tasks/tasks.yml", "r"), methods=task_methods).run()
    except Exception as e:
        print(e)
