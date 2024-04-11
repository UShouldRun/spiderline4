from node import Node
from time import time
from copy import deepcopy
from random import choice
from math import sqrt, log
import networkx as nx
import matplotlib.pyplot as plt

class MCTS:
    def __init__(self, root, name, delta_time, max_nodes, mdp) -> None:
        self.name = name
        self.root_state = root
        self.delta_time, self.cp = delta_time, max_nodes
        self.mdp = mdp
        self.reset()

    def reset(self):
        self.explored_children = dict()
        self.start = 0
        Node.reset()

    def get_name(self) -> str: return self.name
    def get_start(self) -> int: return self.start
    def get_delta_time(self) -> int: return self.delta_time
    def get_time(self) -> int: return time()
    def get_cp(self) -> int: return self.cp
    def get_explored_children(self) -> dict[Node]: return self.explored_children

    def resources_left(self, time: int, comp_power: int): return time < self.get_start() + self.get_delta_time() and comp_power <= self.get_cp()

    def create_root_node(self, state, action) -> Node: return Node(state, None, action)
    def find_direct_children(self, node) -> list[Node]:
        return [self.mdp.execute(node, action) for action in self.mdp.get_actions(node)]
    def find_random_direct_child(self, node) -> Node:
        if not node.get_children(): node.set_children(self.find_direct_children(node))
        if not node.get_children(): return
        return choice(list(node.get_children()))

    def uct_select(self, node: Node, key: bool = False) -> Node:
        '''Select a child of node, balancing exploration & exploitation'''
        def uct(node) -> float:
            if node.get_parent().get_visits() == 0: raise ValueError("Parent node has 0 visits")

            n_parent = node.get_parent().get_visits()
            n_i = node.get_visits()

            if n_i == 0: return float("inf")
            v_i = node.get_reward()/n_i

            if self.mdp.get_const() > 0:
                if n_i > 1: return v_i + self.mdp.get_const() * sqrt(log(n_parent)/log(n_i))
                else: return float("inf")
            return v_i

        return max(node.get_children(), key=uct)

    def select(self, starting_node: Node) -> Node:
        '''Find an unexplored descendent of node'''
        path = []
        node = starting_node
        while True:
            path.append(node)
            if node not in self.get_explored_children() or not self.get_explored_children()[node]: return path[-1]
            unexplored = self.get_explored_children()[node] - self.get_explored_children().keys()
            if unexplored: return unexplored.pop()
            node = self.uct_select(node)

    def expand(self, node: Node) -> None:
        "Update the children dict with the children of node"
        if node in self.get_explored_children(): return  # already expanded
        if not node.get_children(): node.set_children(self.find_direct_children(node))
        self.explored_children[node] = node.get_children()
    
    def backpropagate(self, node: Node, reward: int) -> None:
        '''Restructure the tree according to the new rewards'''
        node.increase_visits()
        node.increase_reward(reward)
        if node.is_root(): return
        self.backpropagate(node.get_parent(), reward)

    def simulate(self, starting_node: Node) -> float:
        '''Simulate a certain universe from a starting branch (node) state'''
        node = self.find_random_direct_child(starting_node)
        while self.mdp.non_terminal(node):
            node1 = self.find_random_direct_child(node)
            if node1 == None: break
            node = node1
        return self.mdp.qfunction(node)

    def mcts(self, root: Node = None) -> Node:
        if root == None: root = self.create_root_node(deepcopy(self.root_state), (self.mdp.action_type, None))

        self.start = time()
        while self.resources_left(self.get_time(), len(self.get_explored_children().keys())):
            leaf = self.select(root)
            if self.mdp.non_terminal(leaf):
                self.expand(leaf)
                reward = self.simulate(leaf)
                self.backpropagate(leaf, reward)

        self.watch_stats(root)
        # self.draw_graph(root)
        return root

    def watch_stats(self, root) -> None:
        # for child in root.get_children(): print(f"Node {child.get_id()}/{child.get_generation()}: {child.get_reward()}/{child.get_visits()}")
        print(f"Total explored nodes: {len(self.get_explored_children().keys())}")
        print(f"Total created nodes: {Node.next_node_id - 1}")
        print("-----------------//----------------")

    def draw_graph(self, root) -> None:
        # Function to recursively add nodes and edges to the graph
        print("loading tree...")
        def add_nodes_edges(G, node, pos=None, level=0):
            if pos is None:
                pos = {node.get_id(): (level, 0)}

            for child in node.get_children():
                G.add_edge(node.get_id(), child.get_id())
                pos[child.get_id()] = (level + 1, len(G) + 1)
                if child.get_generation() < 2:
                    add_nodes_edges(G, counter, child, pos, level + 1)

        # Function to draw the tree graph
        def draw_tree(root):
            G = nx.DiGraph()
            add_nodes_edges(G, root)
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, arrows=True)
            plt.show()

        draw_tree(root)

    def play(self, piece) -> None:
        self.mdp.action_type = piece
        move = self.uct_select(self.mcts(), True).get_action()[1]
        self.root_state.place_piece(piece, move)

        self.reset()

class MDP: # markov decision process
    def __init__(self, get_actions, state_analysis, execute, qfunction, const):
        self._get_actions = get_actions
        self.state_analysis = state_analysis
        self.execute = execute
        self.qfunction = qfunction
        self.const = const
        self.action_type = None

    def get_actions(self, node: Node): return self._get_actions(node, self.action_type)
    def get_const(self): return self.const
    def non_terminal(self, node): return not self.state_analysis(node)