import json
import random 

from conveyor import Conveyor
from diverter import Diverter, DIVERT, CONTINUE_STRAIGHT
from agent import Agent
from sink import Sink


def makeDiverterSelectorFn(station):
    def fn(box):
        return DIVERT if box.IsForStation(station) else CONTINUE_STRAIGHT
    return fn

def makeAgentDelayFn(fromDelay, toDelay):
    def fn():
        return random.randint(fromDelay, toDelay)
    return fn

def makeAgentMarkPickedFn(station):
    def fn(box):
        return box.Pick(station)
    return fn

with open('configuraions/wh.json') as f:
    data = json.load(f)

components = {} 

components['sink'] = ('sink', Sink('sink'))

for c in data['components']:
    type = c['type']
    if type == 'conveyor':
        newComponent = Conveyor(name = c['name'], 
                                capacity = c['capacity'], 
                                delay = c['delay'])
    elif type == 'diverter':
        newComponent = Diverter(name = c['name'], 
                                delay = c['delay'], 
                                selectorFn = makeDiverterSelectorFn(c['divertStation']))
    elif type == 'agent':
        newComponent = Agent(name = c['name'], 
                             delayFn = makeAgentDelayFn(c['minDelay'], c['maxDelay']), 
                             actionFn= makeAgentMarkPickedFn(c['markPicked']))
    else:
        print('Unknown component type:'+ type)

    components[c['name']] = (type, newComponent)

for conn in data['connections']:
    type, component = components[conn['from']]
    if type == 'conveyor':
        _, to = components[conn['to']]
        component.Connect(to.FirstPlace())
    elif type == 'diverter':
        _, to = components[conn['to']]
        _, divertTo = components[conn['divertTo']]
        component.Connect(to.FirstPlace(), divertTo.FirstPlace())
    elif type == 'agent':
        _, source = components[conn['source']]
        _, returnTo = components[conn['returnTo']]
        component.Connect(source, returnTo)
    else:
        print('Connections. Unknown component type:'+ type)