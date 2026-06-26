import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

font_size = 14
plt.rcParams.update({"font.size": font_size})

plt.close("all")


#%%
def Black_Scholes(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    if option_type == "call":
        option_price = S0*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
    if option_type == "put":
        option_price = K*np.exp(-r*T)*stats.norm.cdf(-d2)-S0*stats.norm.cdf(-d1)

    return option_price

def European_option_simulation(S0, K, r, T, sigma, Z, moment_matching=False, option_type="call"):
    if moment_matching:
        Z = (Z-np.mean(Z, axis=0))/np.std(Z, axis=0)
        # 每個 column 計算平均數和標準差，做 moment matching。

    ST = S0*np.exp((r-0.5*sigma**2)*T+sigma*np.sqrt(T)*Z)

    if option_type == "call":
        payoff = np.maximum(ST-K, 0)
    if option_type == "put":
        payoff = np.maximum(K-ST, 0)

    option_prices = np.exp(-r*T)*np.mean(payoff, axis=0)

    return option_prices


#%%
# 參數設定
S0 = 100.0    
K = 100.0     
r = 0.02      
T = 0.5       

option_type = "call"
moment_matching = True

m_paths = 1000    
N = 1             

seed = 42
np.random.seed(seed)

random_type = "pseudo"

if random_type == "pseudo":
    u = np.random.rand(m_paths, N)
    Z = stats.norm.ppf(u)

if random_type == "np.random.randn":
    Z = np.random.randn(m_paths, N)

if random_type == "np.random.normal":
    Z = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))


#%%
# 探討不同波動率 sigma 對 European call option 模擬價格的影響
sigmas = np.linspace(0.1, 0.6, 26)

option_prices_mean = np.zeros(len(sigmas))
option_prices_for_loop_mean = np.zeros(len(sigmas))
option_prices_true = np.zeros(len(sigmas))

for i in range(len(sigmas)):
    sigma = sigmas[i]

    option_price_true = Black_Scholes(S0, K, r, T, sigma, option_type=option_type)
    option_prices = European_option_simulation(S0, K, r, T, sigma, Z,
                                               moment_matching=moment_matching,
                                               option_type=option_type)

    option_prices_true[i] = option_price_true
    option_prices_mean[i] = np.mean(option_prices)


#%%
# 使用 for 迴圈重新產生亂數，比較不同 for 迴圈寫法之結果
np.random.seed(seed)

for i in range(len(sigmas)):
    sigma = sigmas[i]

    if random_type == "pseudo":
        u_for_loop = np.random.rand(m_paths, N)
        Z_for_loop = stats.norm.ppf(u_for_loop)

    if random_type == "np.random.randn":
        Z_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_prices_for_loop = European_option_simulation(S0, K, r, T, sigma, Z_for_loop,
                                                        moment_matching=moment_matching,
                                                        option_type=option_type)

    option_prices_for_loop_mean[i] = np.mean(option_prices_for_loop)

#%%
# 圖：比較兩種 for 迴圈寫法之結果
plt.figure(figsize=(10, 6))

plt.plot(sigmas,
         option_prices_mean,
         color="blue",
         linewidth=2,
         linestyle="--",
         label="same Z")

plt.plot(sigmas,
         option_prices_for_loop_mean,
         color="blue",
         linewidth=2,
         linestyle="-",
         label="Z in for loop")

plt.xlabel(r"$\sigma$")
plt.ylabel("European call option price")
plt.title("European call option simulation price and volatility")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


#%%
"""
結論：

本程式的目的，是在假設股價服從 Geometric Brownian Motion (GBM) 的情況下，
使用蒙地卡羅模擬方法探討 European call option 模擬價格與波動率 sigma 之間的關係。
在模型中，股價到期值 ST 會受到標準常態亂數 Z 與波動率 sigma 的影響，因此當 sigma 改變時，
到期股價的分散程度也會改變，進而影響買權的 payoff 與選擇權價格。

本次參數設定為 S0 = 100、K = 100、r = 0.02、T = 0.5，代表初始股價與履約價格相同，
分析的是價平的 European call option；無風險利率設定為 2%，到期時間設定為半年。
這樣設定可以讓研究重點集中在波動率 sigma 對買權價格的影響，而不會受到價內或價外程度
過大的干擾。模擬路徑數 m_paths 設定為 1000，代表每一個 sigma 下會模擬 1000 個可能的
到期股價；N = 1 表示本次只進行一次重複實驗。亂數種子 seed = 42 是為了讓每次執行程式時
產生相同的亂數，使結果具有可重現性。

本程式將 sigma 設定為從 0.1 到 0.6，共取 26 個等距點。這個範圍包含低波動到較高波動的情況，
可以清楚觀察波動率上升時，European call option 模擬價格的變化趨勢。程式中使用 pseudo-random
numbers，先產生 uniform(0, 1) 亂數，再透過 stats.norm.ppf 轉換成標準常態亂數，這是上課內容中
使用過的亂數產生方式。另外，本程式固定 moment_matching = True，將每一組亂數樣本重新標準化，
使其平均數接近 0、標準差接近 1，以降低亂數抽樣誤差，使模擬結果更穩定。

由圖表可以看出，當 sigma 從 0.1 增加到 0.6 時，European call option 的蒙地卡羅模擬價格呈現
明顯上升趨勢。藍色實線是先產生同一批亂數 Z，再讓所有 sigma 共用同一批 Z，因此曲線較平滑；
藍色虛線則是把亂數產生放在 for 迴圈中，每一個 sigma 都重新抽一批亂數，因此曲線可能出現較明顯的
抽樣波動。這個差異來自 for 迴圈中亂數產生位置不同，而不是選擇權定價理論改變。

整體趨勢仍符合選擇權定價的金融直覺：買權的 payoff 為 max(ST-K, 0)，當股價下跌時，
買權最大的損失只是不履約，payoff 最低為 0；但當股價上漲時，payoff 會隨著 ST-K 增加。
因此，較高的波動率會使到期股價分布更分散，增加股價大幅上漲的可能性，也就提高了買權的期望 payoff。
在折現後，European call option 的價格也會隨著 sigma 上升而增加。

綜合而言，本次模擬結果顯示，在其他參數固定時，波動率 sigma 是影響 European call option 價格的
重要因素，且兩者呈現正向關係。這也說明在 GBM 假設與風險中立評價下，蒙地卡羅模擬可以用來觀察
選擇權價格對參數變化的敏感度，並幫助理解波動率對買權價值的影響。
"""
