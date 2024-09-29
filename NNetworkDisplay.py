import pickle
import pygame
import neat
import os

WIN_WIDTH, WIN_HEIGHT = 700, 700


class Neuron:

    def __init__(self, id, x, y, radius):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, network_surface):
        pygame.draw.circle(network_surface, (0, 0, 255), (self.x, self.y), self.radius, 2)


class Connection:

    def __init__(self, start_neuron_id, end_neuron_id, weight, neurons_list):

        # test
        self.usefulness = 0
        self.useful = False

        for n in neurons_list:
            if n.id == start_neuron_id:
                self.start_neuron = n
                self.usefulness += 1
            if n.id == end_neuron_id:
                self.end_neuron = n
                self.usefulness += 1

        if self.usefulness == 2:
            self.useful = True

        if self.useful:
            self.start_pos = (self.start_neuron.x, self.start_neuron.y)
            self.end_pos = (self.end_neuron.x, self.end_neuron.y)
            self.width = round(abs(weight)+1)

        # different color if weight is negative?
        if weight >= 0:
            self.color = (0, 255, 0)
        else:
            self.color = (255, 0, 0)

    def draw(self, network_surface):
        pygame.draw.line(network_surface, self.color, self.start_pos, self.end_pos, self.width)


def load_network(config, genome):
    _inputs = set()
    for i in config.genome_config.input_keys:
        _inputs.add(i)

    _outputs = set()
    for o in config.genome_config.output_keys:
        _outputs.add(o)

    _used_nodes = set(genome.nodes.keys())
    _hidden = set()
    for n in _used_nodes:
        if n not in _inputs and n not in _outputs:
            _hidden.add(n)

    _connections = set()
    weighted_connections = set()
    for c in genome.connections.values():
        if c.enabled:
            input, output = c.key
            _connections.add((input, output))
            weighted_connections.add(((input, output), c.weight))

    net = neat.graphs.feed_forward_layers(_inputs, _outputs, _connections)

    _layers = []
    _layers.append(_inputs)
    for l in net:
        _layers.append(l)

    return _layers, weighted_connections


def load_test_network(config, genome):
    _inputs = set()
    for i in config.genome_config.input_keys:
        _inputs.add(i)

    _outputs = set()
    for o in config.genome_config.output_keys:
        _outputs.add(o)

    _connections = set()
    _connections.add((-3, 1))
    _connections.add((-3, 2))
    _connections.add((-2, 1))
    _connections.add((-2, 2))
    _connections.add((-1, 2))
    _connections.add((1, 3))
    _connections.add((1, 4))
    _connections.add((2, 3))
    _connections.add((3, 0))
    _connections.add((4, 0))

    weighted_connections = set()
    weighted_connections.add(((-3, 1), 0.1))
    weighted_connections.add(((-3, 2), 0.1))
    weighted_connections.add(((-2, 1), 0.6))
    weighted_connections.add(((-2, 2), -0.5))
    weighted_connections.add(((-1, 2), 0.1))
    weighted_connections.add(((1, 3), 0.2))
    weighted_connections.add(((1, 4), -0.3))
    weighted_connections.add(((2, 3), -0.3))
    weighted_connections.add(((3, 0), 0.3))
    weighted_connections.add(((4, 0), 0.7))


    net = neat.graphs.feed_forward_layers(_inputs, _outputs, _connections)

    _layers = []
    _layers.append(_inputs)
    for l in net:
        _layers.append(l)

    return _layers, weighted_connections


def draw_network(_win, _layers, _connections, NNsize=(400, 400), NNpos=(10, 10)):
    number_of_layers = len(_layers)
    node_radius = NNsize[0] / 4 / number_of_layers
    layer_gap = (NNsize[0] - 2 * node_radius) / (number_of_layers - 1)

    biggest_layer_size = 0
    for l in _layers:
        if len(l) > biggest_layer_size:
            biggest_layer_size = len(l)

    if biggest_layer_size == 1:
        node_gap = 0
    else:
        node_gap = (NNsize[1] - 2 * node_radius) / (biggest_layer_size - 1)

    # DRAWING
    net_surface = pygame.Surface(NNsize)
    net_surface.fill((255, 255, 255))

    # ADD NEURONS
    neurons = []

    for x, layer in enumerate(_layers):
        x_pos = node_radius + x * layer_gap
        # pygame.draw.line(net_surface, (255, 0, 0), (x_pos, 0), (x_pos, NNsize[1]), 2)   # RED LINE TO BE REMOVED
        y_offset = (biggest_layer_size - len(layer)) * node_gap / 2

        for y, node in enumerate(layer):
            y_pos = y_offset + node_radius + y * node_gap

            neurons.append(Neuron(node, x_pos, y_pos, node_radius))

    # ADD CONNECTIONS
    connections = []
    for c in _connections:
        connections.append(Connection(c[0][0], c[0][1], c[1], neurons))

    for neuron in neurons:
        neuron.draw(net_surface)
    for connection in connections:
        if connection.useful:
            connection.draw(net_surface)

    _win.blit(net_surface, NNpos)


def draw_windows(_win, layers, connections):
    bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    bg.fill((255, 255, 255))
    _win.blit(bg, (0, 0))

    draw_network(_win, layers, connections, (500, 500), (20, 20))

    pygame.display.update()


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_neat.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    with open("Flap_AI.pickle", "rb") as file:
        genome = pickle.load(file)

    layers, connections = load_network(config, genome)


    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        draw_windows(win, layers, connections)
