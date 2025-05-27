import pygame # Potreban za pygame.QUIT event i druge konstante
import os
import random
import sys

# Dodaj src direktorij u sys.path ako se main_ga.py pokreće izvan src
# Ovo osigurava da se moduli iz src mogu importati.
current_dir = os.path.dirname(os.path.abspath(__file__))
# src_path = current_dir # Ako je main_ga.py u src
# sys.path.append(os.path.dirname(src_path)) # Dodaj roditeljski direktorij od src

from .ai_brain import Brain # Relativni import
from .game_simulation import run_simulation_for_brain # Relativni import

# Parametri Genetskog Algoritma
POPULATION_SIZE = 30        # Broj jedinki u populaciji
INSTRUCTION_COUNT = 150     # Početni broj instrukcija za svaki mozak
MUTATION_RATE = 0.15        # Šansa da pojedina instrukcija mutira
NEW_INSTRUCTION_CHANCE = 0.05 # Šansa da instrukcija bude zamijenjena potpuno novom
ELITISM_COUNT = 2           # Broj najboljih jedinki koje se direktno prenose u sljedeću generaciju
NUM_GENERATIONS = 100       # Ukupan broj generacija za evoluciju

# Putanja do datoteke s razinom (mora biti dostupna iz game_simulation)
LEVEL_FILENAME = "level.txt"
LEVEL_FILEPATH = os.path.join(current_dir, LEVEL_FILENAME) # Pretpostavka da je level.txt u istom dir kao main_ga.py ili src

def run_genetic_algorithm():
    # Inicijalizacija populacije
    population = [Brain(INSTRUCTION_COUNT) for _ in range(POPULATION_SIZE)]

    best_fitness_overall = -float('inf')
    best_brain_overall = None

    print(f"Starting GA: Population={POPULATION_SIZE}, Instructions/Brain={INSTRUCTION_COUNT}, Generations={NUM_GENERATIONS}")
    print(f"Level file: {LEVEL_FILEPATH}")
    if not os.path.exists(LEVEL_FILEPATH):
        print(f"ERROR: Level file not found at {LEVEL_FILEPATH}")
        return

    for gen_num in range(NUM_GENERATIONS):
        print(f"\n--- Generation {gen_num + 1} ---")

        # Evaluacija svake jedinke u populaciji
        for i, brain_agent in enumerate(population):
            # Povremeno prikaži jednu simulaciju radi vizualnog praćenja
            render_this_brain = (i == 0 and gen_num % 5 == 0) # Renderiraj najboljeg iz prethodne (sada na indeksu 0) svake 5. generacije
            
            fitness = run_simulation_for_brain(brain_agent, LEVEL_FILEPATH, render=render_this_brain, current_generation=gen_num+1, brain_idx=i)
            brain_agent.fitness = fitness # Fitness se već postavlja unutar run_simulation_for_brain
            if render_this_brain:
                 print(f"  Brain {i} (rendered) Fitness: {fitness:.2f}")

        # Sortiraj populaciju po fitnessu (najbolji prvo)
        population.sort(key=lambda b: b.fitness, reverse=True)

        current_best_fitness = population[0].fitness
        if current_best_fitness > best_fitness_overall:
            best_fitness_overall = current_best_fitness
            best_brain_overall = population[0].clone()
        
        avg_fitness = sum(b.fitness for b in population) / POPULATION_SIZE
        print(f"Generation {gen_num + 1}: Best Fitness = {population[0].fitness:.2f}, Avg Fitness = {avg_fitness:.2f}, Overall Best = {best_fitness_overall:.2f}")

        # Kreiranje sljedeće generacije
        next_generation_brains = []

        # 1. Elitizam: Prenesi najbolje jedinke direktno
        for i in range(ELITISM_COUNT):
            next_generation_brains.append(population[i].clone())

        # 2. Popuni ostatak populacije kroz selekciju, kloniranje i mutaciju
        # Jednostavna selekcija: nasumično odaberi roditelje iz gornje polovice populacije
        num_to_generate = POPULATION_SIZE - ELITISM_COUNT
        parent_pool = population[:POPULATION_SIZE // 2] # Roditelji su iz bolje polovice
        if not parent_pool: # Osiguraj da pool nije prazan ako je POPULATION_SIZE // 2 < ELITISM_COUNT
            parent_pool = population[:ELITISM_COUNT] if ELITISM_COUNT > 0 else [population[0]]


        for _ in range(num_to_generate):
            parent = random.choice(parent_pool)
            child = parent.clone()
            child.mutate(MUTATION_RATE, NEW_INSTRUCTION_CHANCE)
            next_generation_brains.append(child)
        
        population = next_generation_brains

        # Periodično povećaj broj poteza ako najbolji mozgovi koriste sve svoje instrukcije
        if gen_num % 10 == 0 and gen_num > 0: # Svakih 10 generacija
            if population[0].current_instruction_number >= len(population[0].instructions) * 0.95:
                print("Best brains are running out of moves. Increasing instruction count.")
                for brain_agent in population:
                    brain_agent.increase_moves(20) # Dodaj npr. 20 novih nasumičnih poteza

    print("\n--- Genetic Algorithm Finished ---")
    if best_brain_overall:
        print(f"Overall Best Fitness: {best_fitness_overall:.2f}")
        print("Running simulation for the best brain overall with rendering...")
        run_simulation_for_brain(best_brain_overall, LEVEL_FILEPATH, render=True, current_generation="FINAL", brain_idx=0)
    else:
        print("No best brain found.")

if __name__ == "__main__":
    # Osiguraj da Pygame može naći fontove itd.
    pygame.init() 
    run_genetic_algorithm()
    pygame.quit()
    sys.exit()