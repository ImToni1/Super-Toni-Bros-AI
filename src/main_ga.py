# src/main_ga.py - AŽURIRANI KOD
import pygame
import os
import random
import sys

from .ai_brain import Brain                   # Relativni import
from .game_simulation import run_simulation_for_brain # Relativni import

# Broj AI agenata u svakoj generaciji
POPULATION_SIZE = 80
# Broj instrukcija (poteza) koje svaki AI agent ima
INSTRUCTION_COUNT = 80
# Vjerojatnost mutacije svake instrukcije
MUTATION_RATE = 0.20
# Vjerojatnost da se potpuno nova instrukcija pojavi
NEW_INSTRUCTION_CHANCE = 0.10
# Broj najboljih agenata koji se direktno prenose u sljedeću generaciju
ELITISM_COUNT = 12
# Ukupan broj generacija koje će algoritam odraditi
NUM_GENERATIONS = 1000 # Ovo postaje maksimalan broj generacija ako AI ne pobijedi ranije

current_dir = os.path.dirname(os.path.abspath(__file__))

LEVEL_FILENAME = "level.txt"
LEVEL_FILEPATH = os.path.join(current_dir, LEVEL_FILENAME)

# Varijabla za praćenje da li je AI pobijedio
ai_has_won = False

def run_genetic_algorithm():
    global ai_has_won # Koristimo globalnu varijablu za prekid
    ai_has_won = False # Resetiraj status pobjede na početku

    population = [Brain(INSTRUCTION_COUNT) for _ in range(POPULATION_SIZE)]

    best_fitness_overall = -float('inf')
    best_brain_overall = None

    print(f"Starting GA: Population={POPULATION_SIZE}, Instructions/Brain={INSTRUCTION_COUNT}, Max Generations={NUM_GENERATIONS}")
    print(f"Level file: {LEVEL_FILEPATH}")
    if not os.path.exists(LEVEL_FILEPATH):
        print(f"ERROR: Level file not found at {LEVEL_FILEPATH}")
        return

    for gen_num in range(NUM_GENERATIONS):
        if ai_has_won: # Ako je AI pobijedio u prethodnoj generaciji, prekini
            print(f"\nAI je pronašao pobjedničko rješenje u generaciji {gen_num}! Prekidam daljnje generacije.")
            break

        print(f"\n--- Generation {gen_num + 1} ---")

        generation_has_winner = False # Zastavica za pobjednika u trenutnoj generaciji

        for i, brain_agent in enumerate(population):
            render_this_brain = False
            if gen_num % 10 == 0 and i == 0:
                render_this_brain = True
            elif gen_num < 5 and i < 3:
                render_this_brain = True
            
            # Proslijedi informaciju da li je AI već pobijedio u run_simulation_for_brain
            # da bi se mogla provjeriti zastavica `game_won_by_ai` koja se tamo postavlja.
            # Ili, još bolje, neka run_simulation_for_brain vrati i status pobjede.
            # Za sada, oslanjat ćemo se na fitness vrijednost.
            # Pretpostavka: Fitness za pobjedu je vrlo visok (npr. > 1000000)
            
            fitness = run_simulation_for_brain(brain_agent, LEVEL_FILEPATH, render=render_this_brain, current_generation=gen_num+1, brain_idx=i)
            brain_agent.fitness = fitness # Fitness se postavlja unutar run_simulation_for_brain

            # Provjera da li je ovaj mozak pobijedio na temelju fitnessa
            # Ovo ovisi o tome kako je fitness za pobjedu definiran u run_simulation_for_brain
            # U run_simulation_for_brain, ako je game_won_by_ai, fitness dobiva +1000000
            if fitness >= 1000000: # Ako je fitness dovoljno visok da indicira pobjedu
                print(f"  Brain {i} je POBIJEDIO u generaciji {gen_num + 1} s fitnessom: {fitness:.2f}")
                generation_has_winner = True
                ai_has_won = True # Postavi globalnu zastavicu


            if render_this_brain:
                 print(f"  Brain {i} (rendered) Fitness: {fitness:.2f}")

        population.sort(key=lambda b: b.fitness, reverse=True)

        current_best_fitness = population[0].fitness
        if current_best_fitness > best_fitness_overall:
            best_fitness_overall = current_best_fitness
            best_brain_overall = population[0].clone()

        avg_fitness = sum(b.fitness for b in population) / POPULATION_SIZE
        print(f"Generation {gen_num + 1}: Best Fitness = {population[0].fitness:.2f}, Avg Fitness = {avg_fitness:.2f}, Overall Best = {best_fitness_overall:.2f}")

        if generation_has_winner: # Ako je netko pobijedio u ovoj generaciji
            print(f"Pobjednik pronađen u generaciji {gen_num + 1}! Najbolji ukupni fitness: {best_fitness_overall:.2f}")
            # ai_has_won je već postavljen na True
            # Petlja će se prekinuti na početku sljedeće iteracije

        # Ako AI nije pobijedio, nastavi s kreiranjem sljedeće generacije
        if not ai_has_won:
            next_generation_brains = []
            for i in range(ELITISM_COUNT):
                if i < len(population):
                    next_generation_brains.append(population[i].clone())

            num_to_generate = POPULATION_SIZE - len(next_generation_brains)
            parent_pool_size = POPULATION_SIZE // 2
            parent_pool = population[:parent_pool_size]
            if not parent_pool:
                parent_pool = population[:max(1, ELITISM_COUNT)]

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

            if best_brain_overall and best_brain_overall.current_instruction_number >= len(best_brain_overall.instructions) * 0.90:
                print("Best brain overall is running out of moves. Increasing instruction count for all brains.")
                new_instruction_count = len(best_brain_overall.instructions) + (INSTRUCTION_COUNT // 4)
                for brain_agent in population:
                    if len(brain_agent.instructions) < new_instruction_count:
                        brain_agent.increase_moves(new_instruction_count - len(brain_agent.instructions))
                if best_brain_overall and len(best_brain_overall.instructions) < new_instruction_count:
                     best_brain_overall.increase_moves(new_instruction_count - len(best_brain_overall.instructions))

    # Kraj petlje generacija
    if ai_has_won:
        print("\n--- Genetski Algoritam Završen - AI JE POBIJEDIO! ---")
    else:
        print(f"\n--- Genetski Algoritam Završen - Dosegnut maksimalan broj generacija ({NUM_GENERATIONS}) ---")
        
    if best_brain_overall:
        print(f"Najbolji ukupni Fitness postignut: {best_fitness_overall:.2f}")
        print("Pokretanje simulacije za najbolji pronađeni mozak s prikazom...")
        
        # Osiguraj da najbolji mozak ima dovoljno instrukcija za finalni prikaz
        # (Ovaj dio je već bio tu, može ostati)
        if len(best_brain_overall.instructions) < INSTRUCTION_COUNT * 1.2 : 
            needed_increase = int(INSTRUCTION_COUNT * 1.2) - len(best_brain_overall.instructions)
            if needed_increase > 0:
                best_brain_overall.increase_moves(needed_increase)

        run_simulation_for_brain(best_brain_overall, LEVEL_FILEPATH, render=True, current_generation="FINALNI NAJBOLJI", brain_idx=0)
    else:
        print("Nije pronađen nijedan mozak (ovo se ne bi smjelo dogoditi).")

if __name__ == "__main__":
    pygame.init()
    run_genetic_algorithm()
    pygame.quit()
    sys.exit()