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


#%%
# 模擬股價路徑
# 隨機過程法
def GBM_stochastic_process_simulation(S0, r, T, sigma, Z):
    NumPaths, n = Z.shape
    dt = T/n
    S = np.zeros((NumPaths, n+1))
    S[:,0] = S0
    mu = r-0.5*sigma**2
    for j in range(n):
        S[:,j+1] = S[:,j]*np.exp(mu*dt+sigma*np.sqrt(dt)*Z[:,j])
        # 這是 Q 測度 (隨機過程的符號) (風險中立測度)
    return S


#%%
def Barrier_European_call_simulation(S, K, r, T, barrier, barrier_type="down-and-out"):
    ST = S[:,-1]
    path_min = np.min(S, axis=1)
    call_payoff = np.maximum(ST-K, 0)

    if barrier_type == "down-and-out":
        payoff = call_payoff*(path_min > barrier)

    if barrier_type == "down-and-in":
        payoff = call_payoff*(path_min <= barrier)

    option_price = np.exp(-r*T)*np.mean(payoff)

    return option_price


#%%
# 參數設定
S0 = 100.0
K = 100.0
r = 0.02
T = 0.5
sigma = 0.2

option_type = "call"
moment_matching = True

m_paths = 1000

time_intervals_year = 252
dt = 1/time_intervals_year
n = int(T/dt)
# 時間分割區間數 (或一條 path 之模擬亂數)
# dt = T/n

seed = 42
np.random.seed(seed)

random_type = "pseudo"

if random_type == "pseudo":
    u = np.random.rand(m_paths, n)
    Z = stats.norm.ppf(u)

if random_type == "np.random.randn":
    Z = np.random.randn(m_paths, n)

if random_type == "np.random.normal":
    Z = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, n))

if moment_matching:
    Z = (Z-np.mean(Z, axis=0))/np.std(Z, axis=0)
    # 每個 column 計算平均數和標準差，做 moment matching。


#%%
# 使用 GBM 模擬股價路徑
S_GBM = GBM_stochastic_process_simulation(S0, r, T, sigma, Z)


#%%
# 探討不同 barrier level 對 Barrier European call option 模擬價格的影響
barriers = np.linspace(60, 99, 40)

down_and_out_prices = np.zeros(len(barriers))
down_and_in_prices = np.zeros(len(barriers))
down_and_out_for_loop_prices = np.zeros(len(barriers))
down_and_in_for_loop_prices = np.zeros(len(barriers))
european_call_prices = np.zeros(len(barriers))

european_call_price_simulation = np.exp(-r*T)*np.mean(np.maximum(S_GBM[:,-1]-K, 0))
european_call_price_true = Black_Scholes(S0, K, r, T, sigma, option_type=option_type)

for i in range(len(barriers)):
    barrier = barriers[i]

    down_and_out_price = Barrier_European_call_simulation(S_GBM, K, r, T, barrier,
                                                          barrier_type="down-and-out")

    down_and_in_price = Barrier_European_call_simulation(S_GBM, K, r, T, barrier,
                                                         barrier_type="down-and-in")

    down_and_out_prices[i] = down_and_out_price
    down_and_in_prices[i] = down_and_in_price
    european_call_prices[i] = european_call_price_simulation


#%%
# 使用 for 迴圈重新產生亂數與股價路徑，比較不同 for 迴圈寫法之結果
np.random.seed(seed)

for i in range(len(barriers)):
    barrier = barriers[i]

    if random_type == "pseudo":
        u_for_loop = np.random.rand(m_paths, n)
        Z_for_loop = stats.norm.ppf(u_for_loop)

    if random_type == "np.random.randn":
        Z_for_loop = np.random.randn(m_paths, n)

    if random_type == "np.random.normal":
        Z_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, n))

    if moment_matching:
        Z_for_loop = (Z_for_loop-np.mean(Z_for_loop, axis=0))/np.std(Z_for_loop, axis=0)

    S_GBM_for_loop = GBM_stochastic_process_simulation(S0, r, T, sigma, Z_for_loop)

    down_and_out_for_loop_price = Barrier_European_call_simulation(S_GBM_for_loop, K, r, T, barrier,
                                                                   barrier_type="down-and-out")

    down_and_in_for_loop_price = Barrier_European_call_simulation(S_GBM_for_loop, K, r, T, barrier,
                                                                  barrier_type="down-and-in")

    down_and_out_for_loop_prices[i] = down_and_out_for_loop_price
    down_and_in_for_loop_prices[i] = down_and_in_for_loop_price


#%%
# 圖：比較 Barrier European call option 模擬價格與 barrier level 之關係
plt.figure(figsize=(10, 6))

plt.plot(barriers,
         down_and_out_prices,
         color="blue",
         linewidth=2,
         linestyle="--",
         label="down-and-out call, same paths")

plt.plot(barriers,
         down_and_out_for_loop_prices,
         color="blue",
         linewidth=2,
         linestyle="-",
         label="down-and-out call, paths in for loop")

plt.plot(barriers,
         down_and_in_prices,
         color="red",
         linewidth=2,
         linestyle="--",
         label="down-and-in call, same paths")

plt.plot(barriers,
         down_and_in_for_loop_prices,
         color="red",
         linewidth=2,
         linestyle="-",
         label="down-and-in call, paths in for loop")

plt.plot(barriers,
         european_call_prices,
         color="gray",
         linewidth=2,
         linestyle=":",
         label="European call simulation price")

plt.xlabel("barrier level")
plt.ylabel("option price")
plt.title("Barrier European call option simulation price and barrier level")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


#%%
"""
結論：

本程式的目的，是在假設股價服從 Geometric Brownian Motion (GBM) 的情況下，
使用蒙地卡羅模擬方法探討 Barrier European call option 的模擬價格與 barrier level
之間的關係。上課內容中介紹的障礙選擇權，是在一般 European option 的基礎上加入
障礙水準 barrier；當股價路徑在存續期間觸及或未觸及 barrier 時，選擇權會依照
knock-out 或 knock-in 的設定失效或生效。

本程式採用上課內容中的 down-and-out European call 與 down-and-in European call
作為比較對象。Down-and-out call 表示只要股價路徑曾經跌破 barrier，選擇權就失效；
down-and-in call 則相反，表示股價路徑必須曾經跌破 barrier，選擇權才會生效。
因此兩者的差異關鍵不只在到期股價 ST 是否高於履約價格 K，也在整條 GBM 股價路徑
期間是否碰到 barrier。

參數設定方面，本程式設定 S0 = 100、K = 100、r = 0.02、T = 0.5、sigma = 0.2，
代表初始股價與履約價格相同，分析的是價平的 European call option；無風險利率為 2%，
到期時間為半年，波動率為 20%。模擬路徑數 m_paths 設為 1000，並使用一年 252 個交易日
作為時間切割基準，因此半年共有 126 個時間區間。這樣設定可以讓程式在每條路徑中觀察
股價是否曾經跌破 barrier，而不是只看最後一期的到期股價。

亂數設定方面，本程式固定 seed = 42，使每次執行時產生相同亂數結果，方便重現圖表。
亂數產生方式使用 pseudo-random numbers，先產生 uniform(0, 1) 亂數，再利用
stats.norm.ppf 轉換為標準常態亂數，這延續了上課內容中模擬 European option 時的寫法。
此外，程式設定 moment_matching = True，將每一個時間點的亂數樣本重新標準化，使其平均數
接近 0、標準差接近 1，以降低蒙地卡羅抽樣誤差。

本程式同時比較兩種 for 迴圈寫法。第一種是先產生同一批 GBM 股價路徑，再用這批路徑計算
所有 barrier level 下的價格，因此不同 barrier 之間使用的亂數來源一致，曲線會比較平滑，
圖中以虛線表示。第二種是把亂數與 GBM 路徑的產生放在 for 迴圈中，每一個 barrier level
都重新模擬一批股價路徑，因此曲線除了反映 barrier level 的影響，也會包含蒙地卡羅抽樣誤差，
圖中以實線表示。

由圖表可以觀察到，當 barrier level 較低時，股價路徑跌破 barrier 的機率較小，因此
down-and-out call 比較不容易被 knock out，價格會接近一般 European call 的模擬價格；
同時，down-and-in call 因為比較不容易被 knock in，所以價格會較低。當 barrier level
逐漸上升並接近 S0 = 100 時，股價路徑碰到 barrier 的機率增加，down-and-out call
越容易失效，因此價格下降；相反地，down-and-in call 越容易生效，因此價格上升。

圖中的灰色點線代表一般 European call 的模擬價格，作為比較基準。藍色虛線與紅色虛線
使用同一批股價路徑，因此可以較清楚看出 down-and-out 與 down-and-in 的互補關係；
在相同股價路徑與相同 barrier level 下，兩者的價格加總會接近一般 European call 的價格。
藍色實線與紅色實線則因為每一個 barrier 都重新抽樣，所以曲線會比較抖動，但整體趨勢仍然
與平滑線一致。這說明抖動主要來自蒙地卡羅抽樣誤差，而不是障礙選擇權的定價邏輯改變。

這也符合上課內容中對 knock-out 與 knock-in 障礙選擇權的解釋：障礙條件並不是改變
call payoff 本身，而是決定這個 payoff 是否生效。

綜合而言，本次模擬結果顯示 barrier level 是影響 Barrier European call option 價格的重要因素。
障礙水準越接近初始股價，越容易被觸發，因此 down-and-out call 的價格會降低，
down-and-in call 的價格會提高。這說明在 GBM 假設下，蒙地卡羅模擬不只可以用來估計一般
European option，也可以處理與整條股價路徑相關的 path-dependent option，例如 Barrier option。
"""
