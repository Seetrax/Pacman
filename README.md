# Pacman AI: Search, Planning, and Learning

My implementations of AI methods using the UC Berkeley CS188 Pacman projects (Spring 2023). These projects helped me connect theory to visible behavior: which maze cells a search explores, how Pacman plans around ghosts, and how rewards shape a learned policy.

This README explains the state representations, algorithms, and evaluation functions in my code. The game engine, displays, utilities, and autograders come from the Berkeley framework.

## Repository map

| Module | Main implementation files | Scope |
| --- | --- | --- |
| [Search](search/) | [search.py](search/search.py), [searchAgents.py](search/searchAgents.py) | DFS, BFS, UCS, A*, corner states, food heuristics, and repeated food searches |
| [Multi-agent search](multiagent/) | [multiAgents.py](multiagent/multiAgents.py) | Reflex evaluation, minimax, alpha-beta pruning, and expectimax |
| [Reinforcement learning](reinforcement/) | [valueIterationAgents.py](reinforcement/valueIterationAgents.py), [qlearningAgents.py](reinforcement/qlearningAgents.py) | Value iteration, tabular Q-learning, and approximate Q-learning |
| [Logic](logic/logic/) | [logicPlan.py](logic/logic/logicPlan.py) | Propositional constraints, SAT planning, localization, mapping, and SLAM |
| [Tracking](tracking/) | [factorOperations.py](tracking/factorOperations.py), [inference.py](tracking/inference.py) | Factor operations, variable elimination, exact inference, particle filtering, and ghost chasing |

## Getting started

Use Python 3 and run commands from the relevant module directory. Each project has its own copies of files such as `pacman.py` and `util.py`, and relies on local imports. Graphical demos require Tkinter; `python -m tkinter` checks whether it is available.

From the repository root:

```sh
cd search
python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
```

Add `-q` to Pacman commands to run without a graphical window. Commands below assume you have switched into the named module directory.

## 1. Search: finding paths through a maze

### Frontier management and path reconstruction

In `search.py`, I separate frontier management from path reconstruction. `parent2[child]` records the predecessor of a state, while `actions[(parent, child)]` records the move between them. After reaching a goal, I follow the parent chain backward and reverse the collected actions to produce Pacman's route.

| Algorithm | Frontier | Next state to explore |
| --- | --- | --- |
| DFS | `util.Stack` | Most recently added state; explores deeply before returning to other branches |
| BFS | `util.Queue` | Earliest added state; explores in increasing numbers of moves |
| UCS | `util.PriorityQueue` | Lowest accumulated path cost, `g(s)` |
| A* | `util.PriorityQueue` | Lowest estimated total cost, `g(s) + h(s)` |

BFS marks states visited when they enter the queue. DFS marks them when popped, so a state can enter its stack more than once. UCS and A* maintain a `g` dictionary: a cheaper route to an unvisited state updates its parent and inserts another priority-queue entry. My implementation uses visited lists and does not reopen expanded states.

BFS targets shortest routes when every move has the same cost. UCS accounts for differing step costs. A* adds a heuristic to guide exploration toward the goal; its optimality depends on the heuristic and search assumptions.

From `search/`, compare these on the same maze:

```sh
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs
python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
```

The display highlights expanded cells, while the console reports path cost and nodes expanded. Together, these show the route found and the effort spent finding it.

### Visiting all four corners

For `CornersProblem`, position alone cannot describe progress: Pacman may revisit the same cell after visiting different corners. I use this state representation:

```text
((x, y), visited_corner_1, visited_corner_2, visited_corner_3, visited_corner_4)
```

Each flag is `0` or `1`. Successors copy the flags and mark a corner when Pacman enters it. Goal states have all four flags set and Pacman at a corner.

My `cornersHeuristic` returns the minimum Manhattan distance to any corner, or zero once all corners have been visited. It includes already visited corners, making it a conservative but weak estimate: it can return zero at a visited corner while others remain.

```sh
python pacman.py -l mediumCorners -p AStarCornersAgent
```

### Collecting food

Food search uses `(pacmanPosition, foodGrid)` as its state, distinguishing visits to the same position with different food remaining. My `foodHeuristic` scans the remaining pellets and returns the **largest Manhattan distance** from Pacman to a pellet:

```text
h(s) = max over remaining food f of (|x - f.x| + |y - f.y|)
```

Pacman must eventually reach even the farthest pellet, and walls can only increase the required distance. This provides a lower bound without running another maze search inside every heuristic call. With no food left, the estimate is zero.

```sh
python pacman.py -l tinySearch -p AStarFoodSearchAgent
```

My `ClosestDotSearchAgent` repeatedly selects the pellet with the smallest **Euclidean distance** from the current starting position, then runs BFS to that specific target. `AnyFoodSearchProblem.isGoalState` checks the selected pellet. Walls can make a visually nearby pellet farther away by maze distance, and repeated local choices do not optimize the complete food-collection route.

### Current search limitations

Parent-chain reconstruction assumes a reachable goal different from the start; start-at-goal and unreachable-goal cases need additional handling. The corner initializer also has a `startingposition` capitalization typo in its start-on-corner branch. These are limitations of the current code, separate from the algorithm ideas above.

## 2. Multi-agent search: planning around ghosts

### Reflex decisions

`ReflexAgent.evaluationFunction` evaluates immediate successors using score change, remaining food, nearest food or capsule distance, ghost distances, and scared timers.

When at least one ghost is active, its main expression is:

```text
4 * score_change + sum(scared_timers) - remaining_food - 2 * nearest_target_distance
```

If the sum of distances to ghosts is below five, I also add twice that sum to favor separation. When all ghosts are scared, the function switches to `4 * successor_score - current_score`. These hand-chosen terms balance food progress and avoidance, although summed ghost distance can hide the danger of one nearby ghost.

### Recursive game-tree search

My recursive functions track the agent index and remaining depth. Pacman is agent `0`; each ghost gets its own subsequent layer. Depth decreases when the last agent finishes and play returns to Pacman, so one depth unit represents a complete round of moves.

- **Minimax (`evals`):** maximize at Pacman nodes and minimize at every ghost node. This plans against ghosts choosing the worst outcome for Pacman.
- **Alpha-beta (`evalsa`):** carry lower and upper bounds through the max/min recursion. Stop a max branch when its value exceeds beta, or a min branch when its value falls below alpha. Comparisons are strict, so equality does not trigger pruning. A dictionary stores backed-up values for root action selection.
- **Expectimax (`evalse`):** maximize at Pacman nodes and average at ghost nodes, assigning each legal ghost action probability `1 / number_of_legal_actions`. This models uniformly random ghosts.

The recursion evaluates states at depth zero or when the current agent has no legal moves. Leaves use the game score by default; `evalFn=better` selects my custom state evaluation.

### My custom evaluation function

The active return expression in `betterEvaluationFunction` is:

```text
game_score + sum(Manhattan distances to ghosts) + sum(scared_timers) - remaining_food
```

If no food remains, it returns the game score. Nearest-food distance is also computed, but is not used in the final expression. This heuristic rewards score, food completion, and separation from ghosts; its distance term does not distinguish active ghosts from scared ghosts.

From `multiagent/`:

```sh
python pacman.py -l smallClassic -p ReflexAgent -f
python pacman.py -l smallClassic -p MinimaxAgent -a depth=2 -f
python pacman.py -l smallClassic -p AlphaBetaAgent -a depth=2 -f
python pacman.py -l smallClassic -p ExpectimaxAgent -a depth=2,evalFn=better -f
```

`-f` fixes the random seed for more reproducible comparisons. Alpha-beta's main benefit is reducing tree exploration; its gameplay may look similar to minimax. These evaluation functions are heuristics and do not guarantee wins.

## 3. Reinforcement learning: learning from rewards

### Value iteration with a known model

In `ValueIterationAgent`, I use the MDP's transition probabilities and rewards to perform a fixed number of Bellman backups:

```text
V_next(s) = max_a sum_s' T(s, a, s') * [R(s, a, s') + gamma * V_previous(s')]
```

Each iteration starts with a copy of the values. Every backup reads that copy, making the update synchronous: later states do not use values already changed during the same sweep. Terminal states are skipped. `computeQValueFromValues` calculates an action's expected return, and `computeActionFromValues` extracts the maximizing action, returning `None` at terminal states.

This implements value iteration followed by policy extraction. There is no separate policy-iteration implementation.

From `reinforcement/`:

```sh
python gridworld.py -a value -i 100 -k 1
```

### Tabular Q-learning without a transition model

`QLearningAgent` stores values in a `util.Counter` indexed by `(state, action)`, so unseen pairs begin at zero. Each observed transition updates:

```text
target = reward + gamma * max_a' Q(next_state, a')
Q(state, action) = (1 - alpha) * Q(state, action) + alpha * target
```

If the next state has no legal actions, the target is just the reward. Action selection is epsilon-greedy: explore with probability epsilon, otherwise choose the highest-valued action. Ties use the first maximizing action in legal-action order.

```sh
python gridworld.py -a q -k 100
python pacman.py -p PacmanQAgent -x 2000 -n 2010 -l smallGrid
```

In the Pacman example, the first 2,000 games train the agent and the final 10 evaluate it. The framework disables exploration and learning after training. Training games run without graphics; evaluation games are suitable for recording.

### Approximate Q-learning with shared features

`ApproximateQAgent` replaces individual table entries with a weighted feature sum:

```text
Q(s, a) = sum_i weight_i * feature_i(s, a)
error = reward + gamma * max_a' Q(next_state, a') - Q(state, action)
weight_i = weight_i + alpha * error * feature_i(state, action)
```

I obtain features through the configured extractor and update each active feature weight using the temporal-difference error. Shared features let experience transfer between different states with similar properties. The supplied `SimpleExtractor` includes food proximity, eating food, and ghosts one step away. The default `IdentityExtractor` instead identifies individual state-action pairs.

```sh
python pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l mediumGrid
```

The supplied crawler also uses the Q-learning interface:

```sh
python crawler.py
```

**Deep Q-learning status:** supporting DQN machinery exists in `deepQLearningAgents.py`, but network initialization, forward pass, loss, and gradient update in `model.py` remain placeholders. Deep Q-learning is unfinished.

## 4. Logic: constraints and entailment

In `logic/logic/logicPlan.py`, I construct propositional sentences using `Expr` and time-indexed symbols using `PropSymbolExpr`. My implemented helpers include:

- **Entailment:** negate the implication from premise to conclusion and ask the supplied SAT helper for a model. If no counterexample exists, the premise entails the conclusion.
- **At least one:** disjoin the literals.
- **At most one:** for every pair, add `not A or not B`, then conjoin the clauses. This excludes assignments with two true literals.
- **Exactly one:** combine the at-least-one and at-most-one constraints.

These constraints express a single position or action at a time. The SAT solver requires `pycosat` to run this module.

### SAT planning and inference

The successor axiom makes each position at time `t` equivalent to the disjunction of legal ways to enter it at `t-1`. `pacphysicsAxioms` combines wall exclusion, exactly one position, exactly one action, and optional movement and sensor models. `checkLocationSatisfiability` queries both a proposed location and its negation against the same facts.

`positionLogicPlan` incrementally extends the time horizon and asks whether the goal can be reached. `foodLogicPlan` also tracks a Boolean food variable per initial pellet: food persists unless Pacman occupies that cell. Testing horizons in increasing order finds a shortest satisfiable plan. Reachability bounds stop the search if no plan exists.

The `_KnowledgeBase` helper converts permanent constraints to integer CNF clauses once. Queries add temporary assumptions and call PicoSAT, avoiding repeated encoding of the entire movement history.

- **Localization:** with a known map, combine four-direction wall readings and actions, then retain every position consistent with the knowledge base.
- **Mapping:** begin with a known starting position and border walls. Infer whether each unknown cell must be a wall or open space using the four-direction sensor.
- **SLAM:** infer both the map and possible positions using a weaker sensor that reports the number of adjacent walls. Its movement model permits failed actions to leave Pacman in place.

Mapping records a cell only when its wall status is logically entailed; uncertain cells remain `-1`. Each generator incorporates a reading, updates its beliefs, advances the simulated agent, and yields the result for that timestep.

## 5. Probabilistic inference: beliefs about hidden ghosts

In `tracking/`, my implemented methods work with distributions over possible positions:

1. **Bayes-net construction:** define Pacman and ghost position variables, plus noisy-distance observations. Each observation depends on Pacman and its corresponding ghost.
2. **Factor joins:** collect variables, enumerate assignments, and multiply input probabilities for each assignment. Variables unconditioned in an input remain unconditioned in the result.
3. **Elimination:** remove an unconditioned variable by summing probabilities over its domain.
4. **Variable elimination:** incorporate evidence, join factors involving each elimination variable, sum it out when permitted, and normalize the final joined factor.
5. **Distribution helpers:** normalize nonzero total mass and sample keys using `random.choices` with their values as weights.
6. **Observation updates:** multiply prior beliefs by noisy-distance likelihoods, then normalize. A jailed ghost produces a `None` observation with probability one; a ghost outside jail cannot produce that observation.

The observation update follows:

```text
posterior(position) is proportional to
    prior(position) * P(observation | Pacman position, ghost position)
```

### Prediction, particle filtering, and ghost chasing

`ExactInference.elapseTime` propagates each old position's probability through the ghost transition model and sums contributions arriving at the same new position:

```text
predicted(new_position) = sum_old prior(old_position) * P(new_position | old_position)
```

`ParticleFilter` approximates this distribution with a fixed-size list of positions:

- Initialization cycles evenly through legal positions rather than drawing a random prior.
- Beliefs are normalized particle counts.
- Observation updates accumulate likelihood weights for every particle, so repeated positions receive proportionally more weight. Resampling draws the next particle population from those weights.
- If all observation weights are zero, the filter restores a uniform population.
- Prediction samples each particle's successor from the ghost transition distribution.

The observation model handles jailed ghosts through the `None` reading. `GreedyBustersAgent` selects the most likely position of each living ghost, chooses the nearest one by maze distance, then takes the legal action that gets closest to that target. With no target, it stops.

## Validation and compatibility

Each module includes Berkeley's autograder. Run it from the relevant module directory:

```sh
python autograder.py
```

Logic and tracking are tested with their supplied public autograders using `python -B autograder.py --no-graphics`. Both suites passed on Python 3.14.7: **Logic 25/25** (q1-q8) and **Tracking 25/25** (q1-q11). The final particle-filter gameplay check won **5/5** games above the required score. The tracking autograder uses `importlib` in place of the removed `imp` module for compatibility with current Python versions. Test questions and expected results were left unchanged.

A successful demo does not establish correctness on all algorithm edge cases. The reinforcement module still has an unfinished deep Q-network.

Documentation smoke checks with Python 3.14.7:

- A* with Manhattan distance completed `mediumMaze`: path cost **68**, **222** expanded nodes.
- Expectimax with `depth=2,evalFn=better` ran on `smallClassic` with a fixed seed, but lost that game with score **-64**.
- Gridworld's text-mode value-iteration demo failed in the supplied `textGridworldDisplay.py` formatter with `TypeError: list expected at most 1 argument, got 5`. Graphical Gridworld demos were not verified in this check.

These are individual smoke checks, not full autograder results or performance benchmarks.

## Suggested GIFs for GitHub

**Best first GIF: a side-by-side BFS and A* comparison on `mediumMaze`.** Show the highlighted search regions and Pacman's route, with short algorithm labels. Keep the maze, scale, and recording speed identical. Caption each run with its actual path cost and expanded-node count. This connects the implementation directly to a visible result.

| Suggested file | What to record | Placement |
| --- | --- | --- |
| `search-comparison.gif` | BFS versus A* using the search commands above, including expansion overlays | Below the introduction |
| `expectimax-gameplay.gif` | A short food-collection and ghost-avoidance sequence using `ExpectimaxAgent` | Multi-agent section |
| `qlearning-policy.gif` | A learned agent playing an evaluation game after training | Reinforcement-learning section |

Start with the search GIF and one gameplay GIF. Aim for an 8-15 second loop, crop to the game window, and export around 700-900 pixels wide at 12-15 fps. Add `--frameTime 0.1` to a Pacman command for readable gameplay speed. Keep each GIF to a few MB where practical. Use measured results in captions; do not imply learning improvement from an unrelated pair of games.

Save recordings under `assets/`. Once a file exists, embed it with:

```markdown
![BFS and A* exploring the same Pacman maze](assets/search-comparison.gif)
```

No GIF recordings are currently included. A tracking GIF showing beliefs concentrating around hidden ghosts is another option now that exact inference and particle filtering are implemented. Deep Q-learning remains unfinished.

## Attribution

Based on the [UC Berkeley CS188 Spring 2023 projects](https://inst.eecs.berkeley.edu/~cs188/sp23/projects/) and the [Berkeley AI Pacman projects](http://ai.berkeley.edu). The core projects and autograders were primarily created by John DeNero and Dan Klein, with student-side autograding contributions from Brad Miller, Nick Hay, and Pieter Abbeel. Original licensing and attribution notices remain in the source files.
