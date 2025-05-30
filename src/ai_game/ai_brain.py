import random

class AIAction:
    def __init__(self, is_jump, hold_time, x_direction):
        self.is_jump = is_jump
        self.hold_time = hold_time # Vrijeme trajanja akcije
        self.x_direction = x_direction # Smjer kretanja (-1 lijevo, 0 stoji, 1 desno)

    def clone(self):
        return AIAction(self.is_jump, self.hold_time, self.x_direction)

    def mutate(self):
        # Blago mijenja vrijeme trajanja akcije
        self.hold_time += random.uniform(-0.15, 0.15)
        self.hold_time = max(0.1, min(self.hold_time, 1.0)) # Osigurava da je vrijeme unutar granica
        # Postoji šansa da se promijeni smjer kretanja
        if random.random() < 0.25:
            self.x_direction = random.choice([-1, 0, 1, 1, 1, 1]) # Veća vjerojatnost kretanja udesno
        # Postoji manja šansa da se promijeni odluka o skoku
        if random.random() < 0.15:
            self.is_jump = not self.is_jump

class Brain:
    JUMP_CHANCE = 0.35 # Vjerojatnost da će nasumična akcija biti skok

    def __init__(self, instruction_size, randomize_instructions=True):
        self.instructions = [] # Lista AI akcija (poteza)
        self.current_instruction_number = 0
        self.fitness = 0.0 # Ocjena uspješnosti mozga
        if randomize_instructions:
            self.randomize(instruction_size)

    def _get_random_action(self):
        is_jump = random.random() < self.JUMP_CHANCE
        hold_time = random.uniform(0.1, 0.8)
        x_direction = random.choices([-1, 0, 1], weights=[5, 15, 80], k=1)[0] # Ponderirani izbor smjera, preferira desno
        return AIAction(is_jump, hold_time, x_direction)

    def randomize(self, size):
        self.instructions = [self._get_random_action() for _ in range(size)]

    def get_next_action(self):
        if self.current_instruction_number >= len(self.instructions):
            return None # Nema više instrukcija
        action = self.instructions[self.current_instruction_number]
        self.current_instruction_number += 1
        return action

    def reset_instructions(self):
        self.current_instruction_number = 0 # Vraća brojač instrukcija na početak

    def clone(self):
        clone = Brain(len(self.instructions), randomize_instructions=False)
        clone.instructions = [instr.clone() for instr in self.instructions]
        return clone

    def mutate(self, mutation_rate, chance_of_new_instruction):
        for i in range(len(self.instructions)):
            # Šansa da se postojeća instrukcija zamijeni potpuno novom
            if random.random() < chance_of_new_instruction:
                self.instructions[i] = self._get_random_action()
            # Šansa da se postojeća instrukcija mutira
            elif random.random() < mutation_rate:
                self.instructions[i].mutate()

    def increase_moves(self, num_additional_moves):
        # Dodaje nove nasumične poteze na kraj postojećih
        for _ in range(num_additional_moves):
            self.instructions.append(self._get_random_action())

    def set_instructions(self, instructions_list):
        """Postavlja listu instrukcija."""
        self.instructions = instructions_list
        self.current_instruction_number = 0