import pygame
import os
import random
import sys
import pickle

from .ai_brain import Brain, AIAction
from .game_simulation import run_simulation_for_brain


POPULATION_SIZE = 80
INSTRUCTION_COUNT = 80
MUTATION_RATE = 0.20
NEW_INSTRUCTION_CHANCE = 0.10
ELITISM_COUNT = 12
NUM_GENERATIONS = 1000

current_dir = os.path.dirname(os.path.abspath(__file__))

LEVEL_FILENAME = "level.txt"
LEVEL_FILEPATH = os.path.join(current_dir, "..", "core", LEVEL_FILENAME)

SAVED_BRAIN_FILENAME = "best_ai_path.pkl"
SAVED_BRAIN_FILEPATH = os.path.join(current_dir, SAVED_BRAIN_FILENAME)


def save_ai_instructions(instructions_list, filepath):
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(instructions_list, f)
    except Exception as e:
        pass

def load_ai_instructions(filepath):
    try:
        with open(filepath, 'rb') as f:
            instructions = pickle.load(f)
        return instructions
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

ai_has_won_session = False

def run_genetic_algorithm():
    global ai_has_won_session
    ai_has_won_session = False

    population = []
    loaded_instructions = load_ai_instructions(SAVED_BRAIN_FILEPATH)

    if loaded_instructions:
        best_loaded_brain = Brain(len(loaded_instructions), randomize_instructions=False)
        best_loaded_brain.set_instructions(loaded_instructions) 
        run_simulation_for_brain(best_loaded_brain, LEVEL_FILEPATH, render=True, current_generation="SPREMLJENI AI", brain_idx=0)
        ai_has_won_session = True
        return
    else:
        population = [Brain(INSTRUCTION_COUNT) for _ in range(POPULATION_SIZE)]


    best_fitness_overall = -float('inf')
    best_brain_overall = None

    for gen_num in range(NUM_GENERATIONS):
        if ai_has_won_session:
            break

        generation_has_winner_this_gen = False

        for i, brain_agent in enumerate(population):
            render_this_brain = False
            if gen_num % 10 == 0 and i == 0: render_this_brain = True
            elif gen_num < 5 and i < 3: render_this_brain = True
            
            fitness = run_simulation_for_brain(brain_agent, LEVEL_FILEPATH, render=render_this_brain, current_generation=gen_num+1, brain_idx=i)

            if brain_agent.fitness >= 1500000:
                generation_has_winner_this_gen = True
                ai_has_won_session = True
                if brain_agent.fitness > best_fitness_overall:
                    best_fitness_overall = brain_agent.fitness
                    best_brain_overall = brain_agent.clone()
                    save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH)
            
            if ai_has_won_session and generation_has_winner_this_gen:
                break


        population.sort(key=lambda b: b.fitness, reverse=True)

        if population and population[0].fitness > best_fitness_overall:
            best_fitness_overall = population[0].fitness
            best_brain_overall = population[0].clone()
            if best_fitness_overall >= 1500000 and not ai_has_won_session:
                ai_has_won_session = True
                save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH)


        avg_fitness = sum(b.fitness for b in population) / POPULATION_SIZE if population else 0

        if ai_has_won_session:
            break

        next_generation_brains = []
        if population:
            for i in range(ELITISM_COUNT):
                if i < len(population):
                    next_generation_brains.append(population[i].clone())

            num_to_generate = POPULATION_SIZE - len(next_generation_brains)
            parent_pool_size = POPULATION_SIZE // 2
            parent_pool = population[:parent_pool_size]
            if not parent_pool: 
                parent_pool = population[:max(1, ELITISM_COUNT if ELITISM_COUNT < len(population) else len(population))]


            for _ in range(num_to_generate):
                if parent_pool:
                    parent1 = random.choice(parent_pool)
                    child = parent1.clone()
                    child.mutate(MUTATION_RATE, NEW_INSTRUCTION_CHANCE)
                    next_generation_brains.append(child)
                else:
                    next_generation_brains.append(Brain(INSTRUCTION_COUNT))
            
            population = next_generation_brains
            while len(population) < POPULATION_SIZE:
                population.append(Brain(INSTRUCTION_COUNT))

    if best_brain_overall:
        current_instructions_count = len(best_brain_overall.instructions)
        target_instructions_display = int(INSTRUCTION_COUNT * 1.2)
        if current_instructions_count < target_instructions_display :
            needed_increase = target_instructions_display - current_instructions_count
            if needed_increase > 0:
                best_brain_overall.increase_moves(needed_increase)
        run_simulation_for_brain(best_brain_overall, LEVEL_FILEPATH, render=True, current_generation="FINALNI NAJBOLJI", brain_idx=0)
    else:
        pass