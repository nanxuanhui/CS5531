import heapq
import random
from collections import deque
import csv

# Define the Process class
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=5):
        self.pid = pid  # Process ID
        self.arrival_time = arrival_time  # Arrival time
        self.burst_time = burst_time  # Burst time
        self.remaining_time = burst_time  # Remaining execution time
        self.priority = priority  # Priority (the smaller the value, the higher the priority)
        self.waiting_time = 0  # Waiting time
        self.turnaround_time = 0  # Turnaround time
        self.completed = False  # Whether completed
        self.response_ratio = 0  # Response ratio (for HRRN)
        self.last_executed_time = arrival_time  # Last executed time (for RR)

    def __lt__(self, other):
        # Required for heap comparison, used in priority scheduling and SRTF
        return self.priority < other.priority

# Generate 30 processes
def generate_processes():
    processes = []
    for i in range(1, 31):
        arrival_time = i - 1  # Each process arrives 1 time unit apart
        burst_time = random.randint(2, 8)  # Burst time between 2 and 8
        priority = random.randint(1, 5)  # Priority between 1 and 5
        process = Process(pid=f'P{i}', arrival_time=arrival_time, burst_time=burst_time, priority=priority)
        processes.append(process)
    return processes

# Add emergency process P31
def add_emergency_process(processes):
    emergency_process = Process(pid='P31', arrival_time=15, burst_time=2, priority=1)
    processes.append(emergency_process)

# Print process information
def print_processes(processes):
    print("Generated 30 process information:")
    print(f"{'Process ID':<7} {'Arrival Time':<12} {'Burst Time':<10} {'Priority':<8}")
    for p in processes:
        print(f"{p.pid:<7}{p.arrival_time:<12}{p.burst_time:<10}{p.priority:<8}")
    print()

# Save process information to a file
def save_processes_to_file(processes, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Process ID', 'Arrival Time', 'Burst Time', 'Priority'])
        # Write process information
        for p in processes:
            writer.writerow([p.pid, p.arrival_time, p.burst_time, p.priority])
    print(f"Process information has been saved to file '{filename}'.")

# First Come First Serve (FCFS)
def fcfs(processes):
    print("FCFS scheduling process:")
    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    queue = []
    completed_processes = []
    process_log = []

    while processes or queue:
        # Add arrived processes to the queue
        while processes and processes[0].arrival_time <= time:
            queue.append(processes.pop(0))
        if queue:
            current_process = queue.pop(0)
            if time < current_process.arrival_time:
                time = current_process.arrival_time
            current_process.waiting_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} starts execution")
            time += current_process.burst_time
            current_process.turnaround_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} finishes execution")
            completed_processes.append(current_process)
            process_log.append((current_process.pid, current_process.arrival_time, current_process.burst_time))
        else:
            time += 1

    return completed_processes

# Longest Job First (LJF)
def ljf(processes):
    print("LJF scheduling process:")
    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    queue = []
    completed_processes = []
    process_log = []

    while processes or queue:
        # Add arrived processes to the queue
        while processes and processes[0].arrival_time <= time:
            # Use negative values to sort from largest to smallest
            heapq.heappush(queue, (-processes[0].burst_time, processes.pop(0)))
        if queue:
            _, current_process = heapq.heappop(queue)
            if time < current_process.arrival_time:
                time = current_process.arrival_time
            current_process.waiting_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} starts execution")
            time += current_process.burst_time
            current_process.turnaround_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} finishes execution")
            completed_processes.append(current_process)
            process_log.append((current_process.pid, current_process.arrival_time, current_process.burst_time))
        else:
            time += 1

    return completed_processes

# Round Robin (RR)
def rr(processes, time_quantum=4):
    print("RR scheduling process:")
    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    queue = deque()
    completed_processes = []

    while processes or queue:
        # Add arrived processes to the queue
        while processes and processes[0].arrival_time <= time:
            queue.append(processes.pop(0))
        if queue:
            current_process = queue.popleft()
            if current_process.last_executed_time == current_process.arrival_time:
                current_process.waiting_time += time - current_process.arrival_time
            else:
                current_process.waiting_time += time - current_process.last_executed_time
            exec_time = min(time_quantum, current_process.remaining_time)
            print(f"Time {time}: Process {current_process.pid} executes for {exec_time} time units")
            time += exec_time
            current_process.remaining_time -= exec_time
            current_process.last_executed_time = time
            # Check if new processes have arrived during execution
            while processes and processes[0].arrival_time <= time:
                queue.append(processes.pop(0))
            if current_process.remaining_time > 0:
                queue.append(current_process)
            else:
                current_process.turnaround_time = time - current_process.arrival_time
                print(f"Time {time}: Process {current_process.pid} finishes execution")
                completed_processes.append(current_process)
        else:
            time += 1

    return completed_processes

# Longest Remaining Time First (LRTF) Non-preemptive
def lrtf(processes):
    print("LRTF scheduling process (non-preemptive):")
    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    completed_processes = []
    queue = []

    while processes or queue:
        # Add arrived processes to the ready queue
        while processes and processes[0].arrival_time <= time:
            process = processes.pop(0)
            heapq.heappush(queue, (-process.burst_time, process))

        if queue:
            # Select the process with the longest burst time
            _, current_process = heapq.heappop(queue)
            if time < current_process.arrival_time:
                time = current_process.arrival_time
            current_process.waiting_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} starts execution")
            time += current_process.burst_time
            current_process.turnaround_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} finishes execution")
            completed_processes.append(current_process)
        else:
            time += 1

    return completed_processes

# Highest Response Ratio Next (HRRN)
def hrrn(processes):
    print("HRRN scheduling process:")
    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    queue = []
    completed_processes = []

    while processes or queue:
        # Add arrived processes to the queue
        while processes and processes[0].arrival_time <= time:
            queue.append(processes.pop(0))
        if queue:
            # Calculate response ratio
            for p in queue:
                waiting_time = time - p.arrival_time
                p.response_ratio = (waiting_time + p.burst_time) / p.burst_time
            # Select the process with the highest response ratio
            queue.sort(key=lambda p: p.response_ratio, reverse=True)
            current_process = queue.pop(0)
            current_process.waiting_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} starts execution")
            time += current_process.burst_time
            current_process.turnaround_time = time - current_process.arrival_time
            print(f"Time {time}: Process {current_process.pid} finishes execution")
            completed_processes.append(current_process)
        else:
            time += 1

    return completed_processes

# Calculate average waiting time and average turnaround time
def calculate_avg_times(completed_processes):
    total_waiting_time = sum(p.waiting_time for p in completed_processes)
    total_turnaround_time = sum(p.turnaround_time for p in completed_processes)
    n = len(completed_processes)
    avg_waiting_time = total_waiting_time / n
    avg_turnaround_time = total_turnaround_time / n
    return avg_waiting_time, avg_turnaround_time

# Main function
def main():
    # Generate processes
    processes = generate_processes()
    add_emergency_process(processes)
    # Print the 30 processes generated
    print_processes(processes)
    # Save process information to a file
    save_processes_to_file(processes, 'processes.csv')

    # Prepare to save summary information
    summary = []

    # FCFS scheduling
    fcfs_processes = fcfs(processes.copy())
    avg_waiting_time, avg_turnaround_time = calculate_avg_times(fcfs_processes)
    print(f"\nFCFS average waiting time: {avg_waiting_time:.2f}")
    print(f"FCFS average turnaround time: {avg_turnaround_time:.2f}")
    summary.append(f"FCFS average waiting time: {avg_waiting_time:.2f}\nFCFS average turnaround time: {avg_turnaround_time:.2f}\n")

    # LJF scheduling
    print()
    ljf_processes = ljf(processes.copy())
    avg_waiting_time, avg_turnaround_time = calculate_avg_times(ljf_processes)
    print(f"\nLJF average waiting time: {avg_waiting_time:.2f}")
    print(f"LJF average turnaround time: {avg_turnaround_time:.2f}")
    summary.append(f"LJF average waiting time: {avg_waiting_time:.2f}\nLJF average turnaround time: {avg_turnaround_time:.2f}\n")

    # RR scheduling
    print()
    rr_processes = rr(processes.copy(), time_quantum=4)
    avg_waiting_time, avg_turnaround_time = calculate_avg_times(rr_processes)
    print(f"\nRR average waiting time: {avg_waiting_time:.2f}")
    print(f"RR average turnaround time: {avg_turnaround_time:.2f}")
    summary.append(f"RR average waiting time: {avg_waiting_time:.2f}\nRR average turnaround time: {avg_turnaround_time:.2f}\n")

    # HRRN scheduling
    print()
    hrrn_processes = hrrn(processes.copy())
    avg_waiting_time, avg_turnaround_time = calculate_avg_times(hrrn_processes)
    print(f"\nHRRN average waiting time: {avg_waiting_time:.2f}")
    print(f"HRRN average turnaround time: {avg_turnaround_time:.2f}")
    summary.append(f"HRRN average waiting time: {avg_waiting_time:.2f}\nHRRN average turnaround time: {avg_turnaround_time:.2f}\n")

    # LRTF scheduling
    print()
    lrtf_processes = lrtf(processes.copy())
    avg_waiting_time, avg_turnaround_time = calculate_avg_times(lrtf_processes)
    print(f"\nLRTF average waiting time: {avg_waiting_time:.2f}")
    print(f"LRTF average turnaround time: {avg_turnaround_time:.2f}")
    summary.append(f"LRTF average waiting time: {avg_waiting_time:.2f}\nLRTF average turnaround time: {avg_turnaround_time:.2f}\n")

    # Save summary information to a file
    with open('summary.txt', 'w', encoding='utf-8') as f:
        f.write("Scheduling algorithm performance summary:\n\n")
        f.writelines(summary)
    print("Summary information has been saved to file 'summary.txt'.")

if __name__ == "__main__":
    main()
