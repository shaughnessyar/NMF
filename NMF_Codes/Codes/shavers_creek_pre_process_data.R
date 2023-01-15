#load package
library(tidyverse)

#import raw data
raw <- read_csv("shavers_creek_raw.csv")

#set seed for reproducability
set.seed(421)
data <- raw %>%
  #remvove date 
  select(-date) %>%
  #normalize everything by sulfate
  mutate(across(everything(),list(SO4 = ~./SO4))) %>%
  #select normalized variables
  select(contains("_SO4"), -SO4_SO4)

norm_dat <- data %>%
  #normalize all variables by their max
  mutate(across(everything(), ~./max(., na.rm = T)))

#calculate the log-mean for every variable
means <- data %>%
  mutate(across(everything(),log10)) %>%
  summarise_all(mean) %>%
  unlist()

#calculate the covariance for all log-transformed variables
covs <- data %>%
  mutate(across(everything(),log10)) %>%
  cov(.)

#boostrap a synthetic dataset to train the model basen on multivariate norm.
syn_norm <- MASS::mvrnorm(n = 6000, Sigma = covs, mu = means) %>%
  as_tibble() %>%
  mutate(across(everything(), ~10^.)) %>%
  mutate(Cl_SO4 = Cl_SO4/max(data$Cl_SO4),
         Ca_SO4 = Ca_SO4/max(data$Ca_SO4),
         K_SO4 = K_SO4/max(data$K_SO4),
         Mg_SO4 = Mg_SO4/max(data$Mg_SO4),
         Na_SO4 = Na_SO4/max(data$Na_SO4),
         NO3_SO4 = NO3_SO4/max(data$NO3_SO4)) %>%
  filter(across(everything(), ~.<=1))

#these files will be used in the model
write_csv(norm_dat, "shavers_creek_norm_data.csv")
write_csv(syn_norm, "shavers_creek_boot_norm_data.csv")
