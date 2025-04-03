import csv
from matplotlib import pyplot as plt


# Function used to take all times from seq file .csv
def take_time(filename):
    times = []
    # Open csv file
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip header
        csvreader.__next__()
        # Take times from the file and appent its on times list
        for row in csvreader:
            for num in row:
                times.append(float(num))
    return times


# Function used to take all times from omp_mpi file .csv with process defined in input of the function
def take_time_omp_mpi(num_process):
    times = {1: [], 2: [], 4: [], 8: [], 16: [], 32: []}
    # Open csv file
    with open(f"test_csv/omp_mpi_{num_process}.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip header
        csvreader.__next__()
        for row in csvreader:
            thread = 0
            for num in range(len(row)):
                if num == 0:
                    continue
                elif num == 1:
                    thread = int(row[num])
                else:
                    times[thread].append(float(row[num]))
    return times


def calculate_eff(num_process, num_thread, seq_time, omp_mpi_time):
    return seq_time / (num_process * num_thread * omp_mpi_time)


def omp_mpi(seq_times):
    process = [2, 4, 8]
    times_omp_mpi = {2: {}, 4: {}, 8: {}}
    for pcs in process:
        times_omp_mpi[pcs] = take_time_omp_mpi(pcs)

    effs = {
        2: {1: [], 2: [], 4: [], 8: [], 16: [], 32: []},
        4: {1: [], 2: [], 4: [], 8: [], 16: [], 32: []},
        8: {1: [], 2: [], 4: [], 8: [], 16: [], 32: []},
    }

    speedup = {
        2: {1: [], 2: [], 4: [], 8: [], 16: [], 32: []},
        4: {1: [], 2: [], 4: [], 8: [], 16: [], 32: []},
        8: {1: [], 2: [], 4: [], 8: [], 16: [], 32: []},
    }

    for pcs in effs.keys():
        for thread in times_omp_mpi[pcs].keys():
            for test in range(6):
                effs[pcs][thread].append(
                    calculate_eff(
                        pcs, thread, seq_times[test], times_omp_mpi[pcs][thread][test]
                    )
                )
                speedup[pcs][thread].append(
                    calculate_eff(
                        1, 1, seq_times[test], times_omp_mpi[pcs][thread][test]
                    )
                )

    threads = [1, 2, 4, 8, 16, 32]
    tests = [
        "2D2input.inp",
        "10Dinput.inp",
        "20Dinput.inp",
        "2Dinput.inp",
        "100Dinput.inp",
        "100D2input.inp",
    ]

    for pcs in process:
        datas = {
            "2D2input.inp": [],
            "10Dinput.inp": [],
            "20Dinput.inp": [],
            "2Dinput.inp": [],
            "100Dinput.inp": [],
            "100D2input.inp": [],
        }

        for test in range(len(tests)):
            data = []
            for thread in times_omp_mpi[pcs].keys():
                data.append(speedup[pcs][thread][test])
            datas[tests[test]] = data

        markers = ["o", "s", "^", "x", "p", "D"]
        colors = ["blue", "orange", "green", "red", "purple", "brown"]

        cont = 0
        plt.figure(figsize=(10, 6))
        for i, dt in datas.items():
            plt.plot(
                threads,
                dt,
                marker=markers[cont],
                linestyle="-",
                color=colors[cont],
                label=f"{i}",
            )
            cont += 1

        # Personalizza il grafico
        plt.xscale("log", base=2)  # Scala logaritmica per il numero di thread
        plt.xticks(threads, threads)  # Mostra solo i valori specificati
        plt.ylim(0, 80)  # Limiti asse Y
        plt.xlabel("Number of Threads")
        plt.ylabel("Speedup")
        plt.title(f"Speedup with MPI Processes = {pcs}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()

        plt.savefig(
            f"test_csv/plots/speedup/plot_omp_mpi_{pcs}.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.clf()

    for pcs in process:
        datas = {
            "2D2input.inp": [],
            "10Dinput.inp": [],
            "20Dinput.inp": [],
            "2Dinput.inp": [],
            "100Dinput.inp": [],
            "100D2input.inp": [],
        }

        for test in range(len(tests)):
            data = []
            for thread in times_omp_mpi[pcs].keys():
                data.append(effs[pcs][thread][test])
            datas[tests[test]] = data

        markers = ["o", "s", "^", "x", "p", "D"]
        colors = ["blue", "orange", "green", "red", "purple", "brown"]

        cont = 0
        plt.figure(figsize=(10, 6))
        for i, dt in datas.items():
            plt.plot(
                threads,
                dt,
                marker=markers[cont],
                linestyle="-",
                color=colors[cont],
                label=f"{i}",
            )
            cont += 1

        # Personalizza il grafico
        plt.xscale("log", base=2)  # Scala logaritmica per il numero di thread
        plt.xticks(threads, threads)  # Mostra solo i valori specificati
        plt.ylim(0, 1)  # Limiti asse Y
        plt.xlabel("Number of Threads")
        plt.ylabel("Efficiency")
        plt.title(f"Efficiency with MPI Processes = {pcs}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()

        plt.savefig(
            f"test_csv/plots/efficency/plot_omp_mpi_{pcs}.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.clf()


def cuda(seq_times):
    cuda_times = take_time("test_csv/cuda_colab.csv")

    tests = [
        "2D2input.inp",
        "10Dinput.inp",
        "20Dinput.inp",
        "2Dinput.inp",
        "100Dinput.inp",
        "100D2input.inp",
    ]

    speedup = []

    for test in range(len(tests)):
        speedup.append(calculate_eff(1, 1, seq_times[test], cuda_times[test]))

    plt.figure(figsize=(10, 6))
    plt.scatter(tests, speedup, marker="D", s=80, color="b")

    # Personalizza il grafico
    plt.xlabel("Test")
    plt.ylabel("Tempo (secondi)")
    plt.title("Tempi di esecuzione dei test")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.savefig(
        "test_csv/plots/speedup/plot_cuda.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.clf()


if __name__ == "__main__":
    # Calculate efficency of omp_mpi version
    seq_times = take_time("test_csv/seq.csv")
    seq_times_colab = take_time("test_csv/seq_colab.csv")

    omp_mpi(seq_times)
    cuda(seq_times_colab)
