# Use this file to define your generic methods, e.g. for plots
from core.math_utils import lin2db
import pandas as pd

def values_computed(network, path, signal_power):
    total_latency=0.0
    total_noise_power=0.0
    snr=0
    for i in range(len(path)-1):
        current_label=path[i]
        next_label=path[i+1]
        line_label=current_label+next_label
        line=network.lines.get(line_label)
        if line:
            total_latency+=line.latency_generation()
            total_noise_power+=line.noise_generation(signal_power)
            snr=signal_power/total_noise_power
    total_snr_db=lin2db(snr)
    return total_latency, total_noise_power, total_snr_db

def create_dataframe(network, signal_power_w):
    all_paths_data=[]
    for source_label in network.nodes:
        for destination_label in network.nodes:
            if source_label!=destination_label:
                paths=network.find_paths(source_label, destination_label)
                for path in paths:
                    path_string="->".join(path)
                    total_latency, total_noise_power, total_snr_db=values_computed(network, path, signal_power_w)
                    all_paths_data.append([path_string, total_latency, total_noise_power, total_snr_db])
    columns=["Path"  , "      Total Latency (s)"  , "    Total Noise Power (W)  "  , "  SNR (dB)  "]
    paths_df=pd.DataFrame(all_paths_data, columns=columns)
    return paths_df