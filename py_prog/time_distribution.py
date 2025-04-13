import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


def time_distribution(vers: str, pcs: int):
    """
    Function to create a time distribution plot for different test cases.
    param:
        - vers: Version of the program (e.g., "omp_mpi", "cuda")
        - pcs: Number of processes (e.g., 2, 4, 8)
    """

    # Define the tests to be analyzed
    tests = [
        "2D2",
        "100D_1000K",
    ]

    all_times = []

    for test in tests:
        # Open comp_time file and read all lines
        with open(f"./comp_time/{vers}/comp_time{test}.csv", "r") as f:
            times_temp = f.readlines()

        # Convert all element in the array to float
        times_temp = [float(time) for time in times_temp]
        all_times.append(times_temp)

    # Palette di colori per distinguere i 9 dataset
    colors = sns.color_palette("tab10", 10)  # Usa una palette di 9 colori differenti

    # Creazione del grafico
    plt.figure(figsize=(10, 6))

    for i, times in enumerate(all_times):
        # Calcoliamo la densità usando SciPy
        kde = gaussian_kde(
            times, bw_method=0.1
        )  # bw_method regola la larghezza di banda

        # Definiamo un intervallo di punti X su cui calcolare la densità
        x_vals = np.linspace(
            min(times), max(times), 300
        )  # 300 punti per maggiore precisione
        y_vals = kde(x_vals)  # Calcoliamo la densità per ogni punto X

        # Plottiamo la curva KDE ottenuta con SciPy
        plt.fill_between(
            x_vals,
            y_vals,
            alpha=0.2,
            color=colors[i],
            label=f"File input: input{tests[i]}.inp",
        )

        # Calcoliamo mediana e media
        mediana = np.median(times)
        media = np.mean(times)

        std_dev = np.std(times)
        cv = std_dev / media
        cv_percent = cv * 100

        plt.plot([], [], " ", label=f"CV: {cv_percent:.2f}%")
        plt.plot([], [], " ", label=f"StdDev: {std_dev:.6f}s")

        # Aggiungiamo linee verticali per la mediana e la media
        plt.axvline(
            mediana, color=colors[i], linestyle="-", linewidth=1, label="Mediana"
        )
        plt.axvline(media, color=colors[i], linestyle="--", linewidth=1, label="Media")

        # Aggiunta di titoli e legenda
        plt.xlabel("Tempo di esecuzione")
        plt.ylabel("Densità")
        plt.title("Distribuzione dei Tempi con Mediana e Media aritmetica")
        plt.legend()
        plt.savefig(
            f"test_csv/plots/time_distribution/time_distribution_{tests[i]}_{vers}{'_' if vers == 'cuda' else f'_{pcs}'}.png",
            dpi=300,
            bbox_inches="tight",
        )

        plt.clf()
