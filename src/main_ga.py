import pygame
import os
import random
import sys

from ai_brain import Brain
from game_simulation import run_simulation_for_brain

# Broj AI agenata u svakoj generaciji
POPULATION_SIZE = 30
# Broj instrukcija (poteza) koje svaki AI agent ima
INSTRUCTION_COUNT = 20
# Vjerojatnost mutacije svake instrukcije
MUTATION_RATE = 0.15
# Vjerojatnost da se potpuno nova instrukcija pojavi
NEW_INSTRUCTION_CHANCE = 0.05
# Broj najboljih agenata koji se direktno prenose u sljedeću generaciju
ELITISM_COUNT = 2
# Ukupan broj generacija koje će algoritam odraditi
NUM_GENERATIONS = 100

current_dir = os.path.dirname(os.path.abspath(__file__))

LEVEL_FILENAME = "level.txt"
LEVEL_FILEPATH = os.path.join(current_dir, LEVEL_FILENAME)

def run_genetic_algorithm():
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

        for i, brain_agent in enumerate(population):
            render_this_brain = (i == 0 and gen_num % 5 == 0)
            fitness = run_simulation_for_brain(brain_agent, LEVEL_FILEPATH, render=render_this_brain, current_generation=gen_num+1, brain_idx=i)
            brain_agent.fitness = fitness
            if render_this_brain:
                 print(f"  Brain {i} (rendered) Fitness: {fitness:.2f}")

        population.sort(key=lambda b: b.fitness, reverse=True)

        current_best_fitness = population[0].fitness
        if current_best_fitness > best_fitness_overall:
            best_fitness_overall = current_best_fitness
            best_brain_overall = population[0].clone()
        
        avg_fitness = sum(b.fitness for b in population) / POPULATION_SIZE
        print(f"Generation {gen_num + 1}: Best Fitness = {population[0].fitness:.2f}, Avg Fitness = {avg_fitness:.2f}, Overall Best = {best_fitness_overall:.2f}")

        next_generation_brains = []

        for i in range(ELITISM_COUNT):
            next_generation_brains.append(population[i].clone())

        num_to_generate = POPULATION_SIZE - ELITISM_COUNT
        parent_pool = population[:POPULATION_SIZE // 2]
        if not parent_pool:
            parent_pool = population[:ELITISM_COUNT] if ELITISM_COUNT > 0 else [population[0]]

        for _ in range(num_to_generate):
            parent = random.choice(parent_pool)
            child = parent.clone()
            child.mutate(MUTATION_RATE, NEW_INSTRUCTION_CHANCE)
            next_generation_brains.append(child)
        
        population = next_generation_brains

        if gen_num % 10 == 0 and gen_num > 0:
            if population[0].current_instruction_number >= len(population[0].instructions) * 0.95:
                print("Best brains are running out of moves. Increasing instruction count.")
                for brain_agent in population:
                    brain_agent.increase_moves(20)

    print("\n--- Genetic Algorithm Finished ---")
    if best_brain_overall:
        print(f"Overall Best Fitness: {best_fitness_overall:.2f}")
        print("Running simulation for the best brain overall with rendering...")
        run_simulation_for_brain(best_brain_overall, LEVEL_FILEPATH, render=True, current_generation="FINAL", brain_idx=0)
    else:
        print("No best brain found.")

if __name__ == "__main__":
    pygame.init() 
    run_genetic_algorithm()
    pygame.quit()
    sys.exit()