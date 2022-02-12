from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        priority = int(args[0])
        task = args[1]

        while priority in self.current_items:
            temp = self.current_items[priority]
            self.current_items[priority] = task
            priority += 1
            task = temp

        self.current_items[priority] = task

        self.write_current()
        print(f'Added task: "{task}" with priority {priority}')

    def done(self, args):
        priority = int(args[0])

        if priority in self.current_items:
            self.completed_items.append(self.current_items[priority])
            self.write_completed()
            del self.current_items[priority]
            self.write_current()
            print("Marked item as done.")
            return

        print(f"Error: no incomplete item with priority {priority} exists.")

    def delete(self, args):
        priority = int(args[0])

        if priority in self.current_items:
            del self.current_items[priority]
            self.write_current()
            print(f"Deleted item with priority {priority}")
            return
        print(f"Error: item with priority {priority} does not exist. Nothing deleted.")

    def ls(self):
        index = 1
        for p in sorted(self.current_items.keys()):
            print(f"{index}. {self.current_items[p]} [{p}]")
            index += 1

    def report(self):

        self.read_current()
        self.read_completed()

        print(f"Pending : {len(self.current_items)}")
        index = 1
        for p in sorted(self.current_items.keys()):
            print(f"{index}. {self.current_items[p]} [{p}]")
            index += 1
        print(f"\nCompleted : {len(self.completed_items)}")
        index = 1
        for item in self.completed_items:
            print(f"{index}. {item}")
            index += 1

    def render_pending_tasks(self):
        self.read_current()
        html = "<h1>Pending tasks</h1><ol>"
        for p in sorted(self.current_items.keys()):
            html = html + f"<li>{self.current_items[p].strip()} [{p}]</li>"
        html = html + "</ol>"
        return html

    def render_completed_tasks(self):
        self.read_completed()
        html = "<h1>Completed tasks</h1><ol>"
        for task in self.completed_items:
            html = html + f"<li>{task.strip()}</li>"
        html = html + "</ol>"
        return html


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
