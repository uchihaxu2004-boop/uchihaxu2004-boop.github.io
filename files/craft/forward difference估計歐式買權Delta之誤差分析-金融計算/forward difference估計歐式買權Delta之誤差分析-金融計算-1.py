import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

plt.close("all")

font_size = 14
plt.rcParams.update({"font.size": font_size})


#%%
def Black_Scholes(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    if option_type == "call":
        option_price = S0*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
    if option_type == "put":
        option_price = K*np.exp(-r*T)*stats.norm.cdf(-d2)-S0*stats.norm.cdf(-d1)

    return option_price

def Black_Scholes_Delta(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    if option_type == "call":
        Delta = stats.norm.cdf(d1)
    if option_type == "put":
        Delta = -stats.norm.cdf(-d1)

    return Delta

def European_option_simulation(S0, K, r, T, sigma, Z,
                               moment_matching=False,
                               option_type="call"):
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
sigma = 0.2

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
# Analytical Delta
delta_true = Black_Scholes_Delta(S0, K, r, T, sigma, option_type=option_type)

# h 由很小到較大，觀察 forward difference 模擬 Delta 的變化
hs = np.logspace(-16, 1, 100)

delta_simulation = np.zeros(len(hs))
delta_simulation_for_loop = np.zeros(len(hs))
error = np.zeros(len(hs))
error_for_loop = np.zeros(len(hs))

for i in range(len(hs)):
    h = hs[i]

    option_price_up = European_option_simulation(S0+h, K, r, T, sigma, Z,
                                                 moment_matching=moment_matching,
                                                 option_type=option_type)

    option_price = European_option_simulation(S0, K, r, T, sigma, Z,
                                              moment_matching=moment_matching,
                                              option_type=option_type)

    delta_simulation[i] = np.mean((option_price_up-option_price)/h)
    error[i] = np.abs((delta_simulation[i]-delta_true)/delta_true)


#%%
# 在 for 迴圈中，每一個 h 重新產生亂數，觀察抽樣波動
np.random.seed(seed)

for i in range(len(hs)):
    h = hs[i]

    if random_type == "pseudo":
        u_for_loop = np.random.rand(m_paths, N)
        Z_for_loop = stats.norm.ppf(u_for_loop)

    if random_type == "np.random.randn":
        Z_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_price_up_for_loop = European_option_simulation(S0+h, K, r, T, sigma, Z_for_loop,
                                                          moment_matching=moment_matching,
                                                          option_type=option_type)

    option_price_for_loop = European_option_simulation(S0, K, r, T, sigma, Z_for_loop,
                                                       moment_matching=moment_matching,
                                                       option_type=option_type)

    delta_simulation_for_loop[i] = np.mean((option_price_up_for_loop-option_price_for_loop)/h)
    error_for_loop[i] = np.abs((delta_simulation_for_loop[i]-delta_true)/delta_true)


#%%
# 圖：模擬 Delta 與誤差
plt.figure(figsize=(8, 6))

plt.subplot(2, 1, 1)
plt.axhline(y=delta_true,
            color="gray",
            label="True Delta",
            linewidth=2)
plt.plot(hs,
         delta_simulation,
         color="blue",
         linestyle="--",
         label="Simulation Delta (same Z)",
         linewidth=2)
plt.plot(hs,
         delta_simulation_for_loop,
         color="blue",
         linestyle="-",
         label="Simulation Delta (Z in for loop)",
         linewidth=2)
plt.xlabel("h")
plt.ylabel("Delta")
plt.xscale("log")
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(hs,
         error,
         color="blue",
         linestyle="--",
         label="Error (same Z)",
         linewidth=2)
plt.plot(hs,
         error_for_loop,
         color="blue",
         linestyle="-",
         label="Error (Z in for loop)",
         linewidth=2)
plt.axhline(y=0,
            color="gray",
            linewidth=2)
plt.xlabel("h")
plt.ylabel("Absolute Relative Error")
plt.xscale("log")
plt.legend()

plt.tight_layout()
plt.show()


#%%
"""
結論：

本程式延續上課內容中子主題 B 的 Delta 分析架構，目的在於假設股價服從 Geometric Brownian Motion
(GBM) 時，使用蒙地卡羅模擬方法估計 European call option 的 Delta。Delta 衡量的是標的股價 S0
變動一小單位時，選擇權價格的變化程度，因此可以用來觀察買權價格對股價變動的敏感度。

本程式先利用 Black-Scholes 公式計算理論 Delta 作為比較基準，再使用蒙地卡羅方法模擬選擇權價格。
在模擬 Delta 時，採用 forward difference 的想法：分別計算 S0+h 與 S0 下的模擬買權價格，
再用兩者差異除以 h，得到模擬 Delta。本程式同時比較兩種亂數產生位置：第一種是先產生同一批
標準常態亂數 Z，讓所有 h 共用同一批 Z；第二種是把亂數產生放在 for 迴圈中，每一個 h 都重新
抽一批亂數。

圖中上半部比較不同 h 下的 Simulation Delta 與 True Delta。藍色虛線代表所有 h 共用同一批 Z 的
平滑寫法，藍色實線代表每一個 h 重新產生亂數的 for 迴圈寫法。若 h 選得適當，模擬 Delta 會接近
Black-Scholes 理論 Delta；若 h 太大，forward difference 近似會比較粗略；若 h 太小，數值計算
可能受到浮點誤差影響。因此 h 的選取會影響 Delta 估計的準確性。

圖中下半部顯示模擬 Delta 相對於理論 Delta 的絕對相對誤差。由誤差圖可以觀察到，Delta 估計值在
不同 h 下的誤差大小不同；而在 for 迴圈中每個 h 重新抽亂數時，曲線可能更容易出現抽樣波動。
綜合而言，蒙地卡羅方法可以用來估計 European call option 的 Delta，但估計結果會受到模擬亂數、
路徑數，以及差分間距 h 的影響。
"""
