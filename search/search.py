# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    visited2=[]
    parent2={}
    
    e=0
    actions={}
    act=[]
    path=[]
    flag=False
    ini=problem.getStartState()
    fin=()
    q=util.Stack()#Queue to store an elemnet which is poped and explored every iteration of while
    q.push(ini)
    visited2.append(ini)
    while ((q.isEmpty())==False):
        u=q.pop()
        visited2.append(u)
        e+=1
        if (problem.isGoalState(u)):
            fin=u
            break
        for v in problem.getSuccessors(u):
            if v[0] not in visited2:
                
                
                actions[tuple((u,v[0]))]=v[1]
                parent2[v[0]]=u
                q.push(v[0])
    x=fin
    path.append(x)
        
    while(parent2[x] !=ini): 
        act.append(actions[(parent2[x],x)])
        x = parent2[x]
        path.append(x)  
    path.append(ini)
    act.append(actions[(parent2[x],x)])
    path = path[::-1] 
    act=act[::-1]
    return act
    util.raiseNotDefined()

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    visited2=[]
    parent2={}
    tree2=[]
    adj={}
    actions={}
    act=[]
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    path=[]
    flag=False
    ini=problem.getStartState()
    fin=()
    q=util.Queue()#Queue to store an elemnet which is poped and explored every iteration of while
    q.push(ini)
    visited2.append(ini)
    tree2.append(ini)
    while ((q.isEmpty())==False):
        u=q.pop()
        if (problem.isGoalState(u)):
            fin=u
            break
        for v in problem.getSuccessors(u):
            if v[0] not in visited2:
                tree2.append(v[0])
                visited2.append(v[0])
                actions[tuple((u,v[0]))]=v[1]
                parent2[v[0]]=u
                q.push(v[0])
                
                    
    x=fin
    path.append(x)
        
    while(parent2[x] !=ini): 
        act.append(actions[(parent2[x],x)])
        x = parent2[x]
        path.append(x)  
    path.append(ini)
    act.append(actions[(parent2[x],x)])
    path = path[::-1] 
    act=act[::-1]
    return act
    util.raiseNotDefined()

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    visited2=[]
    parent2={}
    actions={}
    act=[]
    path=[]
    ini=problem.getStartState()
    visited2.append(ini)
    fin=()
    g={}
    g[ini]=0
    q=util.PriorityQueue()#Queue to store an elemnet which is poped and explored every iteration of while
    q.push(ini,0)
    
    while ((q.isEmpty())==False):
        u=q.pop()

        if u not in visited2:
            visited2.append(u)
        
        if (problem.isGoalState(u)):
            fin=u
            break
        
        for v in problem.getSuccessors(u):
            if v[0] not in visited2:
                ##visited2.append(v[0])
                if v[0] not in g.keys():
                    g[v[0]]=g[u]+v[2]
                    actions[tuple((u,v[0]))]=v[1]
                    parent2[v[0]]=u
                    q.push(v[0],g[v[0]])
                else:
                    if g[v[0]]>g[u]+v[2]:
                        g[v[0]]=g[u]+v[2]
                        actions[tuple((u,v[0]))]=v[1]
                        parent2[v[0]]=u
                        q.push(v[0],g[v[0]])
        
    x=fin
    path.append(x)
        
    while(parent2[x] !=ini): 
        act.append(actions[(parent2[x],x)])
        x = parent2[x]
        path.append(x)  
    path.append(ini)
    act.append(actions[(parent2[x],x)])
    path = path[::-1] 
    act=act[::-1]
    return act
    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    visited2=[]
    parent2={}

    actions={}
    act=[]
    path=[]
    ini=problem.getStartState()
    visited2.append(ini)
    fin=()
    g={}
    g[ini]=0
    q=util.PriorityQueue()#Queue to store an elemnet which is poped and explored every iteration of while
    q.push(ini,0)
    while ((q.isEmpty())==False):
        u=q.pop()

        if u not in visited2:
            visited2.append(u)
        
        if (problem.isGoalState(u)):
            fin=u
            break
        
        for v in problem.getSuccessors(u):
            if v[0] not in visited2:

                ##visited2.append(v[0])
                if v[0] not in g.keys():
                    g[v[0]]=g[u]+v[2]
                    actions[tuple((u,v[0]))]=v[1]
                    parent2[v[0]]=u
                    
                    q.push(v[0],g[v[0]]+heuristic(v[0],problem))
                else:
                    if g[v[0]]>g[u]+v[2]:
                        g[v[0]]=g[u]+v[2]
                        actions[tuple((u,v[0]))]=v[1]
                        parent2[v[0]]=u
                        q.push(v[0],g[v[0]]+heuristic(v[0],problem))
        
    x=fin
    path.append(x)
        
    while(parent2[x] !=ini): 
        act.append(actions[(parent2[x],x)])
        x = parent2[x]
        path.append(x)  
    path.append(ini)
    act.append(actions[(parent2[x],x)])
    path = path[::-1] 
    act=act[::-1]
    return act
    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
