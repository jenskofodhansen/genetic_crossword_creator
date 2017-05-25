import random
from functools import reduce
from builtins import filter
from itertools import accumulate

# This char is the one that represents a block in the crossword
blockchar = '#'

# The allowed letters
allowed_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'y', 'æ', 'ø', 'å', blockchar]

# The vocabulary
vocabulary = set()
    
# Dimensions of cross word
cross_height = 4
cross_width = 4

# GA parameters
gene_pool_size = 1000
mutate_probability = 0.05 # 5 percent chance of mutating a genome
number_of_elite_genes = int(gene_pool_size*0.01)
number_of_epochs = 1000


# Create an array of randomly chosen letters
def create_random_chromosome():
    return [random.choice(allowed_letters) for i in range(cross_height*cross_width)]


# Pretty print of the crossword chromosome
def print_crossword(crossword):
    for idx in range(0, cross_width * cross_height, cross_width):
        print(crossword[idx:idx + cross_width])
     
        
# Evaluate a single strings fitness
def get_crossline_fitness(crossline):
    fitness = 0
    
    # We take words from start until we hit either the end or the block character
    words = ''.join(crossline).split(blockchar)
    
    # For each word, they count if the match
    for word in words:
        if word in vocabulary:
            fitness += len(word)    
            
    return fitness
 
 
# Evaluate the whole crossword       
def get_crossword_fitness(crossword):
    fitness = 0
    
    # First we do row evaluation. 
    for idx in range(0, cross_width * cross_height, cross_width):
        row = crossword[idx:idx + cross_width]
        fitness += get_crossline_fitness(row)
        
    # Then we do column evaluation
    for idx in range(0, cross_width):
        column = crossword[idx:idx+(cross_height * cross_width):cross_width]
        fitness += get_crossline_fitness(column)
    
    return fitness


# Determine if all words in a line is in the vocabulary
def is_crossline_valid(crossline):
    # We take words from start until we hit either the end or the block character
    words = ''.join(crossline).split(blockchar)
    words = filter(lambda x: len(x)>0, words)
    
    # For each word, they count if the match
    for word in words:
        if word not in vocabulary:
            return False    
            
    return True

 
# Validate the whole crossword (are all words in the vocabulary?)      
def is_crossword_valid(crossword):
    # First we do row evaluation. 
    for idx in range(0, cross_width * cross_height, cross_width):
        row = crossword[idx:idx + cross_width]
        if is_crossline_valid(row) is False:
            return False
        
    # Then we do column evaluation
    for idx in range(0, cross_width):
        column = crossword[idx:idx+(cross_height * cross_width):cross_width]
        if is_crossline_valid(column) is False:
            return False
    
    return True


# Breed a new chromosome by fusing two chromosomes at a randomly picked breakpoint. Apply a small chance of mutating the chromosome
def pair_chromosomes(father, mother):
    breakpoint = random.randint(0, cross_width * cross_height)
    
    father_gene = father[1]
    mother_gene = mother[1]
    
    child = father_gene[:breakpoint] + mother_gene[breakpoint:]
    
    # Mutating the chromosome on genome level
    for i in range(0, cross_width * cross_height):
        if random.random() < mutate_probability:
            child[i] = random.choice(allowed_letters)
            
    return child


'''
Pick a chromosome by fitness. This method uses roulette picking, where the chance of a chromosome
being picked is equal to its fitness. 
'''
def pick_by_fitness(chromosomes_with_fitness, fitness_sum):
    # a random int between 0 and the total fitness
    roulette = random.randint(0, fitness_sum)
    
    ''' 
    This line first maps only the fitness from the set of fitness and chromosome 
    After this, it makes the accumulated fitness list using the itertools library
    This accumulated list can be used to look up our chromosome picked by the roulette    
    '''
    accumulated_fitness = list(accumulate(map(lambda x: x[0], chromosomes_with_fitness)))
    
    idx=0;
    for fitness in accumulated_fitness:
        if roulette < fitness:
            return chromosomes_with_fitness[idx]
    
        idx += 1
        
    return random.sample(chromosomes_with_fitness, 1)[0] 


# The genetic algorithm for finding crosswords
def start_ga():
    # Create pool of random chromosomes
    chromosomes = [create_random_chromosome() for i in range(gene_pool_size)]
    
    # The actual GA process
    for epoch in range(0, number_of_epochs):
        # Make a list of sets containing the chromosome fitness, as well as the chromosome itself
        chromosomes_with_fitness = [(get_crossword_fitness(chromosomes[i]), chromosomes[i]) for i in range(gene_pool_size)]
        
        # Sort the list to have fittest chromosomes first
        chromosomes_with_fitness.sort(reverse = True)
        
        # We use the sum for roulette picking and finding the average
        fitness_sum = reduce(lambda x,y: (x[0]+y[0],), chromosomes_with_fitness)[0]
                    
        # The new population starts with the x elite chromosomes from the previous epoch
        new_pop = [chromosomes_with_fitness[i][1] for i in range(0, number_of_elite_genes)]
        
        # The rest of the population is breeds of randomly picked chromosomes
        breeds = [pair_chromosomes(pick_by_fitness(chromosomes_with_fitness, fitness_sum), pick_by_fitness(chromosomes_with_fitness, fitness_sum)) for x in range(0, gene_pool_size-number_of_elite_genes)]
        chromosomes = new_pop + breeds
        
        best_crossword = new_pop[0]
        
        avg_fitness = fitness_sum/gene_pool_size
        
        # Print stats every 10th epoch
        if epoch%10 is 0:
            print("epoch {} ended - best fitness={} - average fitness={}".format(epoch, chromosomes_with_fitness[0][0], avg_fitness))
        
        # Break if we found a solution (every word exists in the vocabulary)
        if is_crossword_valid(best_crossword) is True:
            print("solution found:")
            break
            
    # Pretty print the found solution
    print_crossword(best_crossword)
    
            
if __name__ == "__main__":
    print("Reading vocabulary!")
    
    voc_file = open("da_DK.dic.txt", encoding="utf-8")
    voc_data = voc_file.readlines()
    
    # Strip newline character
    voc_data = list(map(lambda x: x.strip('\n'), voc_data))
    
    # Filter out words longer than longest dimension of crossword (no needs for words longer than the largest dimension in the crossword)
    vocabulary = set(filter(lambda x: len(x)<=max(cross_width, cross_height), voc_data))
    
    print("starting crossword creator!")
    start_ga()
    
    