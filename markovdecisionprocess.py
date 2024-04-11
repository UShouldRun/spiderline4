class MDP: # markov decision process
    def __init__(self, get_actions, state_analysis, execute, qfunction):
        self._get_actions = get_actions
        self.state_analysis = state_analysis
        self.execute = execute
        self.qfunction = qfunction
        self.action_type = None

    def get_actions(self, node): return self._get_actions(node, self.action_type)
    def non_terminal(self, node): return not self.state_analysis(node)
