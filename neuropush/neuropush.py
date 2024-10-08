from neuromutations import NullMutation, FloatReplacement, IntReplacement
from pyshgp.gp.search import SearchAlgorithm, SearchConfiguration
from pyshgp.push.instruction_set import InstructionSet
from networks import NeuralNetwork, visualize_network
from pyshgp.gp.selection import Lexicase, Tournament
from pyshgp.push.type_library import PushTypeLibrary
from pyshgp.gp.variation import VariationStrategy
from pyshgp.push.types import PushFloat, PushInt
from pyshgp.gp.individual import Individual
from pyshgp.gp.population import Population
from multiprocessing import freeze_support
from pyshgp.gp.genome import GeneSpawner
from pyshgp.push.atoms import Literal
from datetime import datetime
import numpy as np
import random
import os
from functools import lru_cache

# INITIALIZATION CONSTANTS
population_size = 200
max_generations = 20
print_genomes = False

MAX_HIDDEN_LAYERS = 3
MIN_HIDDEN_LAYERS = 0
MIN_LAYER_SIZE = 1
MAX_LAYER_SIZE = 16
MIN_WEIGHT_VALUE = -1.0
MAX_WEIGHT_VALUE = 1.0
MAX_WEIGHTS = MAX_LAYER_SIZE**2 * MAX_HIDDEN_LAYERS + MAX_LAYER_SIZE
TOTAL_GENES = MAX_HIDDEN_LAYERS + MAX_WEIGHTS
show_network = False
input_size = 6
output_size = 1

bold = '\033[1m'
endbold = '\033[0m'

# XOR dataset
X_2bit = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_2bit = np.array([[0], [1], [1], [0]])

X_4bit = np.array([[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 0, 1, 1],
                [0, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1],
                [1, 0, 0, 0], [1, 0, 0, 1], [1, 0, 1, 0], [1, 0, 1, 1],
                [1, 1, 0, 0], [1, 1, 0, 1], [1, 1, 1, 0], [1, 1, 1, 1]])
y_4bit = np.array([[0], [1], [1], [0], [1], [0], [0], [1],
                [1], [0], [0], [1], [0], [1], [1], [0]])

X_5bit = np.array([
    [0, 0, 0, 0, 0], [0, 0, 0, 0, 1], [0, 0, 0, 1, 0], [0, 0, 0, 1, 1],
    [0, 0, 1, 0, 0], [0, 0, 1, 0, 1], [0, 0, 1, 1, 0], [0, 0, 1, 1, 1],
    [0, 1, 0, 0, 0], [0, 1, 0, 0, 1], [0, 1, 0, 1, 0], [0, 1, 0, 1, 1],
    [0, 1, 1, 0, 0], [0, 1, 1, 0, 1], [0, 1, 1, 1, 0], [0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0], [1, 0, 0, 0, 1], [1, 0, 0, 1, 0], [1, 0, 0, 1, 1],
    [1, 0, 1, 0, 0], [1, 0, 1, 0, 1], [1, 0, 1, 1, 0], [1, 0, 1, 1, 1],
    [1, 1, 0, 0, 0], [1, 1, 0, 0, 1], [1, 1, 0, 1, 0], [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 0], [1, 1, 1, 0, 1], [1, 1, 1, 1, 0], [1, 1, 1, 1, 1]
])
y_5bit = np.array([
    [0], [1], [1], [0], [1], [0], [0], [0],
    [1], [0], [0], [0], [0], [0], [0], [1],
    [1], [0], [0], [0], [0], [0], [0], [1],
    [0], [0], [0], [1], [0], [1], [1], [0]
])   

# 6-bit XOR (Parity) inputs
X = np.array([
    [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1],
    [0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 1],
    [0, 0, 1, 0, 0, 0], [0, 0, 1, 0, 0, 1], [0, 0, 1, 0, 1, 0], [0, 0, 1, 0, 1, 1],
    [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 1], [0, 0, 1, 1, 1, 0], [0, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1], [0, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 1],
    [0, 1, 0, 1, 0, 0], [0, 1, 0, 1, 0, 1], [0, 1, 0, 1, 1, 0], [0, 1, 0, 1, 1, 1],
    [0, 1, 1, 0, 0, 0], [0, 1, 1, 0, 0, 1], [0, 1, 1, 0, 1, 0], [0, 1, 1, 0, 1, 1],
    [0, 1, 1, 1, 0, 0], [0, 1, 1, 1, 0, 1], [0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1], [1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 1, 1],
    [1, 0, 0, 1, 0, 0], [1, 0, 0, 1, 0, 1], [1, 0, 0, 1, 1, 0], [1, 0, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0], [1, 0, 1, 0, 0, 1], [1, 0, 1, 0, 1, 0], [1, 0, 1, 0, 1, 1],
    [1, 0, 1, 1, 0, 0], [1, 0, 1, 1, 0, 1], [1, 0, 1, 1, 1, 0], [1, 0, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 1], [1, 1, 0, 0, 1, 0], [1, 1, 0, 0, 1, 1],
    [1, 1, 0, 1, 0, 0], [1, 1, 0, 1, 0, 1], [1, 1, 0, 1, 1, 0], [1, 1, 0, 1, 1, 1],
    [1, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 1], [1, 1, 1, 0, 1, 0], [1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 1], [1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1]
])

# 6-bit XOR (Parity) outputs
y = np.array([
    [0], [1], [1], [0], [1], [0], [0], [0],
    [1], [0], [0], [0], [0], [0], [0], [1],
    [1], [0], [0], [0], [0], [0], [0], [1],
    [0], [0], [0], [1], [0], [1], [1], [0],
    [0], [1], [1], [0], [1], [0], [0], [0],
    [1], [0], [0], [0], [0], [0], [0], [1],
    [1], [0], [0], [0], [0], [0], [0], [1],
    [0], [0], [0], [1], [0], [1], [1], [0]
])


fitness_cache = {}

@lru_cache(maxsize=10000)
def cached_fitness_eval(architecture, weights):
    return fitness_eval(architecture, weights, X, y)

def fitness_eval(architecture, weights, X, y):
    try:
        architecture = list(architecture)
        full_layers = [input_size] + architecture + [output_size]
        network = NeuralNetwork(full_layers, weights)
        if show_network:
            visualize_network(network, 'show')

        predictions = network.predict(X)

        # Ensure predictions and y have the same shape
        predictions = predictions.reshape(-1, 1)
        y = y.reshape(-1, 1)

        # Calculate individual errors for each data point
        individual_errors = []
        for i in range(len(X)):
            mse = np.mean((predictions[i] - y[i])**2)
            individual_errors.append(mse)

        # Return as a numpy array
        return np.array(individual_errors)

    except Exception as e:
        print(f"Error in fitness evaluation: {str(e)}")
        return np.full(len(X), np.inf)  # Return an array of infinity values instead of None

def variation_strategy(spawner):
    variation_strategy = VariationStrategy()
    # variation_strategy.add(NullMutation(), 0.9)
    variation_strategy.add(IntReplacement(rate=1), 1)
    variation_strategy.add(FloatReplacement(rate=1), 1)
    
    return variation_strategy

class CustomSearch(SearchAlgorithm):
    def __init__(self, config, variation_strategy):
        super().__init__(config)
        self.variation_strategy = variation_strategy
        self.lexicase_selector = Lexicase(epsilon=True)
        self.tournament_selector = Tournament(tournament_size=3) # decrease tournament size for greater pressure
        self.num_gen = 2

    def step(self):
        """
        Evolve the population by selecting parents and producing children.
        10% elite
        20% random
        70% lexicase
        formerly 40% lexicase, 30% tournament
        """
        # Filter out individuals with invalid error vectors
        valid_individuals = Population([ind for ind in self.population if np.isfinite(ind.error_vector).all() and len(ind.error_vector) > 0])

        # Elitism: Keep the best 10%
        best_individuals = sorted(valid_individuals, key=lambda ind: ind.total_error)[:int(len(valid_individuals) * 0.1)]

        # Selection strategy sizes
        total_size = len(self.population) - len(best_individuals)
        random_size = int(total_size * 0.2)
        remaining_size = total_size - random_size
        lexicase_size = remaining_size # // 2  # Split remaining evenly between lexicase and tournament
        # tournament_size = remaining_size - lexicase_size

        # downsize tournament size if necessary
        self.tournament_selector.tournament_size = min(self.tournament_selector.tournament_size, len(valid_individuals))

        parents_lexicase = self.lexicase_selector.select(valid_individuals, n=lexicase_size)
        # parents_tournament = self.tournament_selector.select(valid_individuals, n=tournament_size)
        randomly_generated = [custom_spawn_genome(np.random.randint(MIN_HIDDEN_LAYERS, MAX_HIDDEN_LAYERS + 1), MAX_WEIGHTS) for _ in range(random_size)]
        random_parents = [Individual(genome, self.config.signature) for genome in randomly_generated]
        parents = parents_lexicase # + parents_tournament

        # print(f"  {len(parents)} parents selected, {len(set(id(parent) for parent in parents))} unique")
        children = best_individuals + random_parents

        unique_parents = set(genome_to_hashable(ind.genome) for ind in parents)
        unique_elite_genomes = set(genome_to_hashable(ind.genome) for ind in best_individuals)
        unique_random_genomes = set(genome_to_hashable(ind.genome) for ind in random_parents)
        unique_lexicase_genomes = set(genome_to_hashable(ind.genome) for ind in parents_lexicase)
        # unique_tournament_genomes = set(genome_to_hashable(ind.genome) for ind in parents_tournament)

        # print(f"{bold}Unique parents:{endbold}    {len(unique_parents)}/{len(parents)}")
        # print(f"  Elite            {len(unique_elite_genomes)}/{len(best_individuals)}")
        # print(f"  Random           {len(unique_random_genomes)}/{len(random_parents)}")
        # print(f"  Lexicase         {len(unique_lexicase_genomes)}/{len(parents_lexicase)}")
        # print(f"  Tournament       {len(unique_tournament_genomes)}/{len(parents_tournament)}")


        if print_genomes:
            print(f"\n{bold}GENERATION {self.num_gen}{endbold}")
            self.num_gen += 1
            print("---------------------------------")

            for ind in best_individuals:
                print("*last generation best individual")
                print(print_genome(ind.genome))

        for _ in range(len(self.population) - len(best_individuals) - len(random_parents)):
            op = np.random.choice(self.variation_strategy.elements)
            num_parents = op.num_parents
            selected_parents = random.sample(parents, num_parents) # is this problematic? is it needed?
            # print(f"  {len(selected_parents)} parents selected, {len(set(id(selected_parent) for selected_parent in parents))} unique")
            child_genome = op.produce([p.genome for p in parents], self.config.spawner) # not using selected_parents
            if print_genomes:
                print(print_genome(child_genome))
            child = Individual(child_genome, self.config.signature)
            children.append(child)

        self.population = Population(children)

        for child in self.population:
            architecture, weights = genome_extractor(child.genome)
            error = cached_fitness_eval(tuple(architecture), tuple(weights))
            if error is not None:
                child.error_vector = error
            else:
                child.error_vector = None

        return self.population
    
# Define ERC (Ephemeral Random Constant) generators
def weights_generator():
    return Literal(value=random.uniform(MIN_WEIGHT_VALUE, MAX_WEIGHT_VALUE), push_type=PushFloat)

def layer_size_generator():
    return Literal(value=random.randint(MIN_LAYER_SIZE, MAX_LAYER_SIZE), push_type=PushInt)

# generates genome with a specified number of ints for layers and floats for weights
def custom_spawn_genome(num_layers, num_weights):
    genome = []
    for _ in range(num_layers):
        genome.append(layer_size_generator())
    for _ in range(num_weights):
        genome.append(weights_generator())

    return genome

# transforms genome into a list of layer sizes and a list of weights
def genome_extractor(genome):
    layers = []
    weights = []
    for gene in genome:
        if isinstance(gene, Literal):
            if gene.push_type == PushInt:
                layers.append(gene.value)
            elif gene.push_type == PushFloat:
                weights.append(gene.value)
        else:
            print(f"Error: Unexpected gene type {type(gene)}")

    return layers, weights

# Display the genomes architecture and number of weights in the terminal
def print_genome(genome):
    int_values = list(str(input_size))
    float_values = []
    for gene in genome:
        if isinstance(gene, Literal):
            if gene.push_type == PushInt:
                int_values.append(str(gene.value))
            elif gene.push_type == PushFloat:
                float_values.append(f"{gene.value:.4f}")
    int_values.append(str(output_size))
    layers = '-'.join(int_values)
    weights = [float(value) for value in float_values]
    num_weights = len(weights)
    
    return f"{layers}\n{num_weights}\n"

def logger(layers, weights, error, pop_size, generations):
    current_time = datetime.now().strftime("%m/%d/%Y at %H:%M")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, "logs.txt")

    layers = [input_size] + layers + [output_size]
    
    with open(filename, "a") as file:
        file.write(f"{current_time}\n")
        file.write(f"Best Individual (population size: {pop_size}, generations: {generations})\n")
        file.write(f"{layers}\n")
        file.write(f"{error}\n")
        file.write(f"{weights}\n\n")
    
    print(f"{bold}Evolution complete!{endbold}")

    return None

def genome_to_hashable(genome):
    return tuple((gene.push_type, gene.value) for gene in genome if isinstance(gene, Literal))

def main():
    cached_fitness_eval.cache_clear() # Clear the cache before starting a new evolution

    print(f"{bold}Beginning evolution{endbold}")
    print(f"Population size: {population_size}, generations: {max_generations}\n")
    # Initialize PyshGP components
    instruction_set = InstructionSet().register_core()
    type_library = PushTypeLibrary(register_core=False)
    type_library.register(PushInt)
    instruction_set = InstructionSet(type_library=type_library)

    spawner = GeneSpawner(
        n_inputs=0,
        instruction_set=instruction_set,
        literals=[],
        erc_generators=[layer_size_generator, weights_generator],
    )

    try:
        # Create variation operator
        global variation_strategy
        variation_strategy = variation_strategy(spawner)    

        # Create search configuration
        search_config = SearchConfiguration(
            signature=None,  # not used atm
            evaluator=None,  # not used atm
            spawner=spawner,
            population_size=population_size,
            max_generations=max_generations,
            initial_genome_size=(TOTAL_GENES, TOTAL_GENES + 1),
            simplification_steps=0,
            error_threshold=0.0,
            selection="lexicase",
        )

        # Create custom search
        custom_search = CustomSearch(search_config, variation_strategy)
    except Exception as e:
        print(f"Error in CustomSearch initialization: {str(e)}")

    # Initialize the population
    population = []

    def evolve():
        nonlocal population
        if not population: # If it's the first generation, initialize the population
            population = []
            if print_genomes:
                print(f"{bold}GENERATION 1{endbold}")
                print("---------------------------------")
            for _ in range(search_config.population_size):
                HIDDEN_LAYERS = np.random.randint(MIN_HIDDEN_LAYERS, MAX_HIDDEN_LAYERS + 1)
                # HIDDEN_LAYERS = 0
                genome = custom_spawn_genome(HIDDEN_LAYERS, MAX_WEIGHTS)
                if print_genomes:
                    print(print_genome(genome))
                individual = Individual(genome, search_config.signature)
                # print(f"Initial individual: {display_genome(individual.genome)}") # FOR DEBUG
                population.append(individual)
        else:  # For subsequent generations, use the evolved population from CustomSearch.step()
            population = custom_search.step()

        custom_search.population = Population(population)

        # Evaluate each individual
        for individual in custom_search.population:
            architecture, weights = genome_extractor(individual.genome)
            # print(f"Architecture: {architecture}")
            error = fitness_eval(architecture, weights, X, y)
            if error is not None:
                individual.error_vector = error
            else:
                individual.error_vector = None
            # to log error vector
    
    # Evolution loop
    for generation in range(search_config.max_generations):
        try:
            evolve()
            # Print generation statistics
            print(f"{bold}Generation {generation + 1}:{endbold}")
            if len(custom_search.population) > 0:
                evaluated_individuals = [ind for ind in custom_search.population if ind.error_vector is not None]
                if evaluated_individuals:
                    # Calculate diversity
                    unique_genomes = set(genome_to_hashable(ind.genome) for ind in evaluated_individuals)
                    diversity = len(unique_genomes)
                    best_individual = min(evaluated_individuals, key=lambda ind: np.mean(ind.error_vector))
                    best_layers, best_weights = genome_extractor(best_individual.genome)
                    best_individuals = sorted(evaluated_individuals, key=lambda ind: ind.total_error)[:int(len(evaluated_individuals) * 0.1)]
                    print(f"  Diversity        {diversity}/{len(evaluated_individuals)}")
                    print(f"  Best network     {input_size} {best_layers} {output_size}")
                    print(f"  Median error     {bold}{np.median([np.mean(ind.error_vector) for ind in evaluated_individuals]):.2f}{endbold}")
                    print(f"  Elite error      {bold}{np.mean([np.mean(ind.error_vector) for ind in best_individuals]):.2f}{endbold}")
                    print(f"  Best error       {bold}{np.mean(best_individual.error_vector):.2f}{endbold}\n")
                else:
                    print("  No evaluated individuals in population!")
            else:
                print("  No individuals in population!")
            
            nn = NeuralNetwork([input_size] + best_layers + [output_size], best_weights)
            if np.mean((nn.predict(X) > 0.5) == y) > 0.9:
                logger(best_layers, best_weights, best_individual.error_vector, len(evaluated_individuals), generation + 1)

            if generation == search_config.max_generations - 1:
                visualize_network(nn, 'show')
                # for i in range(len(X)):
                    # print(f"Input: {X[i]} | Target: {y[i]} | Prediction: {nn.predict(X[i])} | Error: {best_individual.error_vector[i]}")
                print(f"{bold}Accuracy: {np.mean((nn.predict(X) > 0.5) == y) * 100}%{endbold}")

        except Exception as e:
            print(f"evolution loop error: {str(e)}")
            continue

if __name__ == '__main__':
    freeze_support()
    main()