from psychsim.reward import *
from psychsim.pwl import *
from psychsim.action import *
from psychsim.world import *
from psychsim.agent import *
import psychsim.probability


world = World()
world.defineState(None,'round',int)
world.setState(None,'round',0)

banker = Agent('Banker')
world.addAgent(banker)
world.defineState(banker.name,'pool',int)
world.setState(banker.name,'pool',0)

distribute = banker.addAction({'verb': 'distribute'})
actors = []

for i in range(4):
    actor = Agent('Agent'+str(i))
    world.addAgent(actor)
    actor.setHorizon(5)
    world.defineState(actor.name,'money',float)

    # Start with one money unit
    actor.setState('money',1.)

    # Don't give
    action = actor.addAction({'verb': 'pass'})
    tree = makeTree(incrementMatrix(stateKey(None,'round'),1))
    world.setDynamics(stateKey(None,'round'),action,tree)

    # Donate
    action = actor.addAction({'verb': 'contribute'})
    tree = makeTree(incrementMatrix(stateKey(None,'round'),1))
    world.setDynamics(stateKey(None,'round'),action,tree)

    # Remove money from agent
    tree = makeTree(incrementMatrix(stateKey(actor.name,'money'),-1))
    world.setDynamics(stateKey(actor.name,'money'), action, tree)

    # Add money to pool
    tree = makeTree(incrementMatrix(stateKey(banker.name,'pool'),1))
    world.setDynamics(stateKey(banker.name, 'pool'), action, tree)

    # After each round, the banker distributes 90% of the pool value to every agent
    tree = makeTree(addFeatureMatrix(stateKey(actor.name,'money'),stateKey(banker.name, 'pool'),0.9))
    world.setDynamics(stateKey(actor.name, 'money'),distribute,tree)

    actor.setReward(maximizeFeature(stateKey(actor.name, 'money')),1.0)
    #actor.setReward(maximizeFeature(stateKey(banker.name, 'pool')),1.0)

    # TODO models
    '''
    actor.addModel('Level0',R={},level=0,rationality=10.,selection='distribution')
    actor.addModel('Level1',R={},level=1,rationality=10.,selection='distribution')
    actor.addModel('Level2',R={},level=2,rationality=10.,selection='distribution')

    for j in range(4):
        if not i == j:
            world.setMentalModel('Agent'+str(i),'Agent'+str(j),0.5)
        else:
            pass
    '''
    actors.append(actor)

# TODO Punish
for i in range(4):
    for j in range(4):
        if not i == j:
            me = actors[i]
            other = actors[j]
            action = me.addAction({'verb': 'punish', 'object': other.name})
            tree = makeTree(setToConstantMatrix(stateKey(other.name,'money'),0))
            world.setDynamics(stateKey(other.name,'money'),action,tree)
        else:
            pass



# Max rounds
world.addTermination(makeTree({'if': thresholdRow(stateKey(None,'round'),20),
                                True: True,
                                False: False}))

world.setOrder(['Agent0', 'Agent1', 'Agent2', 'Agent3', 'Banker'])
#world.setOrder([set(world.agents.keys())])

while not world.terminated():
    result = world.step()
    world.explain(result, 2)

    # print agent money
    moneys = {}
    for i in range(4):
        me = actors[i]
        moneys[i]=str(world.getState(me.name,'money').domain()[0])
    print moneys
    print('Banker pool: ' + str(world.getState('Banker', 'pool').domain()[0]))
