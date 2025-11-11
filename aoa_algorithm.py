import random
import math
from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load', 'ram_mb'])

# --- Algoritma Archimedes Optimization Algorithm (AOA) ---

def calculate_estimated_makespan(solution: dict, tasks_dict: dict, vms_dict: dict) -> float:
    """
    Fungsi Biaya (Cost Function).
    Memperkirakan makespan (waktu selesai maks) untuk solusi tertentu.
    Model sederhana: makespan = max(total_beban_cpu_vm / core_vm)
    """
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}
    
    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        
        # Estimasi waktu eksekusi: beban / jumlah core
        # Ini model yang sangat sederhana, tapi umum digunakan
        estimated_time = task.cpu_load / vm.cpu_cores
        vm_loads[vm_name] += estimated_time
        
    # Makespan adalah VM yang paling lama selesai
    return max(vm_loads.values())

def solution_to_vector(solution: dict, vm_names: list) -> list:
    """Konversi solusi dictionary ke vector numerik."""
    vm_to_idx = {vm: idx for idx, vm in enumerate(vm_names)}
    return [vm_to_idx[solution[task_id]] for task_id in sorted(solution.keys())]

def vector_to_solution(vector: list, task_ids: list, vm_names: list) -> dict:
    """Konversi vector numerik ke solusi dictionary."""
    solution = {}
    for i, task_id in enumerate(task_ids):
        vm_idx = int(round(vector[i])) % len(vm_names)
        solution[task_id] = vm_names[vm_idx]
    return solution

def archimedes_optimization(tasks: list[Task], vms: list[VM], iterations: int, pop_size: int = 30) -> dict:
    """
    Menjalankan Archimedes Optimization Algorithm (AOA) untuk menemukan solusi terbaik.
    
    Parameters:
    - tasks: Daftar tugas yang akan dijadwalkan
    - vms: Daftar VM yang tersedia
    - iterations: Jumlah iterasi maksimal
    - pop_size: Ukuran populasi
    """
    
    print(f"Memulai Archimedes Optimization Algorithm ({iterations} iterasi, populasi {pop_size})...")
    
    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}
    vm_names = list(vms_dict.keys())
    task_ids = sorted([task.id for task in tasks])
    
    num_tasks = len(tasks)
    num_vms = len(vm_names)
    
    # Inisialisasi populasi
    population = []
    fitness = []
    
    for _ in range(pop_size):
        # Buat solusi acak
        solution = {task_id: random.choice(vm_names) for task_id in task_ids}
        vector = solution_to_vector(solution, vm_names)
        population.append(vector)
        fitness.append(calculate_estimated_makespan(solution, tasks_dict, vms_dict))
    
    # Temukan solusi terbaik awal
    best_idx = fitness.index(min(fitness))
    best_solution_vector = population[best_idx].copy()
    best_fitness = fitness[best_idx]
    
    print(f"Estimasi Makespan Awal: {best_fitness:.2f}")
    
    # Parameter AOA
    C1 = 2  # Konstanta eksplorasi
    C2 = 6  # Konstanta akselerasi
    C3 = 2  # Konstanta transfer
    C4 = 0.5  # Konstanta densitas
    
    # Iterasi utama
    for t in range(iterations):
        # Update parameter yang menurun secara linear
        T_F = math.exp(-t / iterations)  # Transfer flow
        
        # Hitung densitas dan volume untuk setiap objek
        densities = []
        volumes = []
        
        for i in range(pop_size):
            # Densitas berdasarkan fitness (objek lebih baik = lebih padat)
            if fitness[i] > 0:
                density = 1.0 / (fitness[i] + 1e-10)
            else:
                density = 1.0
            densities.append(density)
            
            # Volume (normalisasi berdasarkan posisi)
            volume = sum(population[i]) / (num_tasks * num_vms)
            volumes.append(volume)
        
        # Update setiap objek dalam populasi
        for i in range(pop_size):
            # Pilih objek lain secara acak
            j = random.randint(0, pop_size - 1)
            while j == i:
                j = random.randint(0, pop_size - 1)
            
            # Hitung akselerasi berdasarkan prinsip Archimedes
            # acc = density_diff * volume_diff / mass
            density_diff = densities[j] - densities[i]
            volume_diff = volumes[j] - volumes[i]
            
            # Update posisi berdasarkan kondisi
            new_vector = population[i].copy()
            
            for d in range(num_tasks):
                if t < iterations / 2:
                    # Fase eksplorasi
                    if density_diff > 0:
                        # Objek i naik ke permukaan
                        rand_val = random.uniform(0, 1)
                        new_vector[d] = population[j][d] + C1 * rand_val * density_diff * \
                                      (population[j][d] - population[i][d])
                    else:
                        # Objek i tenggelam
                        rand_val = random.uniform(0, 1)
                        new_vector[d] = population[j][d] - C1 * rand_val * abs(density_diff) * \
                                      (population[j][d] - population[i][d])
                else:
                    # Fase eksploitasi
                    if random.random() < 0.5:
                        new_vector[d] = best_solution_vector[d] + C2 * random.uniform(-1, 1) * T_F * \
                                      (best_solution_vector[d] - population[i][d])
                    else:
                        new_vector[d] = best_solution_vector[d] + C3 * random.uniform(-1, 1) * T_F * \
                                      (random.uniform(0, num_vms - 1) - population[i][d])
                
                # Batasi nilai dalam rentang valid
                new_vector[d] = max(0, min(num_vms - 1, new_vector[d]))
            
            # Evaluasi solusi baru
            new_solution = vector_to_solution(new_vector, task_ids, vm_names)
            new_fitness = calculate_estimated_makespan(new_solution, tasks_dict, vms_dict)
            
            # Greedy selection
            if new_fitness < fitness[i]:
                population[i] = new_vector
                fitness[i] = new_fitness
                
                # Update solusi terbaik global
                if new_fitness < best_fitness:
                    best_fitness = new_fitness
                    best_solution_vector = new_vector.copy()
                    print(f"Iterasi {t}: Estimasi Makespan Baru: {best_fitness:.2f}")
    
    # Konversi solusi terbaik ke format dictionary
    final_solution = vector_to_solution(best_solution_vector, task_ids, vm_names)
    
    print(f"AOA Selesai. Estimasi Makespan Terbaik: {best_fitness:.2f}")
    return final_solution