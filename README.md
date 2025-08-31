# K-Means Clustering Multicore Implementation

Questo progetto implementa l'algoritmo di clustering K-Means utilizzando diverse tecniche di programmazione parallela per confrontare le prestazioni su architetture multicore e GPU.

## 📋 Panoramica del Progetto

Il progetto presenta tre implementazioni dell'algoritmo K-Means:
- **Versione Sequenziale** (`KMEANS.c`): Implementazione di riferimento single-threaded
- **Versione OpenMP/MPI** (`KMEANS_omp_mpi.c`): Implementazione ibrida che combina parallelizzazione a memoria condivisa (OpenMP) e distribuita (MPI)
- **Versione CUDA** (`KMEANS_cuda.cu`): Implementazione per GPU NVIDIA usando CUDA

## 🗂️ Struttura del Progetto

```
KMEANS_multicore/
├── KMEANS.c              # Versione sequenziale di riferimento
├── KMEANS_omp_mpi.c      # Versione ibrida OpenMP + MPI
├── KMEANS_cuda.cu        # Versione CUDA per GPU
├── Makefile              # Build system per tutte le versioni
├── README.md             # Questo file
│
├── comp_time/            # Dati sui tempi di computazione
│   ├── seq/              # Tempi versione sequenziale
│   ├── omp_mpi/          # Tempi versione OpenMP/MPI
│   └── cuda/             # Tempi versione CUDA
│
├── jobs/                 # Script SLURM per esecuzione su cluster
│   ├── job.slurm         # Job principale
│   └── backup_*.slurm    # Backup dei job
│
├── output_files/         # File di output dei risultati del clustering
│   └── seq/              # Output versione sequenziale
│
├── py_prog/              # Script Python per analisi e visualizzazione
│   ├── gen_plots.py      # Generazione grafici di performance
│   ├── run.py            # Script di esecuzione automatica
│   ├── tester.py         # Test di correttezza
│   └── time_distribution.py # Analisi distribuzione tempi
│
├── test_csv/             # Dati di benchmarking e grafici
│   ├── plots/            # Grafici di speedup ed efficienza
│   │   ├── efficency/    # Grafici di efficienza
│   │   ├── speedup/      # Grafici di speedup
│   │   └── time_distribution/ # Distribuzione dei tempi
│   └── slurm/            # Dati da esecuzioni su cluster SLURM
│
├── test_files/           # File di input per i test
│   ├── gen_input.py      # Generatore di dati di test
│   └── input*.inp        # File di input con diverse dimensioni
│
└── Relazione/            # Documentazione del progetto
    └── relazione.pdf     # Relazione tecnica completa
```

## 🚀 Compilazione

Il progetto utilizza un Makefile per automatizzare la compilazione:

```bash
# Compila tutte le versioni
make all

# Compila solo versioni specifiche
make KMEANS_seq      # Versione sequenziale
make KMEANS_omp      # Versione OpenMP (se disponibile)
make KMEANS_mpi      # Versione MPI (se disponibile)
make KMEANS_cuda     # Versione CUDA
make KMEANS_omp_mpi  # Versione ibrida OpenMP/MPI

# Mostra help
make help

# Pulisce i file compilati
make clean
```

### Prerequisiti

- **GCC**: Per le versioni C/OpenMP
- **MPI**: Per le versioni MPI (OpenMPI o MPICH)
- **NVCC**: Per la versione CUDA (CUDA Toolkit)
- **Python 3**: Per gli script di analisi
- **Matplotlib**: Per la generazione dei grafici

## 🎯 Utilizzo

### Esecuzione Diretta

```bash
# Versione sequenziale
./KMEANS_seq input_file.inp k max_iterations flag tolerance output_file.txt time_file.csv

# Versione OpenMP/MPI
mpirun -n <num_processes> ./KMEANS_omp_mpi input_file.inp k max_iterations flag tolerance output_file.txt time_file.csv <num_threads>

# Versione CUDA
./KMEANS_cuda input_file.inp k max_iterations flag tolerance output_file.txt time_file.csv <block_size>
```

### Parametri

- `input_file.inp`: File di input con i dati da clusterizzare
- `k`: Numero di cluster desiderati
- `max_iterations`: Numero massimo di iterazioni
- `flag`: Flag per output dettagliato (0 o 1)
- `tolerance`: Soglia di convergenza
- `output_file.txt`: File di output con i risultati
- `time_file.csv`: File CSV con i tempi di esecuzione
- `<num_threads>`: Numero di thread OpenMP (versione ibrida)
- `<block_size>`: Dimensione del blocco CUDA (versione GPU)

### Esecuzione su Cluster SLURM

Il progetto include script SLURM per l'esecuzione su cluster HPC:

```bash
sbatch jobs/job.slurm
```

## 📊 Analisi delle Prestazioni

### Script Python Disponibili

1. **`gen_plots.py`**: Genera grafici di:
   - Speedup relativo
   - Efficienza parallela
   - Roofline model per CUDA
   
2. **`run.py`**: Automatizza l'esecuzione dei test su diverse configurazioni

3. **`time_distribution.py`**: Analizza la distribuzione dei tempi di esecuzione

4. **`tester.py`**: Verifica la correttezza dei risultati confrontando le diverse versioni

### Metriche Analizzate

- **Speedup**: Rapporto tra tempo sequenziale e tempo parallelo
- **Efficienza**: Speedup normalizzato per il numero di processori
- **Scalabilità**: Comportamento all'aumentare dei processori/thread
- **Throughput**: Punti processati per unità di tempo

## 🧪 Dataset di Test

Il progetto include diversi dataset di test con caratteristiche variabili:

- `input2D.inp`, `input2D2.inp`: Dati 2D per visualizzazione
- `input10D.inp`, `input20D.inp`: Dati a media dimensionalità
- `input100D.inp`, `input100D2.inp`: Dati ad alta dimensionalità
- Dataset grandi (200K, 400K, 800K, 1M punti) per test di scalabilità

I dataset possono essere generati usando `test_files/gen_input.py`.

## 🔬 Risultati Sperimentali

I risultati degli esperimenti sono organizzati in:

- **`comp_time/`**: Tempi di esecuzione raw per ogni versione
- **`test_csv/`**: Dati aggregati e preprocessati
- **`test_csv/plots/`**: Visualizzazioni grafiche delle prestazioni

### Configurazioni Testate

- **Sequenziale**: Baseline per il confronto
- **OpenMP/MPI**: 2, 4, 8 processi MPI con diversi numeri di thread OpenMP
- **CUDA**: Diverse dimensioni di blocco (256, 512, 1024 thread)

## 📈 Visualizzazioni

Il progetto genera automaticamente:

- Grafici di speedup per diverse dimensioni di input
- Grafici di efficienza parallela
- Analisi della distribuzione temporale
- Roofline model per l'analisi delle prestazioni GPU

## 🤝 Contributi

**Autori originali**: Diego García-Álvarez, Arturo Gonzalez-Escribano (Grupo Trasgo)

**Licenza**: Creative Commons Attribution-ShareAlike 4.0 International License

## 📚 Documentazione Aggiuntiva

Per maggiori dettagli sulle implementazioni e i risultati sperimentali, consultare:
- `Relazione/relazione.pdf`: Relazione tecnica completa
- Commenti nel codice sorgente per dettagli implementativi
- Script Python per la riproduzione degli esperimenti

---