# src/ai_brain.py
import random

class AIAction:
    def __init__(self, is_jump, hold_time, x_direction):
        self.is_jump = is_jump
        self.hold_time = hold_time # Vrijeme trajanja akcije (0.1 do 1.0)
        self.x_direction = x_direction # -1 (lijevo), 0 (stoji), 1 (desno)

    def clone(self):
        return AIAction(self.is_jump, self.hold_time, self.x_direction)

    def mutate(self):
        # Mutiraj vrijeme trajanja
        self.hold_time += random.uniform(-0.15, 0.15) # Manji raspon za finije podešavanje
        self.hold_time = max(0.1, min(self.hold_time, 1.0))

        # Mutiraj smjer kretanja s određenom vjerojatnošću
        if random.random() < 0.25: # 25% šanse za promjenu smjera
            # Daj veći prioritet kretanju udesno pri mutaciji
            self.x_direction = random.choice([-1, 0, 1, 1, 1, 1]) # Veća šansa za 1 (desno)
        
        # Mutiraj skok s manjom vjerojatnošću
        if random.random() < 0.15: # 15% šanse za promjenu odluke o skoku
            self.is_jump = not self.is_jump

class Brain:
    JUMP_CHANCE = 0.35 # Malo veća šansa za inicijalni skok

    def __init__(self, instruction_size, randomize_instructions=True):
        self.instructions = []
        self.current_instruction_number = 0
        self.fitness = 0.0

        if randomize_instructions:
            self.randomize(instruction_size)

    def _get_random_action(self):
        is_jump = random.random() < self.JUMP_CHANCE
        hold_time = random.uniform(0.1, 0.8) # Preferiraj kraće do srednje držanje akcija
        
        # Inicijalno snažno favoriziraj kretanje udesno
        x_direction = random.choices([-1, 0, 1], weights=[5, 15, 80], k=1)[0] # 80% šansa za desno, 15% za stajanje, 5% za lijevo
        
        return AIAction(is_jump, hold_time, x_direction)

    def randomize(self, size):
        self.instructions = [self._get_random_action() for _ in range(size)]

    def get_next_action(self):
        if self.current_instruction_number >= len(self.instructions):
            return None
        action = self.instructions[self.current_instruction_number]
        self.current_instruction_number += 1
        return action

    def reset_instructions(self):
        self.current_instruction_number = 0
        # Fitness se postavlja na kraju simulacije, ne treba ga ovdje resetirati na 0 ako se koristi za praćenje najboljeg
        # self.fitness = 0.0 

    def clone(self):
        clone = Brain(len(self.instructions), randomize_instructions=False)
        clone.instructions = [instr.clone() for instr in self.instructions]
        return clone

    def mutate(self, mutation_rate, chance_of_new_instruction):
        for i in range(len(self.instructions)):
            if random.random() < chance_of_new_instruction:
                self.instructions[i] = self._get_random_action()
            elif random.random() < mutation_rate:
                self.instructions[i].mutate()

    def increase_moves(self, num_additional_moves):
        for _ in range(num_additional_moves):
            self.instructions.append(self._get_random_action())