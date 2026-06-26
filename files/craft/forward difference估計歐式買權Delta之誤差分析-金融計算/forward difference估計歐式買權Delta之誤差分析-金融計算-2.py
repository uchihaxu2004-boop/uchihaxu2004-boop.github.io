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
random_type = "pseudo"


#%%
# Analytical Delta
delta_true = Black_Scholes_Delta(S0, K, r, T, sigma, option_type=option_type)

# h 由很小到較大，觀察 forward difference 模擬 Delta 的變化
hs = np.logspace(-16, 1, 100)

delta_fixed_seed = np.zeros(len(hs))
delta_unfixed_seed = np.zeros(len(hs))
error_fixed_seed = np.zeros(len(hs))
error_unfixed_seed = np.zeros(len(hs))


#%%
# 固定亂數種子，並在 for 迴圈中每一個 h 重新產生亂數
np.random.seed(seed)

for i in range(len(hs)):
    h = hs[i]

    if random_type == "pseudo":
        u_fixed = np.random.rand(m_paths, N)
        Z_fixed = stats.norm.ppf(u_fixed)

    if random_type == "np.random.randn":
        Z_fixed = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_fixed = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_price_up_fixed = European_option_simulation(S0+h, K, r, T, sigma, Z_fixed,
                                                       moment_matching=moment_matching,
                                                       option_type=option_type)

    option_price_fixed = European_option_simulation(S0, K, r, T, sigma, Z_fixed,
                                                    moment_matching=moment_matching,
                                                    option_type=option_type)

    delta_fixed_seed[i] = np.mean((option_price_up_fixed-option_price_fixed)/h)
    error_fixed_seed[i] = np.abs((delta_fixed_seed[i]-delta_true)/delta_true)


#%%
# 不固定亂數種子，並在 for 迴圈中每一個 h 重新產生亂數
np.random.seed(None)

for i in range(len(hs)):
    h = hs[i]

    if random_type == "pseudo":
        u_unfixed = np.random.rand(m_paths, N)
        Z_unfixed = stats.norm.ppf(u_unfixed)

    if random_type == "np.random.randn":
        Z_unfixed = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_unfixed = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_price_up_unfixed = European_option_simulation(S0+h, K, r, T, sigma, Z_unfixed,
                                                         moment_matching=moment_matching,
                                                         option_type=option_type)

    option_price_unfixed = European_option_simulation(S0, K, r, T, sigma, Z_unfixed,
                                                      moment_matching=moment_matching,
                                                      option_type=option_type)

    delta_unfixed_seed[i] = np.mean((option_price_up_unfixed-option_price_unfixed)/h)
    error_unfixed_seed[i] = np.abs((delta_unfixed_seed[i]-delta_true)/delta_true)


#%%
# 圖：固定與不固定亂數種子下的模擬 Delta 與誤差
plt.figure(figsize=(8, 6))

plt.subplot(2, 1, 1)
plt.axhline(y=delta_true,
            color="gray",
            label="True Delta",
            linewidth=2)
plt.plot(hs,
         delta_fixed_seed,
         color="blue",
         linestyle="-",
         label="fixed seed",
         linewidth=2)
plt.plot(hs,
         delta_unfixed_seed,
         color="red",
         linestyle="-",
         label="unfixed seed",
         linewidth=2)
plt.xlabel("h")
plt.ylabel("Delta")
plt.xscale("log")
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(hs,
         error_fixed_seed,
         color="blue",
         linestyle="-",
         label="Error (fixed seed)",
         linewidth=2)
plt.plot(hs,
         error_unfixed_seed,
         color="red",
         linestyle="-",
         label="Error (unfixed seed)",
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

本程式延續子主題 B 的 Delta 模擬設定，目的在於比較模擬 Delta 過程中，固定亂數種子與不固定
亂數種子對估計結果的影響。其他參數皆維持不變，包括 S0 = 100、K = 100、r = 0.02、T = 0.5、
sigma = 0.2、m_paths = 1000、N = 1，以及 moment_matching = True。

本題只保留抖動寫法，也就是在每一個 h 下都重新產生一批亂數。固定亂數種子時，整條亂數序列的起點
固定，因此每次重新執行程式都可以得到相同結果；不固定亂數種子時，每次執行程式可能會產生不同
亂數樣本，因此 Delta 與誤差曲線可能會有些微差異。

圖中上半部比較固定亂數種子與不固定亂數種子下的 Simulation Delta，灰色水平線為 Black-Scholes
理論 Delta。圖中下半部則比較兩者相對於理論 Delta 的絕對相對誤差。由圖表可以觀察到，不論亂數
種子是否固定，Delta 估計都會受到差分間距 h 與亂數抽樣誤差影響。

綜合而言，固定亂數種子主要提供可重現性，方便檢查程式與撰寫報告；不固定亂數種子則能呈現蒙地卡羅
模擬在不同亂數樣本下的自然變動。本題結果也說明，在使用蒙地卡羅方法估計 Delta 時，亂數設定與 h
的選取都會影響估計結果的穩定性。
"""
