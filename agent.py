class Agent:
    def __init__(self, start_action="start", end_action="end"):
        self.actions = {}
        self.start_action = start_action
        self.end_action = end_action

    def add_action(self, action_func):
        name = action_func.__name__.lower()
        self.actions[name] = action_func
        return action_func

    def run(self, input=None):
        state = {}
        action_name = self.start_action
        next_input = input
        while action_name != self.end_action and action_name in self.actions:
            action = self.actions[action_name]
            action_name, next_input = action(state, next_input)
            # print("DEBUG", action_name, next_input)

        return state
