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

m_paths = 1000
N = 1

random_type = "pseudo"


#%%
# 探討不同波動率 sigma 對 European call option 模擬價格的影響
sigmas = np.linspace(0.1, 0.6, 26)

option_prices_seed_MM_mean = np.zeros(len(sigmas))
option_prices_no_seed_MM_mean = np.zeros(len(sigmas))
option_prices_seed_no_MM_mean = np.zeros(len(sigmas))
option_prices_no_seed_no_MM_mean = np.zeros(len(sigmas))


#%%
# 固定亂數種子，並在 for 迴圈中每一個 sigma 重新產生亂數
seed = 42
np.random.seed(seed)

for i in range(len(sigmas)):
    sigma = sigmas[i]

    if random_type == "pseudo":
        u_seed_for_loop = np.random.rand(m_paths, N)
        Z_seed_for_loop = stats.norm.ppf(u_seed_for_loop)

    if random_type == "np.random.randn":
        Z_seed_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_seed_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_prices_seed_MM = European_option_simulation(S0, K, r, T, sigma, Z_seed_for_loop,
                                                       moment_matching=True,
                                                       option_type=option_type)

    option_prices_seed_no_MM = European_option_simulation(S0, K, r, T, sigma, Z_seed_for_loop,
                                                          moment_matching=False,
                                                          option_type=option_type)

    option_prices_seed_MM_mean[i] = np.mean(option_prices_seed_MM)
    option_prices_seed_no_MM_mean[i] = np.mean(option_prices_seed_no_MM)


#%%
# 不固定亂數種子，並在 for 迴圈中每一個 sigma 重新產生亂數
np.random.seed(None)

for i in range(len(sigmas)):
    sigma = sigmas[i]

    if random_type == "pseudo":
        u_no_seed_for_loop = np.random.rand(m_paths, N)
        Z_no_seed_for_loop = stats.norm.ppf(u_no_seed_for_loop)

    if random_type == "np.random.randn":
        Z_no_seed_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_no_seed_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_prices_no_seed_MM = European_option_simulation(S0, K, r, T, sigma, Z_no_seed_for_loop,
                                                          moment_matching=True,
                                                          option_type=option_type)

    option_prices_no_seed_no_MM = European_option_simulation(S0, K, r, T, sigma, Z_no_seed_for_loop,
                                                             moment_matching=False,
                                                             option_type=option_type)

    option_prices_no_seed_MM_mean[i] = np.mean(option_prices_no_seed_MM)
    option_prices_no_seed_no_MM_mean[i] = np.mean(option_prices_no_seed_no_MM)


#%%
# 圖：比較固定與不固定亂數種子下，有無使用 moment matching 之模擬結果
plt.figure(figsize=(10, 6))

plt.plot(sigmas,
         option_prices_seed_MM_mean,
         color="blue",
         linewidth=2,
         label="fixed seed, MM")

plt.plot(sigmas,
         option_prices_no_seed_MM_mean,
         color="red",
         linewidth=2,
         label="unfixed seed, MM")

plt.plot(sigmas,
         option_prices_seed_no_MM_mean,
         color="green",
         linewidth=2,
         label="fixed seed, no MM")

plt.plot(sigmas,
         option_prices_no_seed_no_MM_mean,
         color="gold",
         linewidth=2,
         label="unfixed seed, no MM")

plt.xlabel(r"$\sigma$")
plt.ylabel("European call option price")
plt.title("European call option simulation price: moment matching comparison")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


#%%
"""
結論：

本程式延續前一題固定亂數種子與不固定亂數種子的比較，進一步加入是否使用 moment matching 的差異。
因此圖中共有四條線，分別代表固定亂數種子且使用 moment matching、不固定亂數種子且使用 moment matching、
固定亂數種子但不使用 moment matching，以及不固定亂數種子但不使用 moment matching。四條線皆使用
在 for 迴圈中每一個 sigma 重新產生亂數的寫法，因此可以較明顯呈現抽樣波動。
其他參數皆維持不變，包括 S0 = 100、K = 100、r = 0.02、T = 0.5、m_paths = 1000、N = 1，
以及 sigma 從 0.1 到 0.6 共 26 個等距點。

Moment matching 的目的，是將模擬使用的標準常態亂數重新標準化，使樣本平均數接近 0、標準差接近 1。
這樣可以降低因亂數抽樣造成的誤差，使模擬結果較穩定。相對地，不使用 moment matching 時，
亂數樣本的平均數與標準差可能會和理論標準常態分配有些微差異，因此模擬價格可能會產生較明顯的抽樣誤差。

由圖表可以觀察到，四條線的整體趨勢皆隨著 sigma 增加而上升，表示不論亂數種子是否固定、
也不論是否使用 moment matching，European call option 的模擬價格都會隨波動率上升而增加。
這說明波動率與買權價格之間的正向關係，是由買權本身的性質與 GBM 模型決定，而不是單純由某一種
亂數設定造成。

若四條線之間出現些微差距，主要原因來自兩個部分：第一是固定亂數種子與不固定亂數種子產生的亂數樣本不同；
第二是使用 moment matching 會校正亂數樣本，而不使用 moment matching 則保留原本的抽樣誤差。
本題在每一個 sigma 都重新抽一批亂數；在 m_paths = 1000、N = 1 的設定下，模擬樣本數有限，
因此這些差異可能反映在曲線上。

綜合而言，moment matching 可以讓蒙地卡羅模擬結果更穩定，也能降低部分亂數抽樣造成的誤差；
固定亂數種子則可以讓結果具有可重現性。不過不論採用哪一種設定，本次模擬共同支持同一個結論：
在其他條件固定下，European call option 的價格會隨著波動率 sigma 增加而上升。
"""
