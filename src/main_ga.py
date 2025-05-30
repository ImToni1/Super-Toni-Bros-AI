# src/main_ga.py - AŽURIRANI KOD SA SPREMANJEM/UČITAVANJEM
import pygame
import os
import random
import sys
import pickle # Za spremanje i učitavanje objekata

from .ai_brain import Brain, AIAction # AIAction je potreban za pickle ako spremamo cijele AIAction objekte
from .game_simulation import run_simulation_for_brain

# --- Parametri genetskog algoritma ---
POPULATION_SIZE = 80
INSTRUCTION_COUNT = 80 # Početni broj instrukcija
MUTATION_RATE = 0.20 
NEW_INSTRUCTION_CHANCE = 0.10 
ELITISM_COUNT = 12 
NUM_GENERATIONS = 1000 

# --- Putanje ---
current_dir = os.path.dirname(os.path.abspath(__file__))
LEVEL_FILENAME = "level.txt"
LEVEL_FILEPATH = os.path.join(current_dir, LEVEL_FILENAME)
SAVED_BRAIN_FILENAME = "best_ai_path.pkl" # Datoteka za spremanje najboljeg puta
SAVED_BRAIN_FILEPATH = os.path.join(current_dir, SAVED_BRAIN_FILENAME)


# === POMOĆNE FUNKCIJE ZA SPREMANJE I UČITAVANJE ===
def save_ai_instructions(instructions_list, filepath):
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(instructions_list, f)
        print(f"AI instrukcije uspješno spremljene u {filepath}")
    except Exception as e:
        print(f"Greška pri spremanju AI instrukcija: {e}")

def load_ai_instructions(filepath):
    try:
        with open(filepath, 'rb') as f:
            instructions = pickle.load(f)
        print(f"AI instrukcije uspješno učitane iz {filepath}")
        return instructions
    except FileNotFoundError:
        print(f"Datoteka {filepath} za spremljeni AI nije pronađena.")
        return None
    except Exception as e:
        print(f"Greška pri učitavanju AI instrukcija: {e}")
        return None
# ===============================================

ai_has_won_session = False # Zastavica za pobjedu unutar jedne sesije GA

def run_genetic_algorithm():
    global ai_has_won_session
    ai_has_won_session = False 

    population = []
    loaded_instructions = load_ai_instructions(SAVED_BRAIN_FILEPATH)

    if loaded_instructions:
        print("Pronađen spremljeni AI put. Koristim ga.")
        # Stvori jedan mozak s učitanim instrukcijama i pokreni ga direktno
        # ili ga koristi kao temelj za novu populaciju.
        # Za sada, ako postoji spremljeni put, pretpostavit ćemo da je to "pobjednički"
        # i samo ćemo ga demonstrirati. Nećemo pokretati cijeli GA.
        
        # Ako želiš samo demonstrirati spremljeni mozak:
        print("Demonstracija spremljenog najboljeg AI puta...")
        best_loaded_brain = Brain(len(loaded_instructions), randomize_instructions=False)
        best_loaded_brain.set_instructions(loaded_instructions)
        run_simulation_for_brain(best_loaded_brain, LEVEL_FILEPATH, render=True, current_generation="SPREMLJENI AI", brain_idx=0)
        print("Demonstracija završena.")
        ai_has_won_session = True # Smatramo da je sesija "pobijeđena" ako smo učitali i pokazali
        return # Prekini daljnje izvođenje GA ako smo samo demonstrirali spremljeni put
    else:
        print("Nema spremljenog AI puta. Pokrećem učenje od početka.")
        # Inicijaliziraj normalnu populaciju ako nema spremljenog puta
        population = [Brain(INSTRUCTION_COUNT) for _ in range(POPULATION_SIZE)]


    best_fitness_overall = -float('inf')
    best_brain_overall = None

    print(f"Starting GA: Population={POPULATION_SIZE}, Instructions/Brain={INSTRUCTION_COUNT}, Max Generations={NUM_GENERATIONS}")
    # ... (ostatak ispisa)

    for gen_num in range(NUM_GENERATIONS):
        if ai_has_won_session: 
            print(f"\nAI je pronašao pobjedničko rješenje! Prekidam daljnje generacije.")
            break

        print(f"\n--- Generation {gen_num + 1} ---")
        generation_has_winner_this_gen = False

        for i, brain_agent in enumerate(population):
            render_this_brain = False
            # Logika za renderiranje (može ostati ista)
            if gen_num % 10 == 0 and i == 0: render_this_brain = True
            elif gen_num < 5 and i < 3: render_this_brain = True
            
            fitness = run_simulation_for_brain(brain_agent, LEVEL_FILEPATH, render=render_this_brain, current_generation=gen_num+1, brain_idx=i)
            # brain_agent.fitness se postavlja unutar run_simulation_for_brain

            # Provjera pobjede na temelju fitnessa (npr. fitness > određeni prag za pobjedu)
            # U game_simulation.py, pobjeda dodaje +2000000 fitnessu.
            if brain_agent.fitness >= 1500000: # Prag za pobjedu (malo niži od samog bonusa za pobjedu)
                print(f"  Brain {i} je POBIJEDIO u generaciji {gen_num + 1} s fitnessom: {brain_agent.fitness:.2f}")
                generation_has_winner_this_gen = True
                ai_has_won_session = True # Postavi zastavicu za prekid GA
                # Odmah spremi ovaj pobjednički mozak
                if brain_agent.fitness > best_fitness_overall: # Osiguraj da je stvarno najbolji do sada
                    best_fitness_overall = brain_agent.fitness
                    best_brain_overall = brain_agent.clone()
                    save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH) # SPREMI POBJEDNIČKI PUT
                # Možemo prekinuti evaluaciju ostatka populacije u ovoj generaciji ako želimo
                # break # Ovo bi prekinulo for i, brain_agent... petlju


            if render_this_brain:
                 print(f"  Brain {i} (rendered) Fitness: {brain_agent.fitness:.2f}")
            
            # Ako je AI pobijedio, nema potrebe evaluirati ostatak populacije u ovoj generaciji
            if ai_has_won_session and generation_has_winner_this_gen:
                break


        population.sort(key=lambda b: b.fitness, reverse=True)

        # Ažuriraj najbolji ukupni mozak ako trenutni najbolji iz populacije ima veći fitness
        if population and population[0].fitness > best_fitness_overall:
            best_fitness_overall = population[0].fitness
            best_brain_overall = population[0].clone()
            # Ako ovaj najbolji također predstavlja pobjedu i ai_has_won_session još nije postavljen,
            # ažuriraj i spremi.
            if best_fitness_overall >= 1500000 and not ai_has_won_session:
                print(f"  Najbolji mozak generacije je POBJEDNIK! Fitness: {best_fitness_overall:.2f}")
                ai_has_won_session = True
                save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH)


        avg_fitness = sum(b.fitness for b in population) / POPULATION_SIZE if population else 0
        print(f"Generation {gen_num + 1}: Best Fitness = {population[0].fitness if population else 'N/A':.2f}, Avg Fitness = {avg_fitness:.2f}, Overall Best = {best_fitness_overall:.2f}")

        if ai_has_won_session: # Ako je netko pobijedio, prekini petlju generacija
            break 

        # Kreiranje sljedeće generacije (samo ako AI još nije pobijedio)
        next_generation_brains = []
        # ... (ostatak logike za elitizam, selekciju, mutaciju - ostaje uglavnom isti) ...
        if population : # Osiguraj da populacija nije prazna
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
                else: # Fallback ako je parent_pool i dalje prazan (ne bi trebao biti)
                    next_generation_brains.append(Brain(INSTRUCTION_COUNT))
            
            population = next_generation_brains
            while len(population) < POPULATION_SIZE: # Dopuni ako je potrebno
                population.append(Brain(INSTRUCTION_COUNT))

        # Povećanje broja poteza (ostaje isto)
        # ...

    # Kraj petlje generacija
    if ai_has_won_session and best_brain_overall:
        print("\n--- Genetski Algoritam Završen - AI JE POBIJEDIO I PUT JE SPREMLJEN! ---")
        # Već smo spremili pobjednički mozak čim je pronađen
    elif not ai_has_won_session:
        print(f"\n--- Genetski Algoritam Završen - Dosegnut maksimalan broj generacija ({NUM_GENERATIONS}) ---")
        if best_brain_overall:
            # Ako nije pobijedio, ali želimo spremiti najbolji postignuti rezultat do sada
            # save_ai_instructions(best_brain_overall.instructions, SAVED_BRAIN_FILEPATH)
            # print("Najbolji postignuti put (nije pobjednički) je spremljen.")
            pass # Odluči da li želiš spremiti i ako nije pobjeda
        
    if best_brain_overall:
        print(f"Najbolji ukupni Fitness postignut: {best_fitness_overall:.2f}")
        print("Pokretanje simulacije za najbolji pronađeni mozak s prikazom...")
        
        current_instructions_count = len(best_brain_overall.instructions)
        target_instructions_display = int(INSTRUCTION_COUNT * 1.2) # Za prikaz, možda treba više
        if current_instructions_count < target_instructions_display : 
            needed_increase = target_instructions_display - current_instructions_count
            if needed_increase > 0:
                best_brain_overall.increase_moves(needed_increase)

        run_simulation_for_brain(best_brain_overall, LEVEL_FILEPATH, render=True, current_generation="FINALNI NAJBOLJI", brain_idx=0)
    else:
        print("Nije pronađen nijedan mozak za prikaz.")

if __name__ == "__main__":
    pygame.init()
    run_genetic_algorithm()
    pygame.quit()
    sys.exit()