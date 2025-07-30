from anytree import Node, RenderTree
from .grammer_rules import get_grammer
from dataclasses import dataclass
from tqdm.auto import tqdm
import traceback

import hashlib
import os
import json
import random
import subprocess

DEBUG = False
DEBUG_ERRORS = True

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Program:
    script: str
    output: str
    level: str
    hash: str
    initialized_variables: dict = None
    used_variables: set = None

    def to_dict(self):
        return {
            'script': self.script,
            'output': self.output,
            'level': self.level,
            'hash': self.hash,
            'initialized_variables': self.initialized_variables if self.initialized_variables else {},
            'used_variables': list(self.used_variables) if self.used_variables else []
        }
    
    def __str__(self):
        return f"Script: {self.script}\nOutput: {self.output}\nHash: {self.hash}"


class CodeGenerator:
    def __init__(self, max_initialized_vars=3):
        self.max_initialized_vars = max_initialized_vars
        self.var_count = 0
        self.grammer = get_grammer()
    
    def get_new_variable(self, current_variables):
        if self.var_count < self.max_initialized_vars:
            var_name = random.choice(self.grammer['VARIABLE'])
            while var_name in current_variables:
                var_name = random.choice(self.grammer['VARIABLE'])
            self.var_count += 1
            return var_name
        else:
            return None
        
    def get_loop_var(self) -> str:
        choices = ['i', 'j', 'k']
        choice = random.choice(choices)
        return choice
    def generate_sensical_loop_range(self):
        start = random.randint(1, 10)
        end = random.randint(start - 10, start + 10)
        if start == end: 
            end += 1 if random.choice([True, False]) else -1
        step = random.choice([1, 2, 3])
        if start > end:
            relational_operator = random.choice(['>', '>='])
            if step > 1:
                operator_step = f'-={step}'
            else:
                operator_step = '--'
        else:
            relational_operator = random.choice(['<', '<='])
            if step > 1:
                operator_step = f'+={step}'
            else:
                operator_step = '++'
        return str(start), str(end), relational_operator, operator_step

    def generate_code(self, symbol, current_variables, used_variables: set, parent=None, recursive=True):
        node = Node(symbol, parent=parent)
        if symbol in self.grammer:
            if symbol == 'IDENTIFIER_INITIALIZATION':
                if self.var_count < self.max_initialized_vars:
                    self.var_count += 1
                else:
                    symbol = 'INITIALIZATION'

            rule = random.choice(self.grammer[symbol])
            symbols = rule.split()
            
            if not recursive:
                generated_symbols = [s for s in symbols if s not in ['NEW_LINE', 'SPACE', 'TAB']]
                return ''.join(generated_symbols)
            
            generated_symbols = [self.generate_code(s, current_variables, used_variables, node) for s in symbols]
                        
            if symbol == 'INITIALIZATION':
                var_name = generated_symbols[3]
                variable_val = generated_symbols[7] # Check grammer rules for a sanity check
                current_variables[var_name] = variable_val
            
            if symbol == 'FOR_SIMPLE':
                f_start, f_end, f_operator, f_step = self.generate_sensical_loop_range()
                loop_var_name = self.get_loop_var()
                generated_symbols = [s
                    .replace('FIXED_VAR', loop_var_name)
                    .replace('FIXED_DIGIT_1', f_start, 1)
                    .replace('FIXED_DIGIT_2', f_end, 1)
                    .replace('FIXED_DIGIT_3', f_step, 1)
                    .replace('FIXED_RELATIONAL_OPERATOR', f_operator, 1)
                    for s in generated_symbols]
            
            if symbol == 'WHILE_SIMPLE':
                loop_var_name = self.get_loop_var()
                f_start, f_end, f_operator, f_step = self.generate_sensical_loop_range()
                while_end = f'NEW_LINE {loop_var_name} {f_step}'
                fixed_loop_assignment = f'NEW_LINE {loop_var_name} = {f_start}'
                generated_symbols = [s
                    .replace('FIXED_LOOP_ASSIGNMENT', fixed_loop_assignment, 1)
                    .replace('FIXED_VAR', loop_var_name)
                    .replace('FIXED_RELATIONAL_OPERATOR', f_operator, 1)
                    .replace('FIXED_DIGIT', f_end, 1)
                    .replace('WHILE_END', while_end, 1)
                    for s in generated_symbols]
            
            if symbol == 'ASSIGNMENT_SIMPLE' or symbol == 'ASSIGNMENT_COMPLEX':
                if len(generated_symbols) >= 4:
                    selected_var = generated_symbols[1]
                    selected_var_value = generated_symbols[5]
                    if selected_var in ['var', 'let']:
                        selected_var = generated_symbols[3]
                        selected_var_value = generated_symbols[7]
                    used_variables.add(selected_var)
                    current_variables[selected_var] = selected_var_value \
                        .replace('SPACE', ' ').replace('NEW_LINE', '\n').replace('TAB', '\t')
            
            return ''.join(generated_symbols)
        
        if symbol == 'EXPRESSION_IDENTIFIER':
            identifier = random.choice(
                tuple(current_variables.keys()) if current_variables 
                else random.choice(self.grammer['DIGIT'])
            )
            return identifier    
    
        elif symbol == 'DISPLAY_IDENTIFIER':
            try:
                return tuple(used_variables)[0]
            except:
                return random.choice(tuple(current_variables.keys()))
        
        else: return symbol;
    
    def print_tree(self, root):
        for pre, _, node in RenderTree(root):
            print(f"{pre}{node.name}")
    
    def generate_program(self, level):
        current_variables = {}
        used_variables = set()
        root = Node("PROGRAM")
        
        match level:
            case '1.1':
                self.max_initialized_vars = 2
            case '1.2':
                self.max_initialized_vars = 3
            case '2.1':
                self.max_initialized_vars = 2
            case '3.1':
                self.max_initialized_vars = 2
            case '3.2':
                self.max_initialized_vars = 4
            case '4.1':
                self.max_initialized_vars = 2
            case 'ALL':
                self.max_initialized_vars = 5
        
        if level == 'ALL': level_passed = random.choice(self.grammer['ALL'])
        elif level in ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1']: level_passed = f'LEVEL_{level}'
        else: level_passed = level
        
        program = self.generate_code(level_passed, current_variables, used_variables, root)
        
        program = program \
            .replace('SPACE', ' ') \
            .replace('NEW_LINE', '\n') \
            .replace('TAB', '\t')\
            .lstrip()
        return root, program, current_variables, used_variables, level_passed
    
    def generate_and_write_program(self, num_programs, level, deduplicate=True):
        output_dict = [] # Hash, script, output
        generated_programs = 0
        hashes = set()
        
        max_tries = 1000
        num_tries = 0
        
        pbar = tqdm(total=num_programs, desc="Generating Programs", unit="program")
        
        while generated_programs < num_programs:
            try:
                root, script, initialized_variables, used_variables, level = self.generate_program(level)
                if DEBUG:
                    self.print_tree(root)
                program_hash = hashlib.sha256(script.encode('utf-8')).hexdigest()

                program = Program(script=script, output='', hash=program_hash, level=level, initialized_variables=initialized_variables, used_variables=used_variables)
                
                if deduplicate:
                    if program_hash not in hashes:
                        hashes.add(program_hash)
                        output_dict.append(program.to_dict())
                        generated_programs += 1
                        pbar.update(1)
                        num_tries = 0
                    else:
                        num_tries += 1
                        if num_tries >= max_tries:
                            print(f"Max tries reached: {max_tries}. Stopping generation.")
                            break
            except Exception as e:
                if DEBUG_ERRORS:
                    print(f"Error generating program: {e}")
                    traceback.print_exc()
                continue
    
        return output_dict
                    
def create_program(level, count, annotated = False):
    generator = CodeGenerator()
    output = generator.generate_and_write_program(count, level, deduplicate=True)
    if annotated:
        return annotate_program(output, level)
    return output

def annotate_program(input_dict, level='ALL'):
    # Check if nodejs is in environment
    if 'nodejs' not in os.environ.get('PATH', ''):
        raise EnvironmentError("Node.js is not installed or not in PATH.")
    # Save input into temporary json file
    try: os.mkdir('temp')
    except: pass
    temp_input_file = os.path.abspath(os.path.join('temp', 'temp_input.json'))
    with open(temp_input_file, 'w') as f:
        json.dump(input_dict, f, indent=4)
    # Run the nodejs script to annotate the program
    required_amount = len(input_dict)
    output_list = []
    subprocess.run(['npm', 'run', 'annotate', temp_input_file], check=True, cwd=PACKAGE_DIR)
    # Read temporary output file
    temp_output_file = os.path.abspath(os.path.join('temp', 'temp_output.json'))
    with open(temp_output_file, 'r') as f:
        output_dict = json.load(f)
    # Check if its the same length, otherwise create more programs
    if len(output_dict) < required_amount:
        additional_output = create_program(level, required_amount - len(output_dict), annotated=True)
        output_dict.extend(additional_output)
    # Remove temp files
    if os.path.exists(temp_input_file):
        os.remove(temp_input_file)
    if os.path.exists(temp_output_file):
        os.remove(temp_output_file)
    return output_dict
    

def main():
    output_file = os.path.join('output', 'programs.json')
    
    if not os.path.exists('output'):
        os.makedirs('output')
    
    output = create_program('ALL', 10000, annotated=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Output saved to {output_file}")
    
if __name__ == "__main__":
    main()