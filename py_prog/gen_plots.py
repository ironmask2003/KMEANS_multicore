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


def take_time_cuda():
    times = {256: [], 512: [], 1024: []}
    # Open csv file
    with open("test_csv/slurm/cuda_slurm.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip header
        csvreader.__next__()
        for row in csvreader:
            t_block = 0
            for num in range(len(row)):
                if num == 0:
                    t_block = int(row[num])
                else:
                    times[t_block].append(float(row[num]))
    return times


# Function used to take all times from omp_mpi file .csv with process defined in input of the function
def take_time_omp_mpi(num_process):
    times = {1: [], 2: [], 4: [], 8: []}
    # Open csv file
    with open(f"test_csv/slurm/omp_mpi_{num_process}_slurm.csv", "r") as csvfile:
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
    process = [2]
    threads = [1, 2, 4, 8]

    tests = [
        "2D2input.inp",
        "10Dinput.inp",
        "20Dinput.inp",
        "2Dinput.inp",
        "100Dinput.inp",
        "100D2input.inp",
        "100D_200Kinput.inp",
        "100D_400Kinput.inp",
        "100D_800Kinput.inp",
        "100D_1000Kinput.inp",
    ]

    times_omp_mpi = {2: {}}
    for pcs in process:
        times_omp_mpi[pcs] = take_time_omp_mpi(pcs)

    effs = {
        2: {1: [], 2: [], 4: [], 8: []},
    }

    speedup = {
        2: {1: [], 2: [], 4: [], 8: []},
    }

    for pcs in process:
        for thread in threads:
            for test in range(len(tests)):
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

    for pcs in process:
        datas = {
            "100D_200Kinput.inp": [],
            "100D_400Kinput.inp": [],
            "100D_800Kinput.inp": [],
            "100D_1000Kinput.inp": [],
        }

        for test in range(6, len(tests)):
            data = []
            for thread in threads:
                data.append(speedup[pcs][thread][test])
            datas[tests[test]] = data

        markers = ["o", "s", "D", "^", "v", ">", "<", "p", "*", "X"]
        colors = ["b", "g", "r", "c", "m", "y", "k", "#FF5733", "#33FF57", "#5733FF"]

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

            # Aggiunge l'etichetta del valore solo al file input desiderato
            if i == "100D_1000Kinput.inp":
                # Aggiunta delle etichette vicino ad ogni punto
                for x, y in zip(threads, dt):
                    plt.text(
                        x,
                        y + 0.4,
                        f"{y:.1f}",
                        ha="center",
                        fontsize=8,
                        color=colors[cont],
                    )
            cont += 1

        # Personalizza il grafico
        plt.xscale("log", base=2)  # Scala logaritmica per il numero di thread
        plt.xticks(threads, threads)  # Mostra solo i valori specificati
        plt.ylim(0, 16)  # Limiti asse Y
        plt.xlabel("Number of Threads")
        plt.ylabel("Speedup")
        plt.title(f"Speedup with MPI Processes = {pcs}")
        plt.grid(True, linestyle="--", alpha=0.6)

        plt.axhline(y=1, color="black", linestyle="dashed", label="Sequential baseline")

        plt.legend()

        plt.savefig(
            f"test_csv/plots/speedup/plot_omp_mpi_{pcs}_big_slurm.png",
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

        for test in range(len(tests) - 4):
            data = []
            for thread in times_omp_mpi[pcs].keys():
                data.append(effs[pcs][thread][test])
            datas[tests[test]] = data

        markers = ["o", "s", "D", "^", "v", ">", "<", "p", "*", "X"]
        colors = ["b", "g", "r", "c", "m", "y", "k", "#FF5733", "#33FF57", "#5733FF"]

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
        plt.ylim(0, 1.05)  # Limiti asse Y
        plt.xlabel("Number of Threads")
        plt.ylabel("Efficiency")
        plt.title(f"Efficiency with MPI Processes = {pcs}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.axhline(y=1, color="black", linestyle="dashed", label="Ideal efficiency")
        plt.legend()

        plt.savefig(
            f"test_csv/plots/efficency/plot_omp_mpi_{pcs}_small_slurm.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.clf()


def cuda(seq_times):
    cuda_times = take_time_cuda()

    tests = [
        "2D2input.inp",
        "10Dinput.inp",
        "2Dinput.inp",
        "20Dinput.inp",
        "100Dinput.inp",
        "100D2input.inp",
        "200Kinput.inp",
        "400Kinput.inp",
        "800Kinput.inp",
        "1000Kinput.inp",
    ]

    small_test = [
        "2D2input.inp",
        "10Dinput.inp",
        "2Dinput.inp",
        "20Dinput.inp",
        "100Dinput.inp",
    ]

    big_test = [
        "100D2input.inp",
        "200Kinput.inp",
        "400Kinput.inp",
        "800Kinput.inp",
        "1000Kinput.inp",
    ]

    speedup = {256: [], 512: [], 1024: []}

    for t_blocks in speedup.keys():
        for test in range(len(tests)):
            speedup[t_blocks].append(
                calculate_eff(1, 1, seq_times[test], cuda_times[t_blocks][test])
            )

    datas = {
        "100D_200Kinput.inp": [],
        "100D_400Kinput.inp": [],
        "100D_800Kinput.inp": [],
        "100D_1000Kinput.inp": [],
    }

    for test in range(6, len(tests)):
        data = []
        for t_blocks in speedup.keys():
            data.append(speedup[t_blocks][test])
        datas[tests[test]] = data

    # Personalizza il grafico
    plt.xlabel("Thread per blocco")
    plt.xticks(speedup.keys(), speedup.keys())  # Mostra solo i valori specificati
    plt.ylabel("Speedup")
    plt.title("Tempi di esecuzione dei test")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.savefig(
        "test_csv/plots/speedup/plot_cuda_big_slurm.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.clf()


def gen_plot():
    # Calculate efficency of omp_mpi version
    seq_times = take_time("test_csv/slurm/seq_slurm.csv")

    omp_mpi(seq_times)
    # cuda(seq_times)


if __name__ == "__main__":
    gen_plot()
