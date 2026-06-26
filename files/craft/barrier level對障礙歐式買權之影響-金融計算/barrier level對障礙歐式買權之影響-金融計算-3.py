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


def GBM_simulation_paths(S0, r, T, sigma, Z, moment_matching=False):
    if moment_matching:
        Z = (Z-np.mean(Z, axis=0))/np.std(Z, axis=0)
        # 每個 column 計算平均數和標準差，做 moment matching。

    NumPaths, n = Z.shape
    dt = T/n
    mu = r-sigma**2/2
    R = mu*dt+sigma*np.sqrt(dt)*Z

    S = S0*np.ones((NumPaths, n+1))
    for j in range(n):
        S[:, j+1] = S[:, j]*np.exp(R[:, j])

    return S


def barrier_option_simulation(S0, K, B, r, T, sigma, Z,
                              moment_matching=False,
                              barrier_type="down-and-out"):
    S = GBM_simulation_paths(S0, r, T, sigma, Z,
                             moment_matching=moment_matching)
    ST = S[:, -1]
    min_S = np.min(S, axis=1)
    vanilla_payoff = np.maximum(ST-K, 0)

    if barrier_type == "down-and-out":
        payoff = vanilla_payoff*(min_S > B)
    if barrier_type == "down-and-in":
        payoff = vanilla_payoff*(min_S <= B)
    if barrier_type == "vanilla":
        payoff = vanilla_payoff

    option_price = np.exp(-r*T)*np.mean(payoff)

    return option_price


def make_standard_normal(m_paths, n, random_type="pseudo"):
    if random_type == "pseudo":
        u = np.random.rand(m_paths, n)
        Z = stats.norm.ppf(u)

    if random_type == "np.random.randn":
        Z = np.random.randn(m_paths, n)

    if random_type == "np.random.normal":
        Z = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, n))

    return Z


def barrier_delta_simulation(S0, K, B, r, T, sigma, Z, h,
                             moment_matching=False,
                             barrier_type="down-and-out"):
    option_price_up = barrier_option_simulation(S0+h, K, B, r, T, sigma, Z,
                                                moment_matching=moment_matching,
                                                barrier_type=barrier_type)
    option_price = barrier_option_simulation(S0, K, B, r, T, sigma, Z,
                                             moment_matching=moment_matching,
                                             barrier_type=barrier_type)

    Delta = (option_price_up-option_price)/h

    return Delta


def benchmark_barrier_delta(S0, K, B, r, T, sigma, h, n,
                            reference_paths, seed,
                            moment_matching=True,
                            barrier_type="down-and-out",
                            random_type="pseudo"):
    np.random.seed(seed)
    Z_reference = make_standard_normal(reference_paths, n, random_type)
    Delta = barrier_delta_simulation(S0, K, B, r, T, sigma, Z_reference, h,
                                     moment_matching=moment_matching,
                                     barrier_type=barrier_type)

    return Delta


#%%
# 參數設定
S0 = 100.0
K = 100.0
B = 90.0
r = 0.02
T = 0.5
sigma = 0.2
option_type = "call"
barrier_type = "down-and-out"
time_intervals_year = 252
dt = 1/time_intervals_year
n = int(T/dt)
m_paths = 1000
seed = 42
random_type = "pseudo"
reference_paths = 20000
h_reference = 1e-2

vanilla_call_BS = Black_Scholes(S0, K, r, T, sigma,
                                option_type=option_type)
vanilla_delta_BS = Black_Scholes_Delta(S0, K, r, T, sigma,
                                       option_type=option_type)
delta_benchmark = benchmark_barrier_delta(S0, K, B, r, T, sigma,
                                          h_reference, n,
                                          reference_paths, seed+100,
                                          moment_matching=True,
                                          barrier_type=barrier_type,
                                          random_type=random_type)

print("Vanilla European call option price (Black-Scholes) =",
      f"{vanilla_call_BS:.6f}")
print("Vanilla European call Delta (Black-Scholes) =",
      f"{vanilla_delta_BS:.6f}")
print("Benchmark Barrier Delta =", f"{delta_benchmark:.6f}")


#%%
# h 由很小到較大，觀察 forward difference 模擬 Barrier Delta 的變化。
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
# 固定亂數種子，並在 for 迴圈中每一個 h 重新產生亂數。
np.random.seed(seed)

for i in range(len(hs)):
    h = hs[i]
    Z_fixed = make_standard_normal(m_paths, n, random_type)

    delta_fixed_seed_MM[i] = barrier_delta_simulation(S0, K, B, r, T, sigma,
                                                      Z_fixed, h,
                                                      moment_matching=True,
                                                      barrier_type=barrier_type)
    delta_fixed_seed_no_MM[i] = barrier_delta_simulation(S0, K, B, r, T, sigma,
                                                         Z_fixed, h,
                                                         moment_matching=False,
                                                         barrier_type=barrier_type)

    error_fixed_seed_MM[i] = np.abs((delta_fixed_seed_MM[i]-delta_benchmark)
                                    /delta_benchmark)
    error_fixed_seed_no_MM[i] = np.abs((delta_fixed_seed_no_MM[i]-delta_benchmark)
                                       /delta_benchmark)


#%%
# 不固定亂數種子，並在 for 迴圈中每一個 h 重新產生亂數。
np.random.seed(None)

for i in range(len(hs)):
    h = hs[i]
    Z_unfixed = make_standard_normal(m_paths, n, random_type)

    delta_unfixed_seed_MM[i] = barrier_delta_simulation(S0, K, B, r, T, sigma,
                                                        Z_unfixed, h,
                                                        moment_matching=True,
                                                        barrier_type=barrier_type)
    delta_unfixed_seed_no_MM[i] = barrier_delta_simulation(S0, K, B, r, T, sigma,
                                                           Z_unfixed, h,
                                                           moment_matching=False,
                                                           barrier_type=barrier_type)

    error_unfixed_seed_MM[i] = np.abs((delta_unfixed_seed_MM[i]-delta_benchmark)
                                      /delta_benchmark)
    error_unfixed_seed_no_MM[i] = np.abs((delta_unfixed_seed_no_MM[i]
                                          -delta_benchmark)/delta_benchmark)


#%%
# 圖：比較使用與不使用 moment matching 下的模擬 Barrier Delta 與誤差。
plt.figure(figsize=(8, 6))

plt.subplot(2, 1, 1)
plt.axhline(y=delta_benchmark,
            color="gray",
            label="Benchmark Barrier Delta",
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
# 輸出代表性數值，方便報告引用。
print("\n子主題 C-(b)")
print("S0, K, B, r, T, sigma, m_paths, n")
print(S0, K, B, r, T, sigma, m_paths, n)
print("barrier_type =", barrier_type)
print("\nh, fixed MM, unfixed MM, fixed no MM, unfixed no MM")

h_examples = [1e-14, 1e-10, 1e-6, 1e-2, 1]
for h in h_examples:
    index = np.argmin(np.abs(hs-h))
    print(f"{hs[index]:.6e}, "
          f"{delta_fixed_seed_MM[index]:.6f}, "
          f"{delta_unfixed_seed_MM[index]:.6f}, "
          f"{delta_fixed_seed_no_MM[index]:.6f}, "
          f"{delta_unfixed_seed_no_MM[index]:.6f}")


#%%
"""
結論：

本程式依照子主題 B-(b) 的架構，將比較對象改為 Barrier European call
option 的 Delta。分析重點是在固定與不固定亂數種子的情況下，比較使用 moment
matching 與不使用 moment matching 對 down-and-out barrier call Delta 估計的影響。

本題固定 S0 = 100、K = 100、B = 90、r = 0.02、T = 0.5、sigma = 0.2，
並用每日離散監測模擬 barrier option 的完整路徑。由於 barrier option 是否生效
取決於整條股價路徑是否碰到 barrier，因此相較於一般 European call option，
它的 Delta 更容易受到亂數抽樣影響。

圖中四條線分別代表固定亂數種子且使用 moment matching、不固定亂數種子且使用
moment matching、固定亂數種子且不使用 moment matching，以及不固定亂數種子且
不使用 moment matching。透過這樣的安排，可以同時觀察亂數種子設定與 moment
matching 對 Delta 估計穩定性的影響。

Moment matching 會將每個時間點的標準常態亂數重新調整為平均數接近 0、標準差
接近 1，使模擬路徑的亂數樣本更接近理論標準常態分配。因此，使用 moment
matching 時，Delta 與誤差曲線通常會比較穩定；不使用 moment matching 時，
抽樣誤差較容易反映在圖表上。

綜合而言，Barrier Delta 的估計同時受到 h、亂數種子設定與 moment matching 影響。
適中的 h 能降低有限差分誤差，固定 seed 可以提高可重現性，而 moment matching 則有助於
降低抽樣誤差，使蒙地卡羅模擬的 Delta 結果更穩定。
"""
