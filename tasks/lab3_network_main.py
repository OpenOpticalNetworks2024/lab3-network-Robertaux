from pathlib import Path
from core.elements import Network
from core.utils import create_dataframe

# Exercise Lab3: Network

ROOT=Path(__file__).parent.parent
INPUT_FOLDER=ROOT/'resources'
file_input=INPUT_FOLDER/'nodes.json'

# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file

if __name__ == '__main__':
    network=Network(file_input)
    source='A'
    destination='C'
    paths=network.find_paths(source,destination)
    print(f"Paths between {source} and {destination}: {paths}")
    print('Pandas Dataframe:')
    paths_df=create_dataframe(network,signal_power_w=0.001)
    print(paths_df)
    network.draw()
    print('End of the simulation')
    paths_df.to_csv('weighted_path.csv', index=False)