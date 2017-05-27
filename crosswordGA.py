import random
from builtins import filter
from itertools import accumulate
from bisect import bisect
import re
from configparser import ConfigParser

# This char is the one that represents a block in the crossword
blockchar = '*'

# The allowed letters
allowed_letters = ['-', blockchar, 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'y', 'æ', 'ø', 'å']
letter_probabilites = () # These will be calculated

# The vocabulary
vocabulary = set()
    
# The following parameters are the default parameters, which are overriden by the config file
# Dimensions of cross word
cross_height = 4
cross_width = 4

blockchar_probablity = 0.05

# GA parameters
gene_pool_size = 1000
mutate_probability = 0.10 #chance of mutating a genome
number_of_elite_chromosomes = int(gene_pool_size*0.01)
number_of_new_chromosomes = int(gene_pool_size*0.2)
number_of_epochs = 10000

# Pick a random letter by weighted probability
def pick_random_gene():
    idx = bisect(letter_probabilites, random.random())
    
    letter = allowed_letters[idx]
    
    if random.random()<blockchar_probablity:
        letter = blockchar
    
    return letter

# Create an array of randomly chosen letters
def create_random_chromosome():
    return [pick_random_gene() for i in range(cross_height*cross_width)]


# Pretty print of the crossword chromosome
def print_crossword(crossword):
    for idx in range(0, cross_width * cross_height, cross_width):
        print(crossword[idx:idx + cross_width])
     

# Calculate fitness value per word
def get_word_fitness(word):
    max_fitness = 0
    
    if word in vocabulary:
        return len(word)
    
    words_of_len = filter(lambda x: len(x) is len(word), vocabulary)
    
    for voc_word in words_of_len:
        temp_fitness = sum(c1==c2 for c1,c2 in zip(word,voc_word))
        
        max_fitness = max(max_fitness, temp_fitness)
        
    return max_fitness**2
        
# Evaluate a single strings fitness
def get_crossline_fitness(crossline):
    fitness = 0
    
    line_as_string = ''.join(crossline)
    
    # We take words from start until we hit either the end or the block character
    words = line_as_string.split(blockchar)
    
    # For each word, they count if the match
    for word in words:
        if word in vocabulary:
            fitness += get_word_fitness(word)    
            
    if line_as_string.find(blockchar*2) >= 0:
        return fitness / 2
    
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
            child[i] = pick_random_gene()
            
    return child


'''
Pick a chromosome by fitness. This method uses roulette picking, where the chance of a chromosome
being picked is equal to its fitness. 
'''
def pick_by_fitness(chromosomes_with_fitness, fitness_sum):
    # a random int between 0 and the total fitness
    roulette = random.randint(0, int(fitness_sum))
    
    ''' 
    This line first maps only the fitness from the set of fitness and chromosome 
    After this, it makes the accumulated fitness list using the itertools library
    This accumulated list can be used to look up our chromosome picked by the roulette    
    '''
    
    # Unzip chromosomes with fitess
    fitness, chromosomes = zip(*chromosomes_with_fitness)
    accumulated_fitness = list(accumulate(fitness))
    idx = bisect(accumulated_fitness, roulette, 0, gene_pool_size-1)
    
    return chromosomes_with_fitness[idx]

# The genetic algorithm for finding crosswords
def start_ga():
    # Create pool of random chromosomes
    chromosomes = [create_random_chromosome() for i in range(gene_pool_size)]
    
    # The actual GA process
    for epoch in range(0, number_of_epochs):
        chromosome_fitness = [get_crossword_fitness(x) for x in chromosomes]
        
        # Make a list of sets containing the chromosome fitness, as well as the chromosome itself
        chromosomes_with_fitness = list(zip(chromosome_fitness, chromosomes))
        
        # Sort the list to have fittest chromosomes first
        chromosomes_with_fitness.sort(reverse = True)
        
        # We use the sum for roulette picking and finding the average
        fitness_sum = sum(chromosome_fitness)
                    
        # The new population starts with the x elite chromosomes from the previous epoch
        new_pop = [create_random_chromosome() for i in range(0, number_of_new_chromosomes)]
        elite_pop = [chromosomes_with_fitness[i][1] for i in range(0, number_of_elite_chromosomes)]
        
        # The rest of the population is breeds of randomly picked chromosomes
        breeds = [pair_chromosomes(pick_by_fitness(chromosomes_with_fitness, fitness_sum), pick_by_fitness(chromosomes_with_fitness, fitness_sum)) for x in range(0, gene_pool_size-number_of_elite_chromosomes-number_of_new_chromosomes)]
        chromosomes = new_pop + elite_pop + breeds
        
        best_crossword = elite_pop[0]
        
        avg_fitness = fitness_sum/gene_pool_size
        
        # Print stats every 10th epoch
        if epoch%5 is 0:
            print("epoch {} ended - best fitness={} - average fitness={}".format(epoch, chromosomes_with_fitness[0][0], avg_fitness))
            print_crossword(best_crossword)
        
        # Break if we found a solution (every word exists in the vocabulary)
        if is_crossword_valid(best_crossword) is True:
            print("solution found:")
            break
            
    # Pretty print the found solution
    print_crossword(best_crossword)
    
    
def read_config():
    config = ConfigParser()
    config.read("settings.ini")
    
    if not config.has_section("algorithmsettings"):
        return
    
    ga_settings = config["algorithmsettings"]
    
    blockchar_probablity = ga_settings.getfloat("blockchar_probablity")
    cross_height = ga_settings.getint("cross_height")
    cross_width = ga_settings.getint("cross_width")
    
    gene_pool_size = ga_settings.getint("gene_pool_size")
    mutate_probability = ga_settings.getfloat("mutate_probability")
    number_of_elite_chromosomes = ga_settings.getint("number_of_elite_chromosomes")
    number_of_new_chromosomes = ga_settings.getint("number_of_new_chromosomes")
    number_of_epochs = ga_settings.getint("number_of_epochs")
            
if __name__ == "__main__":
    read_config()
    
    print("Reading vocabulary!")
    
    voc_file = open("da_DK.dic.txt", encoding="utf-8")
    voc_data = voc_file.readlines()
    
    # Strip newline character
    voc_data = list(map(lambda x: x.strip('\n').lower(), voc_data))
    
    # Filter out words longer than longest dimension of crossword (no needs for words longer than the largest dimension in the crossword)
    vocabulary = set(filter(lambda x: len(x)<=max(cross_width, cross_height), voc_data))
    
    # Make a string with allowed letters for regex searching for words with characters not in accepted set
    allowchars = ''.join(allowed_letters)
    vocabulary = set(filter(lambda x: re.search("[^{}]".format(allowchars), x) is None, vocabulary))
    
    # Calculate letter probabilities by counting
    vocabulary_as_string = ''.join(vocabulary)
    
    letter_probabilites = [vocabulary_as_string.count(letter)/len(vocabulary_as_string) for letter in allowed_letters]
    letter_probabilites = list(accumulate(letter_probabilites))
        
    print("starting crossword creator!")
    start_ga()
    
    # python -m cProfile -s time crosswordGA.py 
    
    