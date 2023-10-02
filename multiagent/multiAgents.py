# multiAgents.py
# --------------
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
from util import manhattanDistance
from game import Directions
import random, util
from game import Agent
from pacman import GameState
class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """
    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newGhostPos = successorGameState.getGhostPositions()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        sumd=0
        sumf=0
        for i in newGhostPos:
            sumd+=manhattanDistance(newPos,i)
        l1=[]
        for i in range (newFood.width):
            for j in range (newFood.height):
                if newFood[i][j]==True:
                    l1.append((i,j))
        for k in successorGameState.getCapsules():
            l1.append(k)
        if l1==[]:
            return successorGameState.getScore()
        min4=manhattanDistance(newPos,l1[0])
        for i in l1:
            sumf+=manhattanDistance(newPos,i)
            if min4>manhattanDistance(newPos,i):
                min4=manhattanDistance(newPos,i)
        f=1
        for i in newScaredTimes:
            ##print(newScaredTimes)
            if i==0:
                f=0
        if f==1:
            return 4*successorGameState.getScore()-currentGameState.getScore()
        if sumd>=5:
            return 4*(successorGameState.getScore()-currentGameState.getScore())+sum(newScaredTimes)-(newFood.count())-2*min4
        return 4*(successorGameState.getScore()-currentGameState.getScore())+2*(sumd)+sum(newScaredTimes)-(newFood.count())-2*min4
        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
    def evals(self,gameState,index,depth):
        if   depth==0 or gameState.getLegalActions(index)==[]:
            if gameState.isWin():
                return self.evaluationFunction(gameState)
            elif gameState.isLose():
                return self.evaluationFunction(gameState)
            else:
                return self.evaluationFunction(gameState)
        elif index==0:
            maxi=-9999
            for i in gameState.getLegalActions(index):
                if index+1==self.n:
                    ev=self.evals(gameState.generateSuccessor(index,i),0,depth-1)
                else:
                    ev=self.evals(gameState.generateSuccessor(index,i),index+1,depth)
                maxi=max(maxi,ev)
            return maxi
        elif index!=0:
            mini=9999
            for i in gameState.getLegalActions(index):
                if index+1==self.n:
                    ev=self.evals(gameState.generateSuccessor(index,i),0,depth-1)
                else:
                    ev=self.evals(gameState.generateSuccessor(index,i),index+1,depth)
                
                mini=min(mini,ev)

            return mini

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        ut={}
        self.n=gameState.getNumAgents()
        for i in gameState.getLegalActions(self.index):
            if self.n>1:
                    ut[i]=self.evals(gameState.generateSuccessor(self.index,i),self.index+1,self.depth)
            else:
                    ut[i]=self.evals(gameState.generateSuccessor(self.index,i),self.index,self.depth)
            ##ut[i]=self.evals(gameState.generateSuccessor(self.index,i),self.depth-1)
            
       
        m1=max(ut.values())
        return list(ut.keys())[list(ut.values()).index(m1)]
        util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    
    def evalsa(self,gameState,index,depth,alpha,beta):
        
        if   depth==0 or gameState.getLegalActions(index)==[]:
            self.ut[(gameState,None)]=self.evaluationFunction(gameState)
            if gameState.isWin():
                return self.evaluationFunction(gameState)
            elif gameState.isLose():
                return self.evaluationFunction(gameState)
            else:
                return self.evaluationFunction(gameState)
        elif index==0:
            maxi=-9999
            for i in gameState.getLegalActions(index):
                if index+1==self.n2:
                    ev=self.evalsa(gameState.generateSuccessor(index,i),0,depth-1,alpha,beta)
                    
                else:
                    ev=self.evalsa(gameState.generateSuccessor(index,i),index+1,depth,alpha,beta)
                
                maxi=max(maxi,ev)
                self.ut[(gameState,i)]=maxi
                if maxi>beta:
                    return maxi
                alpha=max(alpha,maxi)
                
            return maxi
        elif index!=0:
            mini=9999
            for i in gameState.getLegalActions(index):
                if index+1==self.n2:
                    ev=self.evalsa(gameState.generateSuccessor(index,i),0,depth-1,alpha,beta)
                 

                else:
                    ev=self.evalsa(gameState.generateSuccessor(index,i),index+1,depth,alpha,beta)
                mini=min(mini,ev)
                self.ut[(gameState,i)]=mini
                if mini<alpha:
                    return mini
                
                beta=min(beta,mini)
                

            return mini

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        self.ut={}
        self.n2=gameState.getNumAgents()
        v=self.evalsa(gameState,self.index,self.depth,-999999,999999)
        action=None
        mm=-999999
        for i in gameState.getLegalActions(self.index):
            if self.ut[(gameState,i)]>mm:
                mm=self.ut[(gameState,i)]
                action=i
        return action
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """
    def evalse(self,gameState,index,depth):
        if   depth==0 or gameState.getLegalActions(index)==[]:
            if gameState.isWin():
                return self.evaluationFunction(gameState)
            elif gameState.isLose():
                return self.evaluationFunction(gameState)
            else:
                return self.evaluationFunction(gameState)
        elif index==0:
            maxi=-9999
            for i in gameState.getLegalActions(index):
                if index+1==self.n3:
                    ev=self.evalse(gameState.generateSuccessor(index,i),0,depth-1)
                else:
                    ev=self.evalse(gameState.generateSuccessor(index,i),index+1,depth)
                maxi=max(maxi,ev)
            return maxi
        elif index!=0:
            ev=0
            mini=9999
            for i in gameState.getLegalActions(index):
                prob=1/len(gameState.getLegalActions(index))
                if index+1==self.n3:
                    ev+=prob*self.evalse(gameState.generateSuccessor(index,i),0,depth-1)
                else:
                    ev+=prob*self.evalse(gameState.generateSuccessor(index,i),index+1,depth)
            

            return ev
                

            return mini
    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        ut={}
        self.n3=gameState.getNumAgents()
        for i in gameState.getLegalActions(self.index):
            if self.n3>1:
                    ut[i]=self.evalse(gameState.generateSuccessor(self.index,i),self.index+1,self.depth)
            else:
                    ut[i]=self.evalse(gameState.generateSuccessor(self.index,i),self.index,self.depth)
            ##ut[i]=self.evals(gameState.generateSuccessor(self.index,i),self.depth-1)
            
       
        m1=max(ut.values())
        return list(ut.keys())[list(ut.values()).index(m1)]
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    Pos=currentGameState.getPacmanPosition()
    GhostPos = currentGameState.getGhostPositions()
    GhostStates = currentGameState.getGhostStates()
    ScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]
    sumd=0
    sumf=0

    
    Food = currentGameState.getFood()
        
    
    for i in GhostPos:
        sumd+=manhattanDistance(Pos,i)
    l1=[]
    for i in range (Food.width):
        for j in range (Food.height):
            if Food[i][j]==True:
                l1.append((i,j))
    if l1==[]:
        return currentGameState.getScore()
    min4=manhattanDistance(Pos,l1[0])
    for i in l1:
        sumf+=manhattanDistance(Pos,i)
        if min4>manhattanDistance(Pos,i):
            min4=manhattanDistance(Pos,i)
    '''l1=[]
    for i in range (Food.width):
        for j in range (Food.height):
            if Food[i][j]==True:
                l1.append((i,j))
    for k in currentGameState.getCapsules():
        l1.append(k)
    if l1==[]:
        return currentGameState.getScore()
    min4=manhattanDistance(Pos,l1[0])
    for i in l1:
        sumf+=manhattanDistance(Pos,i)
        if min4>manhattanDistance(Pos,i):
            min4=manhattanDistance(Pos,i)
    f=1
    for i in ScaredTimes:
        if i==0:
            f=0
    if f==1:
        return 4*currentGameState.getScore()
    if sumd>=5:
        return 4*(currentGameState.getScore())+sum(ScaredTimes)-(Food.count())-2*min4
    return 4*(currentGameState.getScore())+2*(sumd)+sum(ScaredTimes)-(Food.count())-2*min4'''



    return currentGameState.getScore()+sumd+sum(ScaredTimes)-(Food.count())
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
