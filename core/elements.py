import json
from core.parameters import speed_light
import matplotlib.pyplot as plt
import math

class Signal_information:
    def __init__(self, signal_power, path):
        self._signal_power=signal_power
        self._noise_power=0.0
        self._latency=0.0
        self._path=path

    @property
    def signal_power(self):
        return self._signal_power

    @signal_power.setter
    def signal_power(self, sign):
        self._signal_power=sign

    def update_signal_power(self, increment_s):
        self._signal_power+=increment_s

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, nois):
        self._noise_power=nois

    def update_noise_power(self, increment_n):
        self._noise_power+=increment_n

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, val_lat):
        self._latency=val_lat

    def update_latency(self, increment_l):
        self._latency+=increment_l

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path_n):
        self._path=path_n

    def update_path(self, node_n):
        self._path.append(node_n)

    def update_path_c(self):
        self._path.pop(0)

class Node:
    def __init__(self, node_data):
        self._label=node_data.get("label", "")
        self._position=node_data.get("position", (0.0, 0.0))
        self._connected_nodes=node_data.get("connected_nodes", [])
        self._successive={}

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, val_s):
        self._successive=val_s

    def propagate(self, signal_info, node):
        signal_info.update_path_c()
        if signal_info.path():
            line_label=self.label+signal_info.path(0)
            if node in self._successive:
                self._successive[line_label].propagate(signal_info, node)

class Line:
    def __init__(self, label, length):
        self._label=label
        self._length=length
        self._successive={}

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._length

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, succ):
        self._successive=succ

    def latency_generation(self):
        speed=(2/3)*speed_light
        latency=self._length/speed
        return latency

    def noise_generation(self, signal_power):
        noise_power=1e-9*signal_power*self._length
        return noise_power

    def propagate(self, signal_info):
        signal_info.update_noise_power(self.noise_generation(signal_info.signal_power))
        signal_info.update_latency(self.latency_generation())
        if signal_info.path and signal_info.path[0] in self._successive:
            self._successive[signal_info.path[0]].propagate(signal_info)

class Network:
    def __init__(self, json_file):
        self._nodes={}
        self._lines={}
        if json_file is not None:
            with open(json_file) as f:
                data=json.load(f)
                for node_label, node_data in data.items():
                    self._nodes[node_label]=Node({
                        "label": node_label,
                        "connected_nodes": node_data["connected_nodes"],
                        "position": tuple(node_data["position"])
                    })
                for node_label, node in self._nodes.items():
                    for neighbor_label in node.connected_nodes:
                        line_label=node_label+neighbor_label
                        if line_label not in self._lines and neighbor_label in self._nodes:
                            line_length=math.dist(node.position, self._nodes[neighbor_label].position)
                            self._lines[line_label]=Line(line_label, line_length)
                self.connect()

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def connect(self):
        for node in self.nodes.values():
            node.successive={label: self.nodes[label] for label in node.connected_nodes}
        for line in self.lines.values():
            node_labels=list(line.label)
            line.successive={node_labels[0]: self.nodes[node_labels[0]], node_labels[1]: self.nodes[node_labels[1]]}

    def find_paths(self, source_label, destination_label):
        def search(current_node, path):
            if current_node.label==destination_label:
                all_paths.append(path.copy())
                return
            crossed.add(current_node.label)
            for neighbor_label, neighbor_node in current_node.successive.items():
                if neighbor_label not in crossed:
                    path.append(neighbor_label)
                    search(neighbor_node, path)
                    path.pop()
            crossed.remove(current_node.label)
        crossed = set()
        all_paths = []
        source_node=self.nodes[source_label]
        search(source_node, [source_label])
        return all_paths

    def propagate(self, signal_info):
        path=signal_info.path
        if len(path)<2:
            return signal_info
        for i in range(len(path)-1):
            line_label=f"{path[i]}-{path[i+1]}"
            line=self.lines.get(line_label)
            if line:
                line.propagate(signal_info)
        return signal_info

    def draw(self):
        for node in self.nodes.values():
            plt.scatter(node.position[0], node.position[1], label=node.label)
        for line in self.lines.values():
            node1=line.label[0]
            node2=line.label[1]
            x1, y1=self.nodes[node1].position
            x2, y2=self.nodes[node2].position
            plt.plot([x1, x2], [y1, y2], linestyle='--', color='black')
            mid_x=(x1+x2)/2
            mid_y=(y1+y2)/2
            distance=round(line.length, 2)
            plt.text(mid_x, mid_y, str(distance), horizontalalignment='center', verticalalignment='center')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.show()
