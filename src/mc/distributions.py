import collections
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.pyplot import MultipleLocator
from scipy.special import rel_entr
from scipy import stats
from tqdm import tqdm

def zipf(num_rounds = 10000, num_clips_k = 1.6, verbose = False):
    
    """
    The Zipf law / distribution is published in 1949 by Harvard linguist George Kingsley Zipf. 
    It can be expressed as follows: in the corpus of natural language, 
    the frequency of a word appears inversely proportional to its ranking 
    in the frequency table. 
    The experiment associated with this law is the paper clip experiment, 
    that is, two paper clips are randomly drawn and connected together, 
    then put back, and then do the above again. 
    After enough rounds, the clips of different lengths will obey zipf distribution. 

    Parameters
    ----------
    num_rounds : The number of random samples. 抽样拼接次数

    num_clips_k : The total number of paper clips should be greater than [num_rounds]. This is the ratio of the numbers. 
    Should always > 1. Some of values are 1.6, 1.8, 2, 2.5, 3.

    Note
    ----
    Internally, we use grid search via the KLD metric to determine the best-fit zipf dist. 
    """ 
    
    if num_clips_k <= 1:
        print('Error: num_clips_k must > 1')
        return

    num_clips = int(num_rounds*num_clips_k) # clip总数，应大于抽样拼接次数，i.e., k > 1
    history = []
    sets = [1]*num_clips    
    for iter in range(num_rounds):
        idx1, idx2 = np.random.choice(range( len(sets)), 2, replace = False)
        # print(idx1, idx2)
        sets[idx1] = sets[idx1] + sets[idx2]
        sets.pop(idx2)
    c = collections.Counter(sets)
    plt.figure(figsize = (10,3))
    plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    vals = np.array(list(c.values())) 
    vals = vals / vals.sum()
    plt.bar(c.keys(), vals, color = 'gray', edgecolor='black')
    plt.title("Frequency Histogram\nclips=" + str(num_clips) + ", rounds=" + str(num_rounds) + ", k=" + str(num_clips_k))
    plt.show()

    kld = np.inf
    best_pwr = 1/2
    x = list(c.keys()) 

    for pwr in [1/6, 1/3, 1/2, 2/3, 1, 3/2]: # this is an inexact fitting

        a = num_clips_k ** (pwr)
        kldn = sum(rel_entr(vals, stats.zipf.pmf(x, a))) # KLD

        if verbose:
            print("Previous and new KLD between experiment and theory: ", round(kld,3), round(kldn,3) )
        if kldn < kld:
            kld = kldn
            best_pwr = pwr
    
    a = num_clips_k ** (best_pwr)
    
    plt.figure(figsize = (10,3))
    x = range(np.array(list(c.keys())).min(), np.array(list(c.keys())).max() + 1) # np.arange(zipf.ppf(0.01, a), zipf.ppf(0.99, a)) 
    plt.bar(x, stats.zipf.pmf(x, a), color = 'gray', edgecolor='black')
    # plt.plot(x, zipf.pmf(x, a), 'bo', ms=8, label='zipf pmf')
    # plt.vlines(x, 0, zipf.pmf(x, a), colors='b', lw=5, alpha=0.5)
    ax=plt.gca()
    ax.xaxis.set_major_locator(MultipleLocator(1)) # use interger ticks
    plt.title('Theoretical Distribution\nzipf(alpha = '+str(round(a,2)) + ')')
    plt.show()
    
    
def binom(num_layers = 20, N = 5000, flavor = 1, display = True):

    """
    The Galton board is a physical model of the binomial distribution. 
    When samples are sufficient, you can also observe CLT. 

    If there are [num_layers] layers of nail plates, the number of nails in each layer increases from the beginning one by one, 
    And the nail plates have [num_layers+1] corresponding grooves under them. 
    This function solves the probability (N times) for a ball falling into each slot by using Monte Carlo's algorithm.

    Parameters
    ----------
    num_layers : The number of nail plate layers.
    N : Number of experiments.
    flavor : 1 or 2. Which implementation to use.

    Returns
    -------
    A [num_layers+1] long vector : Freqency Historgm, i.e., the number of balls that fall into each slot.
    """

    if display:
        plt.figure(figsize = (10,3))
        plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))

    result = [0 for i in range(num_layers + 1)]

    if flavor == 1:        
        for i in range (N):
            pos = 0
            for j in range (num_layers):
                if random.random() > 0.5:
                    pos += 1
            result [pos] += 1
        
        if display:
            plt.bar(range(num_layers+1), result, color = 'gray', linewidth=1.2, edgecolor='black')

    else:

        history = []
        for iter in range(N):
            position = 0 # 初始位置
            for layer in range(num_layers):
                position = position + random.choice([0, +1]) # 0 向左落，+1 向右落
            history.append(position)
        c = collections.Counter(history)
        for pair in zip(c.keys(), c.values()):
            result[pair[0]] = pair[1]

        if display:
            plt.bar(c.keys(), c.values(), color = 'gray', linewidth=1.2, edgecolor='black')
        
    if display:
        plt.title("Frequency Histogram\nlayers=" + str(num_layers) + ", balls=" + str(N) +")")
        plt.show()

        plt.figure(figsize = (10,3))
        plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))

        n = num_layers
        p = 0.5    

        x = range(num_layers+1)
        plt.plot(x, stats.binom.pmf(x, n, p), 'k+', ms=1, label='b (' + str(n) + ',' + str(p) + ')')
        plt.legend()
        plt.title('Theoretical Distribution\nbinomial(n='+str(n) + ',p='+ str(p) + ')')
        plt.bar(x, stats.binom.pmf(x, n, p), color='gray', linewidth=1.2, edgecolor='black')
        plt.show()

    return result
    

def exponential(num_rounds = 1000, p = 0.01, N = 10000):
    """
    元器件寿命为何符合指数分布？  
    定义一个survival game（即每回合有p的死亡率；或电容在单位时间内被击穿的概率）的概率
    取p = 0.001（每回合很小的死亡率），绘制出pmf曲线（离散、等比数组）

    This code defines the probability calculation function of the survival game.
    (e.g. a mortality rate of [p] per turn, or a capacitor having a probability of [p] being broken down per unit of time).

    Parameters
    ----------
    num_rounds : survial game rounds
    p : The probability of suddent death / failure / accident for each round
    N : players / sample count / MC simulations
    
    Returns
    -------
    Plot of survival histogram.
    """

    survival_rounds = []
    for player in range(N):
        fate = random.choices([0,1], weights=(1-p,p), k = num_rounds)
        if 1 in fate:
            survival_rounds.append(fate.index(1))
        # else: # still lives, i.e., > num_rounds
        #     survival_rounds.append(num_rounds)
            
    c = collections.Counter(survival_rounds)

    plt.figure(figsize = (10,3))
    # plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.bar(c.keys(), c.values(), color = 'gray', edgecolor='black')
    plt.title("Frequency Histogram\nper-round sudden death probality p=" + str(p) + ', players = ' + str(N))
    plt.show()

    '''
    # survival game.It has survived n rounds; dies in n+1 round. 
    def survival_dist(n,p):
        return pow((1-p),n)*p

    plt.figure(figsize = (10,3))
    # plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    x = linspace(0,num_rounds,num_rounds+1)
    plt.plot(x, survival_dist(x,p))
    plt.title("Theoretical Distribution\nsurvival PMF" )
    plt.show()
    '''

    plt.figure(figsize = (10,3))    
    theta = round(1 / p + 0.5)
    plt.title('Theoretical Distribution\nexponential(θ='+ str(theta) + ')')  
    # pmf: Probability mass function. i.e. pdf
    # ppf: Percent point function (inverse of cdf — percentiles).
    # x = np.arange(stats.expon.ppf(q=0.001, scale=theta), stats.expon.ppf(q=0.999, scale=theta))
    x = range(np.array(list(c.keys())).min(), np.array(list(c.keys())).max() + 1) 
    plt.plot(x,stats.expon.pdf(x=x, scale=theta))
    # plt.show();
    # plt.plot(x,expon.cdf(x=x, scale=s))
    # plt.plot(x,expon.sf(x=x, scale=s)) # when s = 1, sf and pdf overlaps
    plt.show() 
   

  