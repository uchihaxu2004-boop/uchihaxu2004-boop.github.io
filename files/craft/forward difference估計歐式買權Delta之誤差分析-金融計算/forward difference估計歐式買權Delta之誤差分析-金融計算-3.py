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

m_paths = 1000
N = 1

seed = 42
random_type = "pseudo"


#%%
# Analytical Delta
delta_true = Black_Scholes_Delta(S0, K, r, T, sigma, option_type=option_type)

# h 由很小到較大，觀察 forward difference 模擬 Delta 的變化
hs = np.logspace(-16, 1, 100)

delta_fixed_seed_MM = np.zeros(len(hs))
delta_unfixed_seed_MM = np.zeros(len(hs))
delta_fixed_seed_no_MM = np.zeros(len(hs))
delta_unfixed_seed_no_MM = np.zeros(len(hs))

error_fixed_seed_MM = np.zeros(len(hs))
error_unfixed_seed_MM = np.zeros(len(hs))
error_fixed_seed_no_MM = np.zeros(len(hs))
error_unfixed_seed_no_MM = np.zeros(len(hs))


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

    option_price_up_fixed_MM = European_option_simulation(S0+h, K, r, T, sigma, Z_fixed,
                                                          moment_matching=True,
                                                          option_type=option_type)
    option_price_fixed_MM = European_option_simulation(S0, K, r, T, sigma, Z_fixed,
                                                       moment_matching=True,
                                                       option_type=option_type)

    option_price_up_fixed_no_MM = European_option_simulation(S0+h, K, r, T, sigma, Z_fixed,
                                                             moment_matching=False,
                                                             option_type=option_type)
    option_price_fixed_no_MM = European_option_simulation(S0, K, r, T, sigma, Z_fixed,
                                                          moment_matching=False,
                                                          option_type=option_type)

    delta_fixed_seed_MM[i] = np.mean((option_price_up_fixed_MM-option_price_fixed_MM)/h)
    delta_fixed_seed_no_MM[i] = np.mean((option_price_up_fixed_no_MM-option_price_fixed_no_MM)/h)

    error_fixed_seed_MM[i] = np.abs((delta_fixed_seed_MM[i]-delta_true)/delta_true)
    error_fixed_seed_no_MM[i] = np.abs((delta_fixed_seed_no_MM[i]-delta_true)/delta_true)


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

    option_price_up_unfixed_MM = European_option_simulation(S0+h, K, r, T, sigma, Z_unfixed,
                                                            moment_matching=True,
                                                            option_type=option_type)
    option_price_unfixed_MM = European_option_simulation(S0, K, r, T, sigma, Z_unfixed,
                                                         moment_matching=True,
                                                         option_type=option_type)

    option_price_up_unfixed_no_MM = European_option_simulation(S0+h, K, r, T, sigma, Z_unfixed,
                                                               moment_matching=False,
                                                               option_type=option_type)
    option_price_unfixed_no_MM = European_option_simulation(S0, K, r, T, sigma, Z_unfixed,
                                                            moment_matching=False,
                                                            option_type=option_type)

    delta_unfixed_seed_MM[i] = np.mean((option_price_up_unfixed_MM-option_price_unfixed_MM)/h)
    delta_unfixed_seed_no_MM[i] = np.mean((option_price_up_unfixed_no_MM-option_price_unfixed_no_MM)/h)

    error_unfixed_seed_MM[i] = np.abs((delta_unfixed_seed_MM[i]-delta_true)/delta_true)
    error_unfixed_seed_no_MM[i] = np.abs((delta_unfixed_seed_no_MM[i]-delta_true)/delta_true)


#%%
# 圖：比較使用與不使用 moment matching 下的模擬 Delta 與誤差
plt.figure(figsize=(8, 6))

plt.subplot(2, 1, 1)
plt.axhline(y=delta_true,
            color="gray",
            label="True Delta",
            linewidth=2)
plt.plot(hs,
         delta_fixed_seed_MM,
         color="blue",
         linestyle="-",
         label="fixed seed, MM",
         linewidth=2)
plt.plot(hs,
         delta_unfixed_seed_MM,
         color="red",
         linestyle="-",
         label="unfixed seed, MM",
         linewidth=2)
plt.plot(hs,
         delta_fixed_seed_no_MM,
         color="green",
         linestyle="-",
         label="fixed seed, no MM",
         linewidth=2)
plt.plot(hs,
         delta_unfixed_seed_no_MM,
         color="gold",
         linestyle="-",
         label="unfixed seed, no MM",
         linewidth=2)
plt.xlabel("h")
plt.ylabel("Delta")
plt.xscale("log")
plt.legend(loc="upper right",
           bbox_to_anchor=(0.98, 0.98),
           fontsize=6,
           framealpha=0.55,
           borderpad=0.25,
           labelspacing=0.25,
           handlelength=1.4)

plt.subplot(2, 1, 2)
plt.plot(hs,
         error_fixed_seed_MM,
         color="blue",
         linestyle="-",
         label="Error (fixed seed, MM)",
         linewidth=2)
plt.plot(hs,
         error_unfixed_seed_MM,
         color="red",
         linestyle="-",
         label="Error (unfixed seed, MM)",
         linewidth=2)
plt.plot(hs,
         error_fixed_seed_no_MM,
         color="green",
         linestyle="-",
         label="Error (fixed seed, no MM)",
         linewidth=2)
plt.plot(hs,
         error_unfixed_seed_no_MM,
         color="gold",
         linestyle="-",
         label="Error (unfixed seed, no MM)",
         linewidth=2)
plt.axhline(y=0,
            color="gray",
            linewidth=2)
plt.xlabel("h")
plt.ylabel("Absolute Relative Error")
plt.xscale("log")
plt.legend(loc="upper right",
           bbox_to_anchor=(0.98, 0.98),
           fontsize=6,
           framealpha=0.55,
           borderpad=0.25,
           labelspacing=0.25,
           handlelength=1.4)

plt.tight_layout()
plt.show()


#%%
"""
結論：

本程式延續子主題 B-(a) 的 Delta 模擬設定，目的在於比較模擬 Delta 過程中，使用 moment matching
與不使用 moment matching 的結果差異。其他參數皆維持不變，包括 S0 = 100、K = 100、r = 0.02、
T = 0.5、sigma = 0.2、m_paths = 1000、N = 1。

本題只保留抖動寫法，也就是在每一個 h 下都重新產生一批亂數。圖中共有四條線，分別代表固定亂數
種子且使用 moment matching、不固定亂數種子且使用 moment matching、固定亂數種子但不使用
moment matching，以及不固定亂數種子但不使用 moment matching。

Moment matching 的目的，是將模擬用的標準常態亂數校正為平均數接近 0、標準差接近 1，使亂數樣本
更接近理論標準常態分配。使用 moment matching 時，模擬 Delta 與誤差曲線通常會比較穩定；
不使用 moment matching 時，亂數樣本本身的抽樣誤差會保留下來，因此估計結果可能會有較明顯波動。

圖中上半部比較四種情況下的 Simulation Delta，灰色水平線為 Black-Scholes 理論 Delta。
圖中下半部則比較四種情況下的絕對相對誤差。由圖表可以觀察到，Delta 估計不只受到 h 的大小影響，
也會受到亂數種子設定與是否使用 moment matching 的影響。

綜合而言，moment matching 有助於降低部分亂數抽樣誤差，使蒙地卡羅模擬估計更穩定；固定亂數種子
則能使結果具有可重現性。不過在使用差分法估計 Delta 時，仍需要注意 h 的選取，因為 h 太大或太小
都可能造成估計誤差。
"""
