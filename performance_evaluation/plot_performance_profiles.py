import matplotlib.pyplot as plt
import json
from natsort import natsorted
from os import listdir
from os.path import isfile, join
import numpy as np

corrPaths = {
    'raritytools': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_train_vanilla',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_train_opt',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_test_vanilla',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_test_opt'
    },
    'kramer': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_train_vanilla',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_train_opt',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_test_vanilla',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_test_opt'
    },
    'openrarity': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_train_vanilla',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_train',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_vanilla50', #50
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_opt',
        'test_basic': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_basic50',
        'test_trait_count': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_trait_count50',
        'test_unique_trait_count': '/home/ubuntu/projects/unipro/models/rarity/openrarity_test_unique_trait_count50'
    },
    'nftgo': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/nftgo_corr_train_vanilla',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/nftgo_corr_test_vanilla'
    },
    'roar': {
        'train': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_train',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_train_opt99',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_test_vanilla',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_test_opt'
    }
}

def perf_prof(data, data_names, plot_name=None, tau_min=0.0, tau_max=0.35, npts=1000, filename=None):
    num_prob, num_method = data.shape

    # Compute the distances between optimal method and others for each problem
    dist = np.zeros((num_prob, num_method)) 
    for prob in range(num_prob):
        dist[prob] = abs(np.max(data[prob]) - data[prob])
                
    # Compute the cumulative rates of the distance being less than a fixed threshold
    rho = np.zeros((npts, num_method))
    tau = np.linspace(tau_min, tau_max, npts)
    for method in range(num_method):
        for k in range(npts):
            rho[k, method] = np.sum(dist[:, method] < tau[k]) / num_prob
    
    # make plot
    #colors = [ '#2D328F', '#F15C19',"#81b13c","#ca49ac","000000"]
    label_fontsize = 18
    legend_fontsize = 10
    tick_fontsize = 12
    linewidth = 1.7
    
    plt.figure(figsize=(10, 8))
    
    for method in range(num_method):
        #plt.plot(tau, rho[:, method], color=colors[method], linewidth=linewidth, label=data_names[method])
        plt.plot(tau, rho[:, method], linewidth=linewidth, label=data_names[method])
        
    plt.xlabel(r'$\tau$', fontsize=label_fontsize)
    plt.ylabel(r'$\rho_m(\tau)$', fontsize=label_fontsize)
    lgd = plt.legend(fontsize=legend_fontsize, frameon=False, bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.xticks(fontsize=tick_fontsize, color='lightsteelblue')
    plt.yticks(fontsize=tick_fontsize, color='lightsteelblue')
    ax = plt.gca()
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)
    bottom_side = ax.spines["bottom"]
    bottom_side.set_visible(False)
    left_side = ax.spines["left"]
    left_side.set_visible(False)
    if plot_name is not None:
        plt.title(plot_name, fontsize=label_fontsize)
    plt.grid(True, color='lightsteelblue')
    if filename is None:
        filename = 'plot.png'
    plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')

'''
# TRAIN
onlyfiles = natsorted([f for f in listdir(corrPaths['raritytools']['train_vanilla']) if isfile(join(corrPaths['raritytools']['train_vanilla'], f))])
raritytools_train_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['raritytools']['train_vanilla'] + '/' + filename, "r") as file:
        raritytools_train_vanilla.append(-json.load(file)['fun'])
raritytools_train_vanilla = np.array(raritytools_train_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['kramer']['train_opt']) if isfile(join(corrPaths['kramer']['train_opt'], f))])
kramer_train_opt = []
for filename in onlyfiles:
    with open(corrPaths['kramer']['train_opt'] + '/' + filename, "r") as file:
        kramer_train_opt.append(-json.load(file)['fun'])
kramer_train_opt = np.array(kramer_train_opt).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['openrarity']['train_vanilla']) if isfile(join(corrPaths['openrarity']['train_vanilla'], f))])
openrarity_train_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['openrarity']['train_vanilla'] + '/' + filename, "r") as file:
        openrarity_train_vanilla.append(-json.load(file)['fun'])
openrarity_train_vanilla = np.array(openrarity_train_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['nftgo']['train_vanilla']) if isfile(join(corrPaths['nftgo']['train_vanilla'], f))])
nftgo_train_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['nftgo']['train_vanilla'] + '/' + filename, "r") as file:
        nftgo_train_vanilla.append(-json.load(file)['fun'])
nftgo_train_vanilla = np.array(nftgo_train_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['roar']['train_opt']) if isfile(join(corrPaths['roar']['train_opt'], f))])
roar_train_opt = []
for filename in onlyfiles:
    with open(corrPaths['roar']['train_opt'] + '/' + filename, "r") as file:
        roar_train_opt.append(-json.load(file)['fun'])
roar_train_opt = np.array(roar_train_opt).reshape(len(onlyfiles), 1)

max_indices = []
for i in range(roar_train_opt.shape[0]):
    options = [roar_train_opt[i], nftgo_train_vanilla[i], openrarity_train_vanilla[i], raritytools_train_vanilla[i], kramer_train_opt[i]]
    max_indices.append(np.argmax(options))
    roar_train_opt[i] = np.max(options)
#print(max_indices)

data_names = ['Rarity.tools', 'KRAMER', 'OpenRarity', 'NFTGo', 'ROAR']
data = np.concatenate((raritytools_train_vanilla, kramer_train_opt, openrarity_train_vanilla, nftgo_train_vanilla, roar_train_opt), axis=1) 

perf_prof(data, data_names, tau_max=0.65, filename='corr_train.png')  
'''

'''
# TEST
onlyfiles = natsorted([f for f in listdir(corrPaths['raritytools']['test_vanilla']) if isfile(join(corrPaths['raritytools']['test_vanilla'], f))])
raritytools_test_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['raritytools']['test_vanilla'] + '/' + filename, "r") as file:
        raritytools_test_vanilla.append(-json.load(file)['fun'])
raritytools_test_vanilla = np.array(raritytools_test_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['kramer']['test_opt']) if isfile(join(corrPaths['kramer']['test_opt'], f))])
kramer_test_opt = []
for filename in onlyfiles:
    with open(corrPaths['kramer']['test_opt'] + '/' + filename, "r") as file:
        kramer_test_opt.append(-json.load(file)['fun'])
kramer_test_opt = np.array(kramer_test_opt).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['openrarity']['test_vanilla']) if isfile(join(corrPaths['openrarity']['test_vanilla'], f))])
openrarity_test_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['openrarity']['test_vanilla'] + '/' + filename, "r") as file:
        openrarity_test_vanilla.append(-json.load(file)['fun'])
openrarity_test_vanilla = np.array(openrarity_test_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['nftgo']['test_vanilla']) if isfile(join(corrPaths['nftgo']['test_vanilla'], f))])
nftgo_test_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['nftgo']['test_vanilla'] + '/' + filename, "r") as file:
        nftgo_test_vanilla.append(-json.load(file)['fun'])
nftgo_test_vanilla = np.array(nftgo_test_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['roar']['test_opt']) if isfile(join(corrPaths['roar']['test_opt'], f))])
roar_test_opt = []
for filename in onlyfiles:
    with open(corrPaths['roar']['test_opt'] + '/' + filename, "r") as file:
        roar_test_opt.append(-json.load(file)['fun'])
roar_test_opt = np.array(roar_test_opt).reshape(len(onlyfiles), 1)

max_indices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0]
for i in range(roar_test_opt.shape[0]):
    options = [roar_test_opt[i], nftgo_test_vanilla[i], openrarity_test_vanilla[i], raritytools_test_vanilla[i], kramer_test_opt[i]]
    roar_test_opt[i] = options[max_indices[i]]

data_names = ['Rarity.tools', 'KRAMER', 'OpenRarity', 'NFTGo', 'ROAR']
data = np.concatenate((raritytools_test_vanilla, kramer_test_opt, openrarity_test_vanilla, nftgo_test_vanilla, roar_test_opt), axis=1)

perf_prof(data, data_names, tau_max=0.6, filename='corr_test.png')  
'''


# OpenRarity heuristics
onlyfiles = natsorted([f for f in listdir(corrPaths['openrarity']['test_vanilla']) if isfile(join(corrPaths['openrarity']['test_vanilla'], f))])
openrarity_test_vanilla = []
for filename in onlyfiles:
    with open(corrPaths['openrarity']['test_vanilla'] + '/' + filename, "r") as file:
        openrarity_test_vanilla.append(-json.load(file)['fun'])
openrarity_test_vanilla = np.array(openrarity_test_vanilla).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['openrarity']['test_unique_trait_count']) if isfile(join(corrPaths['openrarity']['test_unique_trait_count'], f))])
openrarity_test_unique_trait_count = []
for filename in onlyfiles:
    with open(corrPaths['openrarity']['test_unique_trait_count'] + '/' + filename, "r") as file:
        openrarity_test_unique_trait_count.append(-json.load(file)['fun'])
openrarity_test_unique_trait_count = np.array(openrarity_test_unique_trait_count).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['openrarity']['test_trait_count']) if isfile(join(corrPaths['openrarity']['test_trait_count'], f))])
openrarity_test_trait_count = []
for filename in onlyfiles:
    with open(corrPaths['openrarity']['test_trait_count'] + '/' + filename, "r") as file:
        openrarity_test_trait_count.append(-json.load(file)['fun'])
openrarity_test_trait_count = np.array(openrarity_test_trait_count).reshape(len(onlyfiles), 1)

onlyfiles = natsorted([f for f in listdir(corrPaths['openrarity']['test_basic']) if isfile(join(corrPaths['openrarity']['test_basic'], f))])
openrarity_test_basic = []
for filename in onlyfiles:
    with open(corrPaths['openrarity']['test_basic'] + '/' + filename, "r") as file:
        openrarity_test_basic.append(-json.load(file)['fun'])
openrarity_test_basic = np.array(openrarity_test_basic).reshape(len(onlyfiles), 1)

data_names = ['OpenRarity: both meta traits', 'OpenRarity: Unique Trait Count', 'OpenRarity: Trait Count', 'OpenRarity: no meta traits']
data = np.concatenate((openrarity_test_vanilla, openrarity_test_unique_trait_count, openrarity_test_trait_count, openrarity_test_basic), axis=1)

perf_prof(data, data_names, tau_max=0.3, filename='corr_openrarity_heuristics.png') 
''''''
