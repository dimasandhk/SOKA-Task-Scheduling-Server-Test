import random
import math
from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load', 'ram_mb'])

# --- Fungsi Cost / Fitness ---
def calculate_estimated_makespan(solution: dict, tasks_dict: dict, vms_dict: dict) -> float:
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}
    
    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        
        # Gunakan 0 jika task tidak punya ram_mb
        ram_load = getattr(task, "ram_mb", 0)
        
        estimated_time = (task.cpu_load / vm.cpu_cores) + (ram_load / (vm.ram_gb * 1024))
        vm_loads[vm_name] += estimated_time
        
    return max(vm_loads.values())

# --- Konversi Representasi Solusi ---
def solution_to_vector(solution: dict, vm_names: list) -> list:
    vm_to_idx = {vm: idx for idx, vm in enumerate(vm_names)}
    return [vm_to_idx[solution[task_id]] for task_id in sorted(solution.keys())]

def vector_to_solution(vector: list, task_ids: list, vm_names: list) -> dict:
    solution = {}
    for i, task_id in enumerate(task_ids):
        vm_idx = int(round(vector[i])) % len(vm_names)
        solution[task_id] = vm_names[vm_idx]
    return solution


# --- Algoritma Archimedes Optimization ---
def archimedes_optimization(tasks: list[Task], vms: list[VM], iterations: int, pop_size: int = 30) -> dict:
    print(f"Menjalankan Archimedes Optimization Algorithm (AOA) dengan {iterations} iterasi dan populasi {pop_size}...")

    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}
    vm_names = list(vms_dict.keys())
    task_ids = sorted([task.id for task in tasks])
    num_tasks = len(tasks)
    num_vms = len(vm_names)

    # --- Inisialisasi populasi ---
    population = []
    fitness = []
    for _ in range(pop_size):
        solution = {task_id: random.choice(vm_names) for task_id in task_ids}
        vector = solution_to_vector(solution, vm_names)
        population.append(vector)
        fitness.append(calculate_estimated_makespan(solution, tasks_dict, vms_dict))

    best_idx = fitness.index(min(fitness))
    best_solution_vector = population[best_idx].copy()
    best_fitness = fitness[best_idx]
    print(f"  Makespan awal terbaik: {best_fitness:.4f}")

    # --- Parameter AOA ---
    C1, C2, C3, C4 = 2, 6, 2, 0.5

    for t in range(iterations):
        # Transfer function (T_F)
        T_F = math.exp(-t / iterations) * math.cos((math.pi * t) / (2 * iterations))

        # Normalisasi fitness untuk stabilitas
        f_min, f_max = min(fitness), max(fitness)
        norm_fit = [(f - f_min) / (f_max - f_min + 1e-10) for f in fitness]

        densities = [1.0 / (f + 1e-10) for f in norm_fit]
        volumes = [sum(vec) / (num_tasks * num_vms) for vec in population]

        for i in range(pop_size):
            j = random.randint(0, pop_size - 1)
            while j == i:
                j = random.randint(0, pop_size - 1)

            density_diff = densities[j] - densities[i]
            volume_diff = volumes[j] - volumes[i]

            acc = C4 * density_diff * volume_diff
            new_vector = population[i].copy()

            for d in range(num_tasks):
                r1, r2 = random.random(), random.uniform(-1, 1)

                if t < iterations / 2:  # Eksplorasi
                    new_vector[d] = population[i][d] + C1 * r1 * acc
                else:  # Eksploitasi
                    if random.random() < 0.5:
                        new_vector[d] = best_solution_vector[d] + C2 * r2 * T_F * \
                                        (best_solution_vector[d] - population[i][d])
                    else:
                        new_vector[d] = best_solution_vector[d] + C3 * r2 * T_F * \
                                        (random.uniform(0, num_vms - 1) - population[i][d])

                # Batasi dalam rentang valid
                new_vector[d] = max(0, min(num_vms - 1, new_vector[d]))

            # Evaluasi solusi baru
            new_solution = vector_to_solution(new_vector, task_ids, vm_names)
            new_fitness = calculate_estimated_makespan(new_solution, tasks_dict, vms_dict)

            # Seleksi greedy
            if new_fitness < fitness[i]:
                fitness[i] = new_fitness
                population[i] = new_vector

                if new_fitness < best_fitness:
                    best_fitness = new_fitness
                    best_solution_vector = new_vector.copy()
                    print(f"Iterasi {t+1}: Makespan baru = {best_fitness:.4f}")

    final_solution = vector_to_solution(best_solution_vector, task_ids, vm_names)
    print(f"AOA selesai ✅ | Makespan terbaik: {best_fitness:.4f}")
    return final_solution
