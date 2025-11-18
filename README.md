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

Sistem scheduler ini membaca daftar task dengan parameter:

- `cpu_load`
- `ram_mb`
- `task_idx`
- `kategori` (jika ada)

Kemudian AOA akan menentukan VM mana yang paling optimal untuk setiap task berdasarkan:

- jumlah CPU core
- kapasitas RAM
- estimasi waktu eksekusi
- density & volume per iterasi
- greedy selection improvement

Hasil akhir berupa file `aoa_results.csv` yang berisi jadwal lengkap.

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

### ▶ Ringkasan Eksekusi

- **Total task selesai:** 20
- **VM terlibat:** vm1, vm2, vm3, vm4
- **Makespan akhir:** sekitar 25.56 detik
- **Zero waiting time** untuk mayoritas task

Beberapa task mengalami waiting (karena antrian VM4):

| Task       | VM  | Start | Exec   | Finish | Wait    |
| ---------- | --- | ----- | ------ | ------ | ------- |
| task-1-14  | vm4 | 3.081 | 12.391 | 15.468 | 3.062 s |
| task-8-15  | vm4 | 6.930 | 12.328 | 19.259 | 6.906 s |
| task-2-16  | vm4 | 7.955 | 11.547 | 19.507 | 7.937 s |
| task-10-19 | vm4 | 8.921 | 16.625 | 25.558 | 8.906 s |

Sementara task lain mostly 0 waiting time karena dialokasikan ke VM yang lebih seimbang (vm1–vm3).

## 5. Format Output (aoa_results.csv)

Contoh isi bisa dilihat di

- [aoa_results.csv](/aoa_results.csv)

## 6. Analisis Kinerja AOA

### 1. Load Balancing

AOA mengalokasikan mayoritas task berat ke:

- **vm3**
- **vm4**

karena keduanya memiliki core & RAM besar.

### 2. Waiting Time

Terdapat waiting signifikan pada vm4 karena cluster task berat menumpuk di satu VM → scheduler cenderung memilih vm4 karena fitness dominan mengutamakan makespan.

### 3. Makespan Optimization

AOA berhasil menekan makespan ke sekitar 25.56 detik, dengan banyak task dieksekusi paralel.

## 8. Kesimpulan

Implementasi AOA dalam repository ini:

- Berhasil menghasilkan schedule dengan makespan optimal
- Menggunakan modelling CPU/RAM yang realistis
- Modular dan mudah diperluas
- Cocok untuk eksperimen distributed scheduling
