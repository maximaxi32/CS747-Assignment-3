#!/bin/bash

# Number of parallel processes
num_processes=5

# Output directory
output_dir="output"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Function to execute the Python command with a random seed and write the "Marks" line to a file
execute_python_command() {
    
    output_file="results4.txt"
    python_command="python main.py --level-all --seed $1 --no-render"
    result=$($python_command | grep "Marks :")
    echo "$1 $result" >> "$output_file"
}

for ((i = 1; i <= 10; i++)); do
    random_number=$(python -c "import random; print(random.randint(1, 100000))")
    execute_python_command $random_number  &
    if ((i % num_processes == 0)); then
        # Wait for a batch of processes to complete
        wait
    fi
done
