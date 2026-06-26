# ============================================================
#  NBA 總冠軍賽勝場數之多元迴歸分析
#  江慶栩 12155209
#  東吳大學財務工程與精算數學系
# ============================================================


# ------------------------------------------------------------
#  1. 載入套件
# ------------------------------------------------------------
library(readxl)    # 讀取 Excel 檔案
library(car)       # VIF 計算
library(lmtest)    # Durbin-Watson、Breusch-Pagan 檢定
library(leaps)     # 全子集迴歸


# ------------------------------------------------------------
#  2. 設定工作目錄並讀取資料
# ------------------------------------------------------------
setwd("/Users/uchihamac/Desktop/迴歸分析")
nba <- read_excel("chatgptnba.xlsx", sheet = "NBA_Data")

# 篩選訓練樣本（排除 2025-26 賽季作為預測對象）
train <- nba[!is.na(nba$FinalsWins), ]
test  <- nba[is.na(nba$FinalsWins), ]
nn <- nrow(train)
cat("訓練樣本數：", nn, "\n")
cat("預測樣本數：", nrow(test), "\n")


# ============================================================
#  肆、資料分析
# ============================================================

vars <- c("FinalsWins",
          "PreFinals_WinPct", "PreFinals_NetRtg",
          "PreFinals_TS", "PreFinals_3P",
          "PreFinals_TOV", "PreFinals_BenchPts",
          "AwardDiff", "H2H_WinDiff",
          "log_Payroll", "log_CityGDP")

# ----- 敘述統計 -----
desc <- data.frame(
  變數   = vars,
  平均數 = sapply(train[vars], mean),
  中位數 = sapply(train[vars], median),
  標準差 = sapply(train[vars], sd),
  最小值 = sapply(train[vars], min),
  最大值 = sapply(train[vars], max),
  個數   = sapply(train[vars], length)
)
cat("\n========== 敘述統計 ==========\n")
print(round(desc[, -1], 3))

# ----- 相關係數矩陣 -----
cor_matrix <- round(cor(train[vars]), 3)
cat("\n========== 相關係數矩陣 ==========\n")
print(cor_matrix)

# ----- Y 與各 X 的相關係數 -----
cat("\n========== Y 與各 X 相關係數 ==========\n")
print(round(cor_matrix["FinalsWins", ], 3))


# ============================================================
#  伍、初始多元迴歸模型
# ============================================================

model_initial <- lm(FinalsWins ~ PreFinals_WinPct + PreFinals_NetRtg +
                                  PreFinals_TS + PreFinals_3P +
                                  PreFinals_TOV + PreFinals_BenchPts +
                                  AwardDiff + H2H_WinDiff +
                                  log_Payroll + log_CityGDP,
                    data = train)

cat("\n========== 初始模型摘要 ==========\n")
print(summary(model_initial))

cat("\n========== 初始模型 VIF ==========\n")
print(round(vif(model_initial), 3))


# ============================================================
#  陸、模型重建與模型選擇
# ============================================================

null_model <- lm(FinalsWins ~ 1, data = train)
full_model <- model_initial


# ----- 二、向前取法 -----

# AIC 向前取法
cat("\n========== 向前取法（AIC） ==========\n")
forward_AIC <- step(null_model,
                    scope = list(lower = null_model, upper = full_model),
                    direction = "forward")
cat("\n--- 向前(AIC)最終模型 ---\n")
print(summary(forward_AIC))

# BIC 向前取法
cat("\n========== 向前取法（BIC） ==========\n")
forward_BIC <- step(null_model,
                    scope = list(lower = null_model, upper = full_model),
                    direction = "forward", k = log(nn))
cat("\n--- 向前(BIC)最終模型 ---\n")
print(summary(forward_BIC))


# ----- 三、向後取法 -----

# AIC 向後取法
cat("\n========== 向後取法（AIC） ==========\n")
backward_AIC <- step(model_initial, direction = "backward")
cat("\n--- 向後(AIC)最終模型 ---\n")
print(summary(backward_AIC))

# BIC 向後取法
cat("\n========== 向後取法（BIC） ==========\n")
backward_BIC <- step(model_initial, direction = "backward", k = log(nn))
cat("\n--- 向後(BIC)最終模型 ---\n")
print(summary(backward_BIC))


# ----- 四、逐步取法 -----

# AIC 逐步取法
cat("\n========== 逐步取法（AIC） ==========\n")
stepwise_AIC <- step(model_initial, direction = "both")
cat("\n--- 逐步(AIC)最終模型 ---\n")
print(summary(stepwise_AIC))

# BIC 逐步取法
cat("\n========== 逐步取法（BIC） ==========\n")
stepwise_BIC <- step(model_initial, direction = "both", k = log(nn))
cat("\n--- 逐步(BIC)最終模型 ---\n")
print(summary(stepwise_BIC))


# ----- 五、全子集取法 -----

cat("\n========== 全子集取法 ==========\n")
best_subsets <- regsubsets(FinalsWins ~ PreFinals_WinPct + PreFinals_NetRtg +
                                         PreFinals_TS + PreFinals_3P +
                                         PreFinals_TOV + PreFinals_BenchPts +
                                         AwardDiff + H2H_WinDiff +
                                         log_Payroll + log_CityGDP,
                           data = train, nvmax = 10, nbest = 1)
bs_summary <- summary(best_subsets)

# 計算每個變數數量下的 AIC 與 BIC
n_subsets <- length(bs_summary$rss)
bs_AIC <- numeric(n_subsets)
bs_BIC <- numeric(n_subsets)
for (i in 1:n_subsets) {
  rss <- bs_summary$rss[i]; k <- i
  ll <- -nn/2 * (log(2*pi) + log(rss/nn) + 1)
  bs_AIC[i] <- -2*ll + 2*(k+2)
  bs_BIC[i] <- -2*ll + log(nn)*(k+2)
}

bs_table <- data.frame(
  變數數 = 1:n_subsets,
  R2     = round(bs_summary$rsq, 4),
  Adj_R2 = round(bs_summary$adjr2, 4),
  Cp     = round(bs_summary$cp, 4),
  AIC    = round(bs_AIC, 2),
  BIC    = round(bs_BIC, 2)
)
print(bs_table)

best_n_AIC <- which.min(bs_AIC)
best_n_BIC <- which.min(bs_BIC)
cat("\n→ 全子集（AIC）最佳變數數 =", best_n_AIC, "\n")
cat("→ 全子集（BIC）最佳變數數 =", best_n_BIC, "\n")

all_vars_names <- c("PreFinals_WinPct", "PreFinals_NetRtg",
                    "PreFinals_TS", "PreFinals_3P",
                    "PreFinals_TOV", "PreFinals_BenchPts",
                    "AwardDiff", "H2H_WinDiff",
                    "log_Payroll", "log_CityGDP")

# 全子集(AIC)最終模型
selected_AIC <- all_vars_names[bs_summary$which[best_n_AIC, -1]]
bestsubsets_AIC <- lm(as.formula(paste("FinalsWins ~", paste(selected_AIC, collapse = " + "))),
                      data = train)
cat("\n--- 全子集(AIC)最終模型 ---\n")
print(summary(bestsubsets_AIC))

# 全子集(BIC)最終模型
selected_BIC <- all_vars_names[bs_summary$which[best_n_BIC, -1]]
bestsubsets_BIC <- lm(as.formula(paste("FinalsWins ~", paste(selected_BIC, collapse = " + "))),
                      data = train)
cat("\n--- 全子集(BIC)最終模型 ---\n")
print(summary(bestsubsets_BIC))


# ----- 六、九模型對照表 -----

get_stats <- function(m, name) {
  s <- summary(m)
  if (length(coef(m)) <= 1 || is.null(s$fstatistic)) {
    F_val <- NA; F_p <- NA
  } else {
    F_val <- round(s$fstatistic[1], 4)
    F_p   <- round(pf(s$fstatistic[1], s$fstatistic[2], s$fstatistic[3],
                      lower.tail = FALSE), 4)
  }
  max_vif <- if (length(coef(m)) > 2) round(max(vif(m)), 4) else NA
  data.frame(
    模型       = name,
    變數數     = length(coef(m)) - 1,
    R2         = round(s$r.squared, 4),
    Adj_R2     = round(s$adj.r.squared, 4),
    殘差SE     = round(s$sigma, 4),
    F          = F_val,
    F_p        = F_p,
    AIC        = round(AIC(m), 2),
    BIC        = round(BIC(m), 2),
    最大VIF    = max_vif
  )
}

compare_all <- rbind(
  get_stats(model_initial,   "初始模型"),
  get_stats(forward_AIC,     "向前(AIC)"),
  get_stats(forward_BIC,     "向前(BIC)"),
  get_stats(backward_AIC,    "向後(AIC)"),
  get_stats(backward_BIC,    "向後(BIC)"),
  get_stats(stepwise_AIC,    "逐步(AIC)"),
  get_stats(stepwise_BIC,    "逐步(BIC)"),
  get_stats(bestsubsets_AIC, "全子集(AIC)"),
  get_stats(bestsubsets_BIC, "全子集(BIC)")
)

cat("\n========== 九模型對照表 ==========\n")
print(compare_all)


# ============================================================
#  柒、最終模型診斷
# ============================================================

# 確認最終模型為 backward_AIC（與向後 BIC、逐步 AIC、逐步 BIC、全子集 AIC 一致）
final_model <- backward_AIC

cat("\n========== 最終模型摘要 ==========\n")
print(summary(final_model))

# ----- 一、共線性檢查（VIF） -----
cat("\n========== 最終模型 VIF ==========\n")
print(round(vif(final_model), 3))

# ----- 二、自我相關檢定（Durbin-Watson） -----
cat("\n========== Durbin-Watson 自我相關檢定 ==========\n")
print(dwtest(final_model))

# ----- 三、異質變異檢定（Breusch-Pagan） -----
cat("\n========== Breusch-Pagan 異質變異檢定 ==========\n")
print(bptest(final_model))

# Scale-Location 圖（同質變異視覺輔助）
plot(final_model, which = 3)

# ----- 四、常態性檢定（Shapiro-Wilk） -----
cat("\n========== Shapiro-Wilk 常態性檢定 ==========\n")
print(shapiro.test(residuals(final_model)))

# Q-Q Residuals 圖（常態性視覺輔助）
plot(final_model, which = 2)

# ----- 五、影響點分析（Cook's Distance & Leverage） -----
cat("\n========== Cook's Distance ==========\n")
cook_d <- cooks.distance(final_model)
cat("最大 Cook's Distance =", round(max(cook_d), 4), "\n")
cat("警戒線（4/n）=", round(4/nn, 4), "\n")

# Cook's Distance 圖
plot(final_model, which = 4)

# Residuals vs Leverage 圖
plot(final_model, which = 5)


# ============================================================
#  捌、2025-26 賽季預測
# ============================================================

cat("\n========== 2025-26 預測結果 ==========\n")
pred <- predict(final_model, newdata = test)
pred_table <- data.frame(
  球隊     = test$Team,
  對手     = test$Opponent,
  預測分數 = round(pred, 4)
)
print(pred_table)

cat("\n→ 預測冠軍：", pred_table$球隊[which.max(pred_table$預測分數)],
    "（預測分數", round(max(pred_table$預測分數), 2),
    "，領先", round(diff(range(pred_table$預測分數)), 2), "分）\n")


# ============================================================
#  END OF SCRIPT
# ============================================================
