import os
import time
import threading
import time
from collections import defaultdict
import matplotlib.pyplot as plt
import csv
import readline

class DataCollector:
    def __init__(self):
        self.cpu_stats = {
            'user': [],
            'nice': [],
            'system': [],
            'idle': [],
            'iowait': [],
            'irq': [],
            'softirq': [],
            'steal': [],
            'guest': [],
            'guest_nice': []
        }
        self.vm_stats = defaultdict(list)
        self.collecting = False
        self.imported_files = []
        self.start_time = None

    def start_collecting(self):
        self.collecting = True
        self.start_time = time.time()
        thread = threading.Thread(target=self.collect_data)
        thread.start()

    def stop_collecting(self):
        self.collecting = False
        self.start_time = None

    def collect_data(self):
        while self.collecting:
            try:
                with open('/proc/stat', 'r') as file:
                    first_line = file.readline()
                    values = first_line.split()[1:]  # Ignore 'cpu'

                    self.cpu_stats['user'].append(int(values[0]))
                    self.cpu_stats['nice'].append(int(values[1]))
                    self.cpu_stats['system'].append(int(values[2]))
                    self.cpu_stats['idle'].append(int(values[3]))
                    self.cpu_stats['iowait'].append(int(values[4]))
                    self.cpu_stats['irq'].append(int(values[5]))
                    self.cpu_stats['softirq'].append(int(values[6]))
                    self.cpu_stats['steal'].append(int(values[7]))
                    self.cpu_stats['guest'].append(int(values[8]))
                    self.cpu_stats['guest_nice'].append(int(values[9]))

                with open('/proc/vmstat', 'r') as file:
                    for line in file:
                        key, value = line.split()
                        self.vm_stats[key].append(int(value))

                time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
                self.collecting = False

    def plot_data(self, item):
        try:
            category, key = item.split('.')
            if category == 'cpu':
                data = self.cpu_stats[key]
            elif category == 'vmstat':
                data = self.vm_stats[key]
            else:
                print(f"Unknown category: {category}")
                return
        except Exception as e:
            print(f"Error: {e}")
            return  
            
        timestamps = list(range(1, len(data) + 1))

        plt.figure()
        plt.plot(timestamps, data)
        plt.xlabel('Timestamp')
        plt.ylabel(key)
        plt.title(f'{category} {key} over time')
        plt.savefig(f'plot/{category}_{key}.png')

    def export_data(self, mode='abs', cpu_file='cpu_stats.csv', vm_file='vm_stats.csv'):
        if mode not in ['abs', 'diff']:
            print(f"Unknown mode: {mode}")
            return

        try:
            with open(f'data/{mode}_{cpu_file}', 'w') as file:
                writer = csv.writer(file)
                writer.writerow(['category', 'value'])
                for key, values in self.cpu_stats.items():
                    if mode == 'diff':
                        base_value = values[0]
                        values = [x - base_value for x in values]
                    for value in values:
                        writer.writerow([key, value])

            with open(f'data/{mode}_{vm_file}', 'w') as file:
                writer = csv.writer(file)
                writer.writerow(['category', 'value'])
                for key, values in self.vm_stats.items():
                    if mode == 'diff':
                        base_value = values[0]
                        values = [x - base_value for x in values]
                    for value in values:
                        writer.writerow([key, value])
        except Exception as e:
            print(f"Error: {e}")
            
    def import_data(self, cpu_file='cpu_stats.csv', vm_file='vm_stats.csv'):
        try:
            with open(f'data/{cpu_file}', 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    key, value = row
                    self.cpu_stats[key].append(int(value))

            with open(f'data/{vm_file}', 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    key, value = row
                    self.vm_stats[key].append(int(value))
            self.imported_files = [cpu_file, vm_file]   
            print(f"Data imported from {cpu_file} and {vm_file}") 
        except Exception as e:
            print(f"Error: {e}")

    def list_items(self, category):
        try:
            if category == 'cpu':
                for key in self.cpu_stats.keys():
                    print(key)
            elif category == 'vmstat':
                for key in self.vm_stats.keys():
                    print(key)
            else:
                print(f"Unknown category: {category}")
        except Exception as e:
            print(f"Error: {e}")

    def plot_diff_data(self, item):
        try:
            category, key = item.split('.')
            if category == 'cpu':
                data = self.cpu_stats[key]
            elif category == 'vmstat':
                data = self.vm_stats[key]
            else:
                print(f"Unknown category: {category}")
                return
        except Exception as e:
            print(f"Error: {e}")
            return  

        base_value = data[0]
        diff_data = [x - base_value for x in data]
        timestamps = list(range(1, len(diff_data) + 1))

        plt.figure()
        plt.plot(timestamps, diff_data)
        plt.xlabel('Timestamp')
        plt.ylabel(f'{key} (difference from first value)')
        plt.title(f'{category} {key} over time (difference from first value)')
        plt.savefig(f'plot/{category}_{key}_diff.png')

    def plot_two_data(self, file1, file2, item):
        try:
            category, key = item.split('.')
            with open(f'data/{file1}', 'r') as f1, open(f'data/{file2}', 'r') as f2:
                reader1 = csv.reader(f1)
                reader2 = csv.reader(f2)
                next(reader1)  # Skip header
                next(reader2)  # Skip header

                data1 = [int(row[1]) for row in reader1 if row[0] == key]
                data2 = [int(row[1]) for row in reader2 if row[0] == key]
        except Exception as e:
            print(f"Error: {e}")
            return  

        timestamps = list(range(1, max(len(data1), len(data2)) + 1))

        plt.figure()
        plt.plot(timestamps[:len(data1)], data1, label=file1)
        plt.plot(timestamps[:len(data2)], data2, label=file2)
        plt.xlabel('Timestamp')
        plt.ylabel(key)
        plt.title(f'{category} {key} over time')
        plt.legend()
        plt.savefig(f'plot/{category}_{key}_comparison.png')

def print_usage():
    print("Usage:")
    print(" *** Collecting ***")
    print("  s: Start collecting data")
    print("  e: End collecting data")
    print(" *** Plotting ***")
    print("  ls <category:cpu/vmstat>: List items in <category>")
    print("  p <item>: Plot data for <item>, <item> should be in the format <category>.<key> (e.g. cpu.user, vmstat.pgpgin)")
    print("  pd <item>: Plot data for <item> with values as difference from the first value")
    print(" *** Data management ***")
    print("  export [abs|diff] [file1 file2]: Export data to files (default: cpu_stats.csv, vm_stats.csv)")
    print("  import [file1 file2]: Import data from files (default: cpu_stats.csv, vm_stats.csv)")
    print(" *** Special plotting ***")
    print("  p2 <file1 file2> <item>: Plot data for <item> from <file1> and <file2>")
    print(" *** Others ***")
    print("  q: Quit the program")
    print("  h: Help message")

collector = DataCollector()

# Create directories if they don't exist
os.makedirs('plot', exist_ok=True)
os.makedirs('data', exist_ok=True)

def create_command_line_prompt(collector):
    prompt = ""
    if collector.imported_files:
        prompt += f"Data imported {collector.imported_files[0]}, {collector.imported_files[1]}"
    elif collector.start_time:
        prompt += "Collecting started at " + time.ctime(collector.start_time)
    else:
        prompt += "(h for help)" 
    return prompt

while True:
    cmd_line = create_command_line_prompt(collector) + " > "
    command = input(cmd_line).split()
    if not command:
        continue
    readline.add_history(' '.join(command))
                         
    if command[0] == 's':
        collector.start_collecting()
    elif command[0] == 'e':
        collector.stop_collecting()
    elif command[0] == 'ls':
        if len(command) < 2:
            print("Category not provided")
            continue    
        collector.list_items(command[1])
    elif command[0] == 'p':
        if len(command) < 2:
            print("Item not provided")
            continue    
        collector.plot_data(command[1])
    elif command[0] == 'pd':
        if len(command) < 2:
            print("Item not provided")
            continue    
        collector.plot_diff_data(command[1])
    elif command[0] == 'export':
        if len(command) < 2:
            print("Mode not provided")
            continue
        collector.export_data(*command[1:])
    elif command[0] == 'import':
        collector.import_data(*command[1:])
    elif command[0] == 'p2':
        collector.plot_two_data(command[1], command[2], command[3])
    elif command[0] == 'q':
        if collector.start_collecting:
            collector.stop_collecting()
        break
    elif command[0] == 'h':
        print_usage()
    else:
        print("Unknown command: " + command[0])
        print_usage()