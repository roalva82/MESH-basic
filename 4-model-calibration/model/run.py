import subprocess
import pandas as pd
import numpy as np
import csv

def nse(simulated, observed):
	denominator = np.sum((observed - np.mean(observed)) ** 2)
	numerator = np.sum((simulated - observed) ** 2)
	nse = 1 - numerator / denominator
	return nse

# run mesh
mesh_command  = './sa_mesh'
subprocess.run([mesh_command])

# read simulated data
sim_df = pd.read_csv('./results/ROF_D.csv', header=None)
sim = sim_df[649].to_numpy()

# read observed data
obs_df = pd.read_csv('./data_obs/05BL027_Daily_Flow_ts.csv', skiprows=1, header=None, names=['ID','PARAM','Date','Flow','SYM'])
obs_df['Date'] = pd.to_datetime(obs_df['Date'])

# extract values for observed data
start_date = '1980-05-02'
end_date = '1980-05-29'
mask = (obs_df['Date'] >= start_date) & (obs_df['Date'] <= end_date)
obs = obs_df.loc[mask]['Flow'].to_numpy()

# compute and export metric
metric = -1.0*nse(sim,obs)


with open('./results/Metric.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([metric])
    

