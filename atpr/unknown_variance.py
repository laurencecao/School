#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plot
total_obs = 2000
primary_mean = known_mean = 5
primary_var = 14
x = np.sqrt(primary_var)*np.random.randn(total_obs) + primary_mean
all_a = []
all_b = []
all_prec_guess = []
all_prec_doubt = []
prior_a=1/2.+1
prior_b=1/2.*np.sum((x[0]-primary_mean)**2)
f,axarr = plot.subplots(3)
axarr[0].plot(x)
for i in range(1,total_obs):
    posterior_a=prior_a+1/2.
    posterior_b=prior_b+1/2.*np.sum((x[i]-known_mean)**2)
    all_a.append(posterior_a)
    all_b.append(posterior_b)
    all_prec_guess.append(posterior_a/posterior_b)
    all_prec_doubt.append(posterior_a/(posterior_b**2))
    prior_a=posterior_a
    prior_b=posterior_b
axarr[1].plot(all_prec_guess)
axarr[2].plot(all_prec_doubt)
plot.show()
