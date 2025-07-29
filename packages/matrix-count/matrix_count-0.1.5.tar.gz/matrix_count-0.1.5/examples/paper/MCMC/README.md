## MCMC

This is meant to be a self-contained implementation of typical rewiring tricks in order to sample uniformly from the configuration model.

Particularly it is meant to compare the convergence of the MCMC algorithm on evaluting the path length between certain nodes within a configuration model compared to the SIS algorithm. 

Run `make` to compile the code.

Then, the code is run as follows:

```bash
./mcmc -i in.txt -o out.csv
```