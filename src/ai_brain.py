import random

# Preuzeto iz Brain.js i prilagođeno za Python
class AIAction:
    def __init__(self, is_jump, hold_time, x_direction):
        self.is_jump = is_jump  # boolean: treba li skočiti
        self.hold_time = hold_time  # float (0.1 do 1.0): koliko dugo držati akciju (proporcionalno)
        self.x_direction = x_direction  # int: -1 (lijevo), 0 (stoji), 1 (desno)

    def clone(self):
        return AIAction(self.is_jump, self.hold_time, self.x_direction)

    def mutate(self):
        # Mutiraj vrijeme držanja
        self.hold_time += random.uniform(-0.3, 0.3)
        self.hold_time = max(0.1, min(self.hold_time, 1.0)) # Ograniči između 0.1 i 1.0

        # Dodatna mala šansa za promjenu smjera ili skoka
        if random.random() < 0.1: # 10% šansa za promjenu smjera
            directions = [-1, 0, 1]
            self.x_direction = random.choice(directions)
        if random.random() < 0.05: # 5% šansa za promjenu odluke o skoku
            self.is_jump = not self.is_jump


class Brain:
    # Konstante za generiranje nasumične akcije - preuzeto iz Brain.js
    JUMP_CHANCE = 0.5  # Šansa da nasumična akcija bude skok (u Brain.js je random() > jumpChance, što znači (1-jumpChance))
                      # Ovdje ćemo koristiti kao direktnu šansu.
    CHANCE_OF_FULL_JUMP_HOLD = 0.2 # U Brain.js je ovo bilo za holdTime, ovdje nije direktno primjenjivo na isti način.
                                 # Ostavljamo logiku holdTime mutacije kao glavnu.

    def __init__(self, instruction_size, randomize_instructions=True):
        self.instructions = []
        self.current_instruction_number = 0
        self.fitness = 0.0
        # parentReachedBestLevelAtActionNo iz Brain.js nije direktno korišteno u ovoj osnovnoj verziji
        # za jednostavnost, mutacija će djelovati na sve instrukcije ili nasumično odabrane.

        if randomize_instructions:
            self.randomize(instruction_size)

    def _get_random_action(self):
        is_jump = False
        if random.random() < self.JUMP_CHANCE:
            is_jump = True

        hold_time = random.uniform(0.1, 1.0)
        # if random.random() < self.CHANCE_OF_FULL_JUMP_HOLD: # Originalna Brain.js logika
        #     hold_time = 1.0

        directions = [-1, -1, 0, 1, 1] # Favorizira kretanje
        x_direction = random.choice(directions)

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
        self.fitness = 0.0

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