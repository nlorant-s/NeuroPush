from pyshgp.gp.genome import GeneSpawner, genome_to_code
from pyshgp.push.instruction_set import InstructionSet
from pyshgp.push.types import PushInt, PushFloat, PushBool, PushStr

# Create an InstructionSet with core instructions
instruction_set = InstructionSet().register_core()

# Create a GeneSpawner
spawner = GeneSpawner(
    n_inputs=1,  # Number of input instructions
    instruction_set=instruction_set,
    literals=[1, 2.0, True, "Hello"],  # Example literals of different types
    erc_generators=[]  # No Ephemeral Random Constant generators for simplicity
)

# Generate a random genome
genome = spawner.spawn_genome(10)  # Generate a genome with 50 genes

# Print the genome
print("Generated Push Genome:")
for gene in genome:
    print(gene)

# Translate the genome to a Push program and print it
# push_program = genome_to_code(genome)

# print("\nTranslated Push Program:")
# print(push_program)

# Note: This program is randomly generated and may not perform any meaningful computation