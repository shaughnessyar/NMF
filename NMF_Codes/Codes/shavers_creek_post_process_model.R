#load package
library(tidyverse)

#import data
nmf_output <- read_csv("shavers_creek_NMF_output.csv")
norm_dat <- read_csv("shavers_creek_norm_data.csv")
model_inputs <- read_csv("shavers_creek_raw.csv")

#calculate errors for all valid models as SSE
total_nmf_mods <- list(
  norm_dat %>%
    mutate(sample = row_number()),
  nmf_output %>%
    arrange(sample)
) %>%
  reduce(full_join, by = "sample") %>%
  mutate(error = ((Ca_SO4-Ca_mod)^2) + ((Na_SO4-Na_mod)^2) + ((Mg_SO4-Mg_mod)^2) + ((K_SO4-K_mod)^2) + ((Cl_SO4-Cl_mod)^2) + ((NO3_SO4-NO3_mod)^2)) %>%
  nest(data = -sample)

#pull out 5th percentile best model and unnormalize endmember composition
sc_max <- model_inputs %>%
  select(contains("_SO4")) %>%
  summarise_all(max)

sc_nmf <- total_nmf_mods %>%
  mutate(n = map_dbl(data, ~nrow(.x)),
         ref = map_dbl(data, ~quantile(.x$error, 0.05, na.rm = T)),
         filtered = map2(data, ref, ~filter(.x, error < .y)),
         new_n = map_dbl(filtered, ~nrow(.x)),
         rock = map_dbl(filtered, ~mean(.x$rock, na.rm = T)),
         rock_sd = map_dbl(filtered, ~sd(.x$rock, na.rm = T)),
         rain = map_dbl(filtered, ~mean(.x$rain, na.rm = T)),
         rain_sd = map_dbl(filtered, ~sd(.x$rain, na.rm = T)),
         fert = map_dbl(filtered, ~mean(.x$fert, na.rm = T)),
         fert_sd = map_dbl(filtered, ~sd(.x$fert, na.rm = T)),
         em_rc_ca = map_dbl(filtered, ~mean(.x$Ca_SO4_rock)* sc_max$Ca_SO4),
         em_rc_mg = map_dbl(filtered, ~mean(.x$Mg_SO4_rock)* sc_max$Mg_SO4),
         em_rc_na = map_dbl(filtered, ~mean(.x$Na_SO4_rock)* sc_max$Na_SO4),
         em_rc_k = map_dbl(filtered, ~mean(.x$K_SO4_rock)* sc_max$K_SO4),
         em_rc_cl = map_dbl(filtered, ~mean(.x$Cl_SO4_rock)* sc_max$Cl_SO4),
         em_rc_no3 = map_dbl(filtered, ~mean(.x$NO3_SO4_rock)* sc_max$NO3_SO4),
         
         em_rn_ca = map_dbl(filtered, ~mean(.x$Ca_SO4_rain)* sc_max$Ca_SO4),
         em_rn_mg = map_dbl(filtered, ~mean(.x$Mg_SO4_rain)* sc_max$Mg_SO4),
         em_rn_na = map_dbl(filtered, ~mean(.x$Na_SO4_rain)* sc_max$Na_SO4),
         em_rn_k = map_dbl(filtered, ~mean(.x$K_SO4_rain)* sc_max$K_SO4),
         em_rn_cl = map_dbl(filtered, ~mean(.x$Cl_SO4_rain)* sc_max$Cl_SO4),
         em_rn_no3 = map_dbl(filtered, ~mean(.x$NO3_SO4_rain)* sc_max$NO3_SO4),
         
         em_ft_ca = map_dbl(filtered, ~mean(.x$Ca_SO4_fert)* sc_max$Ca_SO4),
         em_ft_mg = map_dbl(filtered, ~mean(.x$Mg_SO4_fert)* sc_max$Mg_SO4),
         em_ft_na = map_dbl(filtered, ~mean(.x$Na_SO4_fert)* sc_max$Na_SO4),
         em_ft_k = map_dbl(filtered, ~mean(.x$K_SO4_fert)* sc_max$K_SO4),
         em_ft_cl = map_dbl(filtered, ~mean(.x$Cl_SO4_fert)* sc_max$Cl_SO4),
         em_ft_no3 = map_dbl(filtered, ~mean(.x$NO3_SO4_fert)* sc_max$NO3_SO4)
  ) %>%
  list(., model_inputs) %>%
  bind_cols()
