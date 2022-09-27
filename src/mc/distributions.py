from scipy import stats
import numpy as np
import collections
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.pyplot import MultipleLocator
from scipy.special import rel_entr

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

    Returns
    -------
    The histogram generated by this experiment is generated when alpha takes a different value or k takes a different value.

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
    
    
def binom(num_rounds, n, display = True):
    """
   Fit the model according to the given training data.

   Parameters
   ----------
   num_rounds : it represents the number of experiments.
      
   n : the number of nail plate layers.

   Returns
   -------
   The histogram obtained from the experiment.

   Notes
   -----
   """

    ### If there are 20 layers of nail plates and 21 drop slots on the nail board, use Monte Carlo's algorithm to solve the probability of the ball falling into each slot (simulating 100,000 times).

    import random
    def galtonBoard(num_rounds, n):
        history = []
        tracks = []
        for iter in range(num_rounds):
            position = 0 # 初始位置
            track = []
            for layer in range(n):
                position = position + random.choice([0, +1]) # 0 向左落，+1 向右落
                track.append(position)        
                tracks.append(track)
            history.append(position)        
        return history, tracks
    num_rounds = 500000
    n = 20
    hist, _ = galtonBoard(num_rounds, n)

    import collections
    c = collections.Counter(hist)
    
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    plt.figure(figsize = (10,3))
    plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.bar(c.keys(), c.values(), color = 'gray', edgecolor='black', linewidth=1.2)
    # plt.plot(list(c.keys()), list(c.values()))

    

    return [histogram]





def clt(N, dist=[], display = True):
    """
   Fit the model according to the given training data.

   Parameters
   ----------
   m : a random sampling of m is taken from a given arbitrarily distributed population at a time.
      
   N : number of experiments.

   Returns
   -------
   The resulting histogram when m takes a different value.

   Notes
   -----
   """  

    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import collections
    from scipy.stats import binom
    from tqdm import tqdm
    import numpy as np
 
    ### underlying distribution: uniform.
    for m in [1,2,5]:
        xbars = []
        for i in tqdm(range(10000)): # MC试验次数
            xbar = np.random.uniform(-1,1,m).mean()
            xbars.append(xbar)        
        plt.figure()
        plt.hist(xbars, density=False, bins=100, facecolor="none", edgecolor = "black")
        plt.title('m = ' + str(m))
        plt.yticks([])
        plt.show()

    ### underlying distribution: exponential.
    for m in [1,2,5,50]:
        xbars = []
        for i in tqdm(range(10000)): # MC试验次数
            xbar = np.random.exponential(scale = 1, size = m).mean()
            xbars.append(xbar)        
        plt.figure()
        plt.hist(xbars, density=False, bins=100, facecolor="none", edgecolor = "black")
        plt.title('m = ' + str(m))
        plt.yticks([])
        plt.show()
       
    return 
    

    
    

def exponential(p, N):
    """
  Fit the model according to the given training data.

   Parameters
   ----------
   p : during each experiment, the experiment fixes the probability of failure or accident.
      
   N : number of experiments.

   Returns
   -------
   Plot of probability of dying in n+1 rounds after surviving n rounds.

   Notes
   -----
   """

    ### The code defines a probability calculation function for survival.game (i.e. the probability of p mortality per turn, or the probability that the capacitance is broken per unit time survival_dist.

    import numpy
    from matplotlib import pyplot as plt

    # survival game.It has survived n rounds; dies in n+1 round. 
    def survival_dist(n,p):
        return pow((1-p),n)*p;
    N = 10000
    p = 0.001
    x = numpy.linspace(0,N,N+1)
    plt.plot(x,survival_dist(x,p))
    plt.show()
    
    return