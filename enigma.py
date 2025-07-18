import json
import sys

class JSONFileError(Exception):
    pass

class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.initial_wheels = wheels[:]
        self.wheels = wheels[:]
        self.reflector_map = reflector_map

    def _advance_wheels(self, encrypted_count):
        # Rotate W1
        self.wheels[0] = (self.wheels[0] % 8) + 1
        
        # Update W2 based on the count of encrypted characters
        if encrypted_count % 2 == 0:
            self.wheels[1] *= 2
        else:
            self.wheels[1] -= 1
        
        # Update W3 based on the count of encrypted characters
        if encrypted_count % 10 == 0:
            self.wheels[2] = 10
        elif encrypted_count % 3 == 0:
            self.wheels[2] = 5
        else:
            self.wheels[2] = 0

    def encrypt(self, message):
        encrypted_message = []
        encrypted_count = 0
        
        for char in message:
            if char.islower():
                i = self.hash_map[char]
                
                # Step 2
                shift_value = (2 * self.wheels[0] - self.wheels[1] + self.wheels[2]) % 26
                if shift_value != 0:
                    i += shift_value
                else:
                    i += 1
                
                i %= 26
                
                # Step 4: Find corresponding character
                c1 = next(key for key, value in self.hash_map.items() if value == i)
                
                # Step 5: Reflect
                c2 = self.reflector_map[c1]
                
                # Step 6: Get new index from hash_map
                i = self.hash_map[c2]
                
                # Step 7: Subtract the shift value
                if shift_value != 0:
                    i -= shift_value
                else:
                    i -= 1
                
                i %= 26
                
                # Step 9: Find final character
                c3 = next(key for key, value in self.hash_map.items() if value == i)
                
                encrypted_message.append(c3)
                encrypted_count += 1
            else:
                encrypted_message.append(char)
            
            # Advance wheels based on encrypted characters count
            self._advance_wheels(encrypted_count)
        
        # Reset wheels to initial state after encryption
        self.wheels = self.initial_wheels[:]
        
        return ''.join(encrypted_message)

def load_enigma_from_path(path):
    try:
        with open(path, 'r') as file:
            config = json.load(file)
            enigma = Enigma(
                hash_map=config["hash_map"],
                wheels=config["wheels"],
                reflector_map=config["reflector_map"]
            )
            return enigma
    except Exception as e:
        raise JSONFileError(f"Error loading Enigma configuration: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) not in [5, 7]:
        print("Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>")
        sys.exit(1)
    
    try:
        config_file = None
        input_file = None
        output_file = None

        for i in range(1, len(sys.argv), 2):
            if sys.argv[i] == '-c':
                config_file = sys.argv[i + 1]
            elif sys.argv[i] == '-i':
                input_file = sys.argv[i + 1]
            elif sys.argv[i] == '-o':
                output_file = sys.argv[i + 1]

        if not config_file or not input_file:
            print("Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>")
            sys.exit(1)

        enigma = load_enigma_from_path(config_file)

        with open(input_file, 'r') as infile:
            messages = infile.readlines()
        
        encrypted_messages = []
        for message in messages:
            encrypted_messages.append(enigma.encrypt(message.rstrip('\n')))
            # Preserve empty lines in the output
            if message.rstrip('\n') == "":
                encrypted_messages[-1] = ""

        if output_file:
            with open(output_file, 'w') as outfile:
                outfile.write('\n'.join(encrypted_messages) + '\n')
        else:
            for message in encrypted_messages:
                print(message)

    except Exception as e:
        print("The enigma script has encountered an error")
        sys.exit(1)
