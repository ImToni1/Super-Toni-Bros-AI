import pygame
import os
import random
import sys
import pickle

from .ai_brain import Brain, AIAction
from .game_simulation import run_simulation_for_brain


POPULATION_SIZE = 80 # Broj jedinki (mozgova) u jednoj generaciji
INSTRUCTION_COUNT = 80 # Početni broj instrukcija za svaki mozak
MUTATION_RATE = 0.20 # Vjerojatnost mutacije pojedine instrukcije
NEW_INSTRUCTION_CHANCE = 0.10 # Vjerojatnost da se instrukcija zamijeni potpuno novom
ELITISM_COUNT = 12 # Broj najboljih jedinki koje direktno prelaze u sljedeću generaciju
NUM_GENERATIONS = 1000 # Maksimalan broj generacija za treniranje

current_dir = os.path.dirname(os.path.abspath(__file__))

LEVEL_FILENAME = "level.txt"
LEVEL_FILEPATH = os.path.join(current_dir, "..", "core", LEVEL_FILENAME) #

SAVED_BRAIN_FILENAME = "best_ai_path.pkl" 
SAVED_BRAIN_FILEPATH = os.path.join(current_dir, SAVED_BRAIN_FILENAME)


def save_ai_instructions(instructions_list, filepath):
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(instructions_list, f) # Spremanje liste instrukcija pomoću pickle
    except Exception as e:
        pass # Greške pri spremanju se tiho ignoriraju

def load_ai_instructions(filepath):
    try:
        with open(filepath, 'rb') as f:
            instructions = pickle.load(f) # Učitavanje liste instrukcija
        return instructions
    except FileNotFoundError:
        return None # Ako datoteka ne postoji, vraća None
    except Exception as e:
        return None # Ostale greške pri učitavanju također vraćaju None

ai_has_won_session = False # Zastavica koja označava je li AI pobijedio u trenutnoj sesiji treniranja

def run_genetic_algorithm():
    global ai_has_won_session
    ai_has_won_session = False

    population = []
    loaded_instructions = load_ai_instructions(SAVED_BRAIN_FILEPATH)

    if loaded_instructions:
        # Ako postoji spremljeni AI, pokreće se demonstracija
        best_loaded_brain = Brain(len(loaded_instructions), randomize_instructions=False)
        best_loaded_brain.set_instructions(loaded_instructions) #
        run_simulation_for_brain(best_loaded_brain, LEVEL_FILEPATH, render=True, current_generation="SPREMLJENI AI", brain_idx=0)
        ai_has_won_session = True # Postavlja zastavicu da je AI "pobijedio" (jer je učitan pobjednički)
        return # Prekida daljnje treniranje
    else:
        # Ako nema spremljenog AI, stvara se nova populacija
        population = [Brain(INSTRUCTION_COUNT) for _ in range(POPULATION_SIZE)]


    best_fitness_overall = -float('inf') # Najbolji fitness postignut tijekom svih generacija
    best_brain_overall = None # Najbolji mozak pronađen

    for gen_num in range(NUM_GENERATIONS): # Glavna petlja genetskog algoritma
        if ai_has_won_session: # Ako je AI pobijedio, prekida se treniranje
            break

        generation_has_winner_this_gen = False # Je li u ovoj generaciji pronađen pobjednik

        for i, brain_agent in enumerate(population):
            render_this_brain = False # Određuje hoće li se trenutna simulacija iscrtavati
            if gen_num % 10 == 0 and i == 0: render_this_brain = True # Iscrtaj prvu jedinku svake 10. generacije
            elif gen_num < 5 and i < 3: render_this_brain = True # Iscrtaj prve 3 jedinke u prvih 5 generacija
            
            fitness = run_simulation_for_brain(brain_agent, LEVEL_FILEPATH, render=render_this_brain, current_generation=gen_num+1, brain_idx=i)

            if brain_agent.fitness >= 1500000: # Arbitrarna granica fitnessa koja označava pobjedu
                generation_has_winner_this_gen = True
                ai_has_won_session = True # Postavlja globalnu zastavicu o pobjedi
                if brain_agent.fitness > best_fitness_overall:
                    best_fitness_overall = brain_agent.fitness
                    best_brain_overall = brain_agent.clone()
                    save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH) # Sprema pobjednički AI
            
            if ai_has_won_session and generation_has_winner_this_gen: # Ako je pobjednik nađen, prekida se evaluacija ostalih u generaciji
                break


        population.sort(key=lambda b: b.fitness, reverse=True) # Sortira populaciju po fitnessu, najbolji prvi

        if population and population[0].fitness > best_fitness_overall:
            best_fitness_overall = population[0].fitness
            best_brain_overall = population[0].clone()
            if best_fitness_overall >= 1500000 and not ai_has_won_session: # Još jedna provjera za spremanje ako je pobjeda ostvarena
                ai_has_won_session = True
                save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH) #


        avg_fitness = sum(b.fitness for b in population) / POPULATION_SIZE if population else 0

        if ai_has_won_session: # Ponovna provjera za prekid vanjske petlje
            break

        # Stvaranje sljedeće generacije
        next_generation_brains = []
        if population:
            # Elitizam: Najbolje jedinke prelaze direktno
            for i in range(ELITISM_COUNT):
                if i < len(population):
                    next_generation_brains.append(population[i].clone())

            num_to_generate = POPULATION_SIZE - len(next_generation_brains) # Koliko novih jedinki treba stvoriti
            parent_pool_size = POPULATION_SIZE // 2 # Veličina bazena roditelja za križanje
            parent_pool = population[:parent_pool_size] # Uzima se bolja polovica populacije kao roditelji
            if not parent_pool: # Osigurava da bazen roditelja nije prazan
                parent_pool = population[:max(1, ELITISM_COUNT if ELITISM_COUNT < len(population) else len(population))]


            for _ in range(num_to_generate): # Stvaranje novih jedinki križanjem i mutacijom
                if parent_pool:
                    parent1 = random.choice(parent_pool) # Nasumični odabir roditelja
                    child = parent1.clone()
                    child.mutate(MUTATION_RATE, NEW_INSTRUCTION_CHANCE) # Mutacija djeteta
                    next_generation_brains.append(child)
                else:
                    # Ako nema roditelja (npr. prva generacija ili greška), stvara nasumičnu jedinku
                    next_generation_brains.append(Brain(INSTRUCTION_COUNT))
            
            population = next_generation_brains
            while len(population) < POPULATION_SIZE: # Dopunjava populaciju ako je manja od željene veličine
                population.append(Brain(INSTRUCTION_COUNT))

    if best_brain_overall:
        # Prikaz najboljeg AI-a nakon završetka svih generacija (ili prijevremenog prekida zbog pobjede)
        current_instructions_count = len(best_brain_overall.instructions)
        target_instructions_display = int(INSTRUCTION_COUNT * 1.2) # Povećava broj instrukcija za prikaz, da AI ne stane prerano
        if current_instructions_count < target_instructions_display :
            needed_increase = target_instructions_display - current_instructions_count
            if needed_increase > 0:
                best_brain_overall.increase_moves(needed_increase)
        run_simulation_for_brain(best_brain_overall, LEVEL_FILEPATH, render=True, current_generation="FINALNI NAJBOLJI", brain_idx=0)
    else:
        # Ako nije pronađen nijedan zadovoljavajući AI (npr. ako NUM_GENERATIONS = 0)
        pass