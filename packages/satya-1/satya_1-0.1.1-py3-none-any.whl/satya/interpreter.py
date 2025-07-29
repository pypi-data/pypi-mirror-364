import re
from collections import deque, defaultdict

class SatyaLinkedList:
    def __init__(self):
        self.data = []

    def create(self, size):
        self.data = [None] * size
        return f"Linked list created with {size} nodes."

    def add(self, elements):
        added = []
        for el in elements:
            for i in range(len(self.data)):
                if self.data[i] is None:
                    self.data[i] = el
                    added.append(el)
                    break
            else:
                return f"Linked list full. Only added: {added}"
        return f"Added: {added}"

    def remove(self, index):
        index -= 1
        if 0 <= index < len(self.data):
            removed = self.data[index]
            self.data[index] = None
            return f"Removed: {removed}"
        return "Index out of range"

    def show(self):
        return f"Linked List: {self.data}"

    def size(self):
        return f"List size: {len([x for x in self.data if x is not None])}"


class SatyaStack:
    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)
        return f"Pushed: {val}"

    def pop(self):
        if self.stack:
            return f"Popped: {self.stack.pop()}"
        return "Stack is empty"

    def show(self):
        return f"Stack: {self.stack}"


class SatyaQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, val):
        self.queue.extend(val)
        return f"Enqueued: {val}"

    def dequeue(self):
        if self.queue:
            return f"Dequeued: {self.queue.pop(0)}"
        return "Queue is empty"

    def show(self):
        return f"Queue: {self.queue}"


class SatyaGraph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v):
        self.graph[u].append(v)
        self.graph[v].append(u)
        return f"Edge added between {u} and {v}"

    def show(self):
        return dict(self.graph)

    def dfs(self, start):
        visited = set()
        result = []

        def _dfs(v):
            visited.add(v)
            result.append(v)
            for neighbor in self.graph[v]:
                if neighbor not in visited:
                    _dfs(neighbor)

        _dfs(start)
        return f"DFS: {result}"

    def bfs(self, start):
        visited = set([start])
        queue = deque([start])
        result = []

        while queue:
            v = queue.popleft()
            result.append(v)
            for neighbor in self.graph[v]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return f"BFS: {result}"


class SatyaInterpreter:
    def __init__(self):
        self.ll = SatyaLinkedList()
        self.stack = SatyaStack()
        self.queue = SatyaQueue()
        self.graph = SatyaGraph()

    def run(self, command):
        cmd = command.lower().strip().replace("?", "")

        # Linked List
        if "create linked list" in cmd:
            size = int(re.search(r'\d+', cmd).group())
            return self.ll.create(size)
        elif "add" in cmd and "linked list" not in cmd:
            elements = [x.strip() for x in re.split(r',| ', command) if x.strip().lower() not in ["add"] and x.strip()]
            return self.ll.add(elements)
        elif "remove" in cmd and "element" in cmd:
            match = re.search(r'(\d+)', cmd)
            if match:
                return self.ll.remove(int(match.group(1)))
            return "Couldn't understand which element to remove."
        elif "list size" in cmd:
            return self.ll.size()
        elif "list show" in cmd:
            return self.ll.show()

        # Stack
        elif "create stack" in cmd:
            self.stack = SatyaStack()
            return "Stack created."
        elif "push" in cmd:
            val = command.split()[-1]
            return self.stack.push(val)
        elif "pop" in cmd:
            return self.stack.pop()
        elif "stack show" in cmd:
            return self.stack.show()

        # Queue
        elif "create queue" in cmd:
            self.queue = SatyaQueue()
            return "Queue created."
        elif "enqueue" in cmd:
            vals = [x.strip() for x in re.split(r',| ', command) if x.strip().lower() != "enqueue" and x.strip()]
            return self.queue.enqueue(vals)
        elif "dequeue" in cmd:
            return self.queue.dequeue()
        elif "queue show" in cmd:
            return self.queue.show()

        # Graph
        elif "create graph" in cmd:
            self.graph = SatyaGraph()
            return "Graph created."
        elif "add edge" in cmd:
            parts = command.split()
            u, v = parts[-2], parts[-1]
            return self.graph.add_edge(u, v)
        elif "show graph" in cmd:
            return f"Graph: {self.graph.show()}"
        elif "dfs" in cmd:
            node = command.split()[-1]
            return self.graph.dfs(node)
        elif "bfs" in cmd:
            node = command.split()[-1]
            return self.graph.bfs(node)

        # Math & Logic
        elif "factorial" in cmd:
            n = int(re.search(r'\d+', cmd).group())
            fact = 1
            for i in range(2, n + 1): fact *= i
            return f"Factorial of {n} is {fact}"
        elif "fibonacci" in cmd:
            n = int(re.search(r'\d+', cmd).group())
            fib = [0, 1]
            while len(fib) < n:
                fib.append(fib[-1] + fib[-2])
            return f"Fibonacci: {fib[:n]}"
        elif "palindrome" in cmd:
            match = re.search(r'is\s+(.+?)\s+palindrome', cmd)
            if match:
                s = match.group(1).replace(" ", "")
                return "Yes" if s == s[::-1] else "No"
            return "Invalid input for palindrome check."
        elif "prime" in cmd:
            n = int(re.search(r'\d+', cmd).group())
            if n < 2:
                return "No"
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return "No"
            return "Yes"
        elif "armstrong" in cmd:
            n = int(re.search(r'\d+', cmd).group())
            total = sum(int(d) ** len(str(n)) for d in str(n))
            return "Yes" if total == n else "No"

        # Sorting
        elif "sort" in cmd:
            nums = [int(x) for x in re.findall(r'\d+', cmd)]
            return f"Sorted: {sorted(nums)}"

        # Searching
        elif "search" in cmd:
            matches = re.findall(r'\d+', cmd)
            if matches:
                target = int(matches[0])
                nums = list(map(int, matches[1:]))
                if target in nums:
                    return f"Found {target} at index {nums.index(target)}"
                return f"{target} not found"
            return "Invalid search input."

        # Help
        elif "help" in cmd:
            return """Available commands:
- Create linked list with N nodes
- Add a, b, c
- Remove 2nd element
- List show / List size
- Create stack / Push x / Pop / Stack show
- Create queue / Enqueue 1,2 / Dequeue / Queue show
- Create graph / Add edge A B / Show graph / DFS A / BFS A
- Factorial of N / Fibonacci till N / Is N palindrome?
- Is N armstrong? / Is N prime? / Sort 5 1 3 / Search 3 in 1 2 3"""

        return "Unknown command."
