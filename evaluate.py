import numpy as np
import matplotlib.pyplot as plt
import math 
#from utils import plot, getInternalStateAsNumPy, stateAsNumPy
from warehouse import Warehouse
from box import BoxListFromFile
from policies import HeuristicPolicy, StateFullHeuristicPolicy, RLPolicy


def save_items_statistics(items, file):
    pass 
    # nitems = len(items)
    # stats1 = np.asarray([items[i].startTime for i in range(len(items))]).reshape(nitems, 1)
    # stats2 = np.asarray([items[i].finishTime for i in range(len(items))]).reshape(nitems, 1)
    # stats = np.hstack((stats1, stats2))
    # np.save(file, stats)
    #print(f'min={np.min(processing_times)}, max={np.max(processing_times)}, mean={np.mean(processing_times)}, std={np.std(processing_times)}')

datafolder = 'data/eval'
datafiles = [
    '1_001box.txt',    
    '2_003boxes.txt',  
    '3_030boxes.txt',  
    '4_049boxes.txt',  
    '5_116boxes.txt',  
    '6_816boxes.txt'
]

#w = Warehouse('test', 'files/wh1.txt', None)
#w = Warehouse('test', 'files/wh1_deterministic_pickers.txt', None)
#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
w = Warehouse('test', 'configurations/wh.json', None)
#w = Warehouse('test', 'files/wh1_combined_agents_p50_q5.txt', None)
#w = Warehouse('test', 'files/wh1_faster_agents.txt', None)
#w = Warehouse('test', 'files/wh1_even_slower_agents.txt', None)


policies = [
    HeuristicPolicy(burstSize=1, waitBetweenBoxes = 0, waitBetweenBursts=0), 
#    HeuristicPolicy(burstSize=5, waitBetweenBoxes = 1, waitBetweenBursts=8), 
    StateFullHeuristicPolicy(coefC1 = 10, coefC2 = 10, fillMargin = 0.4), 
#    RLPolicy('models/best-old-reward-function.onnx'), 
#    RLPolicy('models/best.onnx'), 
    #RLPolicy('models/best_robust_target.onnx'),
    #RLPolicy('models/best_robust_min_processing_time.onnx'),
    #RLPolicy('models/trained_policy_network_400.onnx'),
    RLPolicy('models/trained_policy_network_500.onnx')
    ]

policy_names = [
    'heuristic_1_0_0',
#    'heuristic_5_1_8',
    'C1C2_0.4', 
#    'rl_old_RF',
#    'rl_best',
    #'latest_robust',
    #'min-per-item',
    #'latest 400 ep',
    'RL_Best'
]

sorts = ['iid', '1,2,3', '2,1,3', '3,2,1']

show_plots = False  


plt.rc('font', size=8) 
plt.rcParams["figure.figsize"] = [8, 8]
plt.rcParams["figure.autolayout"] = True

nxplots = int(math.sqrt(len(datafiles)))
nyplots = len(datafiles) - nxplots

if nyplots == 0:
    nyplots = 2

fig, axes = plt.subplots(nxplots, nyplots, sharex=True, sharey=True, constrained_layout=True)
#fig.set_size_inches(5, 5)

for ax in axes.flat:
    ax.set_visible(False)

for ax, datafile in zip(axes.flat, datafiles):
    ax.set_visible(True)
    summary = np.zeros(shape=(len(policies), 4), dtype=int)
    summary_avg_total = np.zeros(shape=(len(policies), 4), dtype=float)
    for ix, (policy, policy_name) in enumerate(zip(policies, policy_names)):
        print('---s---------------------')
        items = BoxListFromFile(f'{datafolder}/{datafile}')
        for sorttype, sorttypestr in enumerate(sorts):
            if sorttype == 1:
                items.sort(reverse=False, key=lambda b: b.route)
            elif sorttype == 2:
                items.sort(reverse=True, key=lambda b: 1 if b.route == 2 else 0 )
            elif sorttype == 3:
                items.sort(reverse=True, key=lambda b: b.route)
                
            state, remaining_items, actions_mask = w.reset(items)

            
            npstate = np.zeros(len(state)-2)
            normalizedState =  np.zeros(len(state)-2)
            fullInternalState = w.GetDetailedState()

            ctime = 0 
            while True:

                action = policy(ctime, normalizedState, remaining_items)
                state, reward, terminated, truncated, (info, remaining_items, actions_mask, avgPickTime) = w.step(action)
                #print(ctime, reward, terminated, truncated)
                normalizedState = state[1:-1]
                #normalizedState[0] = action 
                npstate = np.vstack((npstate, normalizedState))
            
                instate = w.GetDetailedState()

                fullInternalState = np.vstack((fullInternalState, instate))

                if terminated:
                    title = f'OK. T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                    print(title)
                    summary[ix, sorttype] = avgPickTime
                    summary_avg_total[ix, sorttype] = (1.0 * ctime) /len(items)
                    np.save(f'vis/full_state_{policy_name}_{sorttypestr}', fullInternalState)
                    #if show_plots:
                    #    plot(title, npstate, sorted_components)  
                    save_items_statistics(items, f'vis/item_stats_{datafile}_{policy_name}_{sorttypestr}')     
                    break
                    
                elif truncated:
                    title = f'Failed. {info} T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                    print(title)
                    #if policy_name == 'latest':
                    #    plot(title, npstate, sorted_components)
                    break 

                ctime += 1
            

    failed_value = int(1.5 * np.max(summary))

    summary[summary == 0] = failed_value

    failed_value = 1.5 * np.max(summary_avg_total)

    summary_avg_total[summary_avg_total == 0] = failed_value

    #heatmap_val = summary 
    heatmap_val = summary_avg_total 
  
    #fig, ax = plt.subplots()
    im = ax.imshow(heatmap_val, cmap='inferno_r')

    # Show all ticks and label them with the respective list entries
    ax.set_yticks(np.arange(len(policy_names)))
    ax.set_yticklabels(policy_names)

    ax.set_xticks(np.arange(len(sorts)))
    ax.set_xticklabels(sorts)

    # Loop over data dimensions and create text annotations.
    
    avg = np.mean(heatmap_val)

    nitems = len(items)

    for i in range(len(policy_names)):
        for j in range(len(sorts)):
            v = heatmap_val[i, j]
            if v <= avg:
                c = 'k'
            else:
                c = 'w'

            if v == failed_value:
                v = 'F'
            else:
                v1 = summary[i, j]
                v2 = summary_avg_total[i, j]
                v = f'{v1:.0f}\n{v2:.2f}'
        
            text = ax.text(j, i, v,
                        ha='center', va='center', color=c)

    ax.set_title(f'{datafile}')


#fig.tight_layout()
#lt.show()
plt.tight_layout()
plt.show()
        