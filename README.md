# Archimedes Optimization Algorithm (AOA) Scheduler

## Distributed Task Scheduling for Multi-VM Execution

Repository ini berisi implementasi penjadwalan tugas terdistribusi menggunakan Archimedes Optimization Algorithm (AOA). Algoritma ini digunakan untuk mengalokasikan task ke VM secara optimal berdasarkan kapasitas CPU dan RAM, dengan tujuan meminimalkan makespan, mengurangi bottleneck, dan meningkatkan utilisasi sumber daya.

Struktur repository telah dirancang modular, terdiri dari:

- `aoa_algorithm.py` → Implementasi algoritma AOA
- `scheduler.py` → Eksekusi scheduling + simulasi waktu
- `server/` → Task execution API (jika dijalankan secara distributed)
- `aoa_results.csv` → Hasil penjadwalan AOA
- `docker-compose.yml` → Menjalankan sistem secara terdistribusi

## Repository Structure

```
├── images/
├── server/
├── .env.example
├── .gitignore
├── .python-version
├── README.md
├── aoa_algorithm.py
├── aoa_results.csv
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── scheduler.py
├── shc_results.csv
└── uv.lock
```

## 1. Overview Sistem

Hasil akhir berupa file `aoa_results.csv` yang berisi jadwal lengkap dengan kolom:

- `index`: Indeks task
- `task_name`: Nama task
- `vm_assigned`: VM yang ditugaskan untuk task tersebut
- `start_time`: Waktu mulai eksekusi
- `exec_time`: Waktu eksekusi task
- `finish_time`: Waktu selesai eksekusi
- `wait_time`: Waktu tunggu sebelum eksekusi dimulai

## 2. Archimedes Optimization Algorithm (AOA)

AOA bekerja dengan prinsip:

- **Eksplorasi awal** menggunakan perbedaan density & volume antar solusi
- **Eksploitasi akhir** menggunakan transfer function (T_F)
- **Representasi solusi** berupa vector VM index
- **Evaluasi fitness** = estimated makespan
- **Greedy selection** untuk update populasi

Contoh kode inti (disederhanakan):

```python
best_fitness = fitness[best_idx]
for t in range(iterations):
    T_F = exp(-t / iterations) * cos(pi * t / (2 * iterations))

    for i in range(pop_size):
        # update vector (exploration or exploitation)
        # evaluate new solution
        # greedy selection
```

Implementasi lengkap ada di `aoa_algorithm.py`.

## 5. Arsitektur dan Alur Kerja Algoritma AOA untuk Penjadwanalan Tugas

### 5.1. Pemodelan Masalah

Setiap elemen dalam masalah penjadwanalan dipetakan ke konsep fisika yang digunakan oleh AOA, seperti yang ditunjukkan pada tabel berikut:

| Konsep Fisika AOA             | Implementasi pada Penjadwanalan Tugas                                             |
| :---------------------------- | :-------------------------------------------------------------------------------- |
| **Benda (Object)**            | Sebuah **Solusi Jadwal** (kandidat pemetaan semua tugas ke VM).                   |
| **Posisi Benda**              | **Vektor Solusi**. Sebuah array di mana `vektor[i]` adalah ID VM untuk `tugas_i`. |
| **Cairan**                    | **Ruang Pencarian (Search Space)**, yaitu semua kemungkinan kombinasi jadwal.     |
| **Kualitas Sifat Fisik**      | **Kualitas Solusi**. Direpresentasikan oleh:                                      |
| &nbsp;&nbsp;&nbsp;_- Density_ | Dihitung dari **invers nilai fitness**. Fitness rendah (baik) -> Density tinggi.  |
| &nbsp;&nbsp;&nbsp;_- Volume_  | Dihitung dari komponen vektor solusi.                                             |
| **Keadaan Setimbang**         | **Solusi Optimal**, yaitu jadwal dengan **Makespan terendah**.                    |

### 5.2. Fungsi Fitness: Mengukur Kualitas Jadwal

Tujuan utama algoritma adalah meminimalkan **Makespan**. Fungsi fitness kami, `calculate_estimated_makespan`, menghitung estimasi makespan dengan cara:

1.  Untuk setiap VM, total beban dihitung dengan menjumlahkan estimasi waktu eksekusi setiap tugas yang dialokasikan padanya.
2.  Estimasi waktu eksekusi sebuah tugas pada VM tertentu dihitung berdasarkan:

    `estimated_time = (task.cpu_load / vm.cpu_cores) + (task.ram_mb / (vm.ram_gb * 1024))`

3.  **Makespan** adalah nilai maksimum dari total beban di antara semua VM. Algoritma AOA akan terus mencari jadwal yang menghasilkan nilai ini serendah mungkin.

### 5.3. Fase Pencarian dalam AOA

Algoritma secara dinamis menyeimbangkan dua perilaku pencarian untuk menemukan solusi optimal:

**1. Fase Eksplorasi (Iterasi Awal: `t < max_iter / 2`)**

- **Tujuan:** Menjelajahi sebanyak mungkin area di ruang pencarian untuk menghindari _local optima_.
- **Mekanisme:** Posisi sebuah solusi diperbarui dengan mempertimbangkan "tabrakan" dengan solusi **acak** lainnya. Hal ini menciptakan pergerakan yang divergen dan mendorong penemuan area-area baru.

  `# Gerakan dipengaruhi oleh percepatan yang didasarkan pada solusi acak`
  `new_vector[d] = population[i][d] + C1 * r1 * acc`

**2. Fase Eksploitasi (Iterasi Akhir: `t >= max_iter / 2`)**

- **Tujuan:** Menyempurnakan solusi di sekitar wilayah terbaik yang telah ditemukan.
- **Mekanisme:** Posisi sebuah solusi diperbarui dengan bergerak menuju **solusi terbaik global** (`best_solution_vector`). Pergerakan ini bersifat konvergen, memfokuskan pencarian pada area yang paling menjanjikan.

  `# Gerakan ditarik menuju solusi terbaik yang pernah ada`
  `new_vector[d] = best_solution_vector[d] + C2 * r2 * T_F * (best_solution_vector[d] - population[i][d])`

## 3. Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/dimasandhk/SOKA-Task-Scheduling-Server-Test.git
cd SOKA-Task-Scheduling-Server-Test
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# atau
.\venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Atau menggunakan `uv` (recommended):**

```bash
# Install uv sebagai dependency manager
# Lihat: https://docs.astral.sh/uv/getting-started/installation/

uv sync
```

### 4. Edit File `.env.example`, kemudian rename menjadi `.env`

Isi variabel seperti:

```conf
VM1_IP=10.15.42.77
VM2_IP=10.15.42.78
VM3_IP=10.15.42.79
VM4_IP=10.15.42.80
VM_PORT=5000
DATASET_FILE=dataset.txt
RESULTS_FILE=aoa_results.csv
```

### 5. Inisiasi Dataset untuk Scheduler

Buat file `dataset.txt` kemudian isi dengan dataset berupa angka 1 - 10. Berikut adalah contohnya:

```txt
6
5
8
2
10
3
4
4
7
3
9
1
7
9
1
8
2
5
6
10
```

### 6. Jalankan Server (Optional - untuk distributed execution)

```bash
docker compose build --no-cache
docker compose up -d
```

### 7. Jalankan Scheduler

**Jangan lupa menggunakan VPN / Wifi ITS**

```bash
python scheduler.py
```

**Atau menggunakan `uv`:**

```bash
uv run scheduler.py
```

## 4. Hasil Penjadwalan AOA

File output: `aoa_results.csv`

Berikut adalah rangkuman dari hasil sebenarnya:

### Ringkasan Eksekusi

- **Total task selesai:** 20
- **VM terlibat:** vm1, vm2, vm3, vm4
- **Makespan akhir:** 25.558703 detik
- **Zero waiting time** untuk mayoritas task

Beberapa task mengalami waiting (karena antrian VM4):

| Task       | VM  | Start     | Exec   | Finish    | Wait   |
| ---------- | --- | --------- | ------ | --------- | ------ |
| task-1-14  | vm4 | 3.081384  | 12.391 | 15.4684   | 3.062  |
| task-8-15  | vm4 | 6.930438  | 12.328 | 19.259543 | 6.906  |
| task-2-16  | vm4 | 7.955255  | 11.547 | 19.507874 | 7.937  |
| task-10-19 | vm4 | 8.921793  | 16.625 | 25.558703 | 8.906  |
| task-1-11  | vm3 | 11.688463 | 13.078 | 24.76234  | 11.672 |

Sementara task lain mostly 0 waiting time karena dialokasikan ke VM yang lebih seimbang (vm1–vm3).

File output memiliki format CSV dengan header:

```
index,task_name,vm_assigned,start_time,exec_time,finish_time,wait_time
```

Contoh isi file `aoa_results.csv`:

```csv
index,task_name,vm_assigned,start_time,exec_time,finish_time,wait_time
0,task-6-0,vm4,0.0,15.266000000061467,15.26771,0.0
1,task-5-1,vm3,0.009032,24.688000000081956,24.685179,0.0
2,task-8-2,vm4,0.010033,6.922000000020489,6.930438,0.0
3,task-2-3,vm3,0.011031,12.188000000081956,12.192256,0.0
4,task-10-4,vm3,0.011031,11.688000000081956,11.688463,0.0
5,task-3-5,vm4,0.011031,9.484000000171363,9.493329,0.0
6,task-4-6,vm4,0.012031,8.905999999959022,8.921793,0.0
7,task-4-7,vm4,0.012031,7.936999999918044,7.955255,0.0
8,task-7-8,vm4,0.013044,3.0619999999180436,3.080189,0.0
9,task-3-9,vm4,0.013044,13.093000000109896,13.11362,0.0
10,task-9-10,vm3,0.013044,21.718000000109896,21.746196,0.0
11,task-1-11,vm3,11.688463,13.077999999979511,24.76234,11.672000000020489
12,task-7-12,vm4,0.014041,12.436999999918044,12.460917,0.0
13,task-9-13,vm2,0.014041,23.280999999959022,23.299076,0.0
14,task-1-14,vm4,3.081384,12.391000000061467,15.4684,3.0619999999180436
15,task-8-15,vm4,6.930438,12.327999999979511,19.259543,6.905999999959022
16,task-2-16,vm4,7.955255,11.547000000020489,19.507874,7.936999999918044
17,task-5-17,vm2,0.015041,5.515000000130385,5.536733,0.0
18,task-6-18,vm1,0.015041,15.672000000020489,15.688357,0.0
19,task-10-19,vm4,8.921793,16.625,25.558703,8.905999999959022
```

## 6. Analisis Kinerja AOA

### 1. Load Balancing

AOA mengalokasikan mayoritas task berat ke:

- **vm3**
- **vm4**

karena keduanya memiliki core & RAM besar.

### 2. Waiting Time

Terdapat waiting signifikan pada vm4 karena cluster task berat menumpuk di satu VM → scheduler cenderung memilih vm4 karena fitness dominan mengutamakan makespan.

### 3. Makespan Optimization

AOA berhasil menekan makespan ke 25.558703 detik, dengan banyak task dieksekusi paralel.

## 7. Perbaikan yang Bisa Dilakukan

Jika ingin meningkatkan kualitas jadwal:

- Tambahkan penalti VM overload pada fungsi fitness
- Tambahkan parameter communication cost jika cluster benar-benar distributed
- Gunakan hybrid AOA + local search
- Batasi eksploitasi ke satu VM yang dominan

## 8. Kesimpulan

Implementasi AOA dalam repository ini:

- Berhasil menghasilkan schedule dengan makespan optimal
- Menggunakan modelling CPU/RAM yang realistis
- Modular dan mudah diperluas
- Cocok untuk eksperimen distributed scheduling
