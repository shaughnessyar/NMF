#load package
library(tidyverse)

#import data
nmf_output <- read_csv("shale_hills_NMF_output.csv")
norm_dat <- read_csv("shale_hills_norm_data.csv")
model_inputs <- read_csv("shale_hills_raw.csv")

#calculate errors for all valid models as SSE
total_nmf_mods <- list(
  norm_dat %>%
    mutate(sample = row_number()),
  nmf_output %>%
    arrange(sample)
) %>%
  reduce(full_join, by = "sample") %>%
  mutate(error = ((Ca_SO4-Ca_mod)^2) + ((Na_SO4-Na_mod)^2) + ((Mg_SO4-Mg_mod)^2) + ((K_SO4-K_mod)^2) + ((Cl_SO4-Cl_mod)^2)) %>%
  nest(data = -sample)

#pull out 5th percentile best model and unnormalize endmember composition
sh_nmf_clean <- list(
  model_inputs %>%
    mutate(sample = row_number()),

  total_nmf_mods %>%
    mutate(n = map_dbl(data, ~nrow(.)),
           ref = map_dbl(data, ~quantile(.x$error, 0.05, na.rm = T)),
           filtered = map2(data, ref, ~filter(.x, error < .y)),
           new_n = map_dbl(filtered, ~nrow(.x)),
           rock_s = map_dbl(filtered, ~mean(.x$rock)),
           rain_s = map_dbl(filtered, ~mean(.x$rain)),
           rock_s_sd = map_dbl(filtered, ~sd(.x$rock)),
           rain_s_sd = map_dbl(filtered, ~sd(.x$rain)),
           em_rc_ca = map_dbl(filtered, ~mean(.x$Ca_SO4_rock)* 17.49987),
           em_rc_ca_sd = map_dbl(filtered, ~sd(.x$Ca_SO4_rock)* 17.49987),
           em_rc_mg = map_dbl(filtered, ~mean(.x$Mg_SO4_rock)* 6.040544),
           em_rc_mg_sd = map_dbl(filtered, ~sd(.x$Mg_SO4_rock)* 6.040544),
           em_rc_na = map_dbl(filtered, ~mean(.x$Na_SO4_rock)* 1.709566),
           em_rc_k = map_dbl(filtered, ~mean(.x$K_SO4_rock)* 1.963759),
           em_rc_cl = map_dbl(filtered, ~mean(.x$Cl_SO4_rock)* 2.98167),
           em_rn_ca = map_dbl(filtered, ~mean(.x$Ca_SO4_rain)* 17.49987),
           em_rn_mg = map_dbl(filtered, ~mean(.x$Mg_SO4_rain)* 6.040544),
           em_rn_mg_sd = map_dbl(filtered, ~sd(.x$Mg_SO4_rain)* 6.040544),
           em_rn_na = map_dbl(filtered, ~mean(.x$Na_SO4_rain)* 1.709566),
           em_rn_k = map_dbl(filtered, ~mean(.x$K_SO4_rain)* 1.963759),
           em_rn_k_sd = map_dbl(filtered, ~sd(.x$K_SO4_rain)* 1.963759),
           em_rn_cl = map_dbl(filtered, ~mean(.x$Cl_SO4_rain)* 2.98167))
  ) %>%
  reduce(full_join, by = "sample")
