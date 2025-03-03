# Funzione che controlla riga per riga se due file sono uguali
def check_out(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                return False
    return True


# Funzione che legge un file e prende il numero all'interno del file
def take_num(file) -> float:
    with open(file, "r") as f:
        get_num = f.readline()
        return float(get_num)


# Prende in input un file .sh e lo esegue con un input per esempio, deve eseguire ./ciao.sh 100D
def exec_file(file, test):
    import subprocess

    # Voglio che il subprocess non stampi nulla a schermo
    subprocess.run(["sh", file, test])
    return


if __name__ == "__main__":
    # Prende in input una stringa
    vers = input("Inserisci la versione del file da controllare: ")
    test = input("Inserisci la versione del file di test: ")

    comp_times = []

    # Esecuzione della versione scelta per 100 volte
    for i in range(100):
        print("\nEsecuzione numero: \n", i)
        sh_file = f"{vers}_run.sh"
        exec_file(sh_file, test)
        comp_times.append(take_num(f"comp_time/{vers}/comp_time{test}.txt"))

        if (
            check_out(
                f"output_files/seq/output{test}.txt",
                f"output_files/{vers}/output{test}.txt",
            )
            == True
        ):
            continue
        else:
            print("Error file seq and file mpi are different")
            break

    # Calcolo della media degli elementi in comp_times
    media = sum(comp_times) / len(comp_times)
    # Calcolo della deviazione standard
    dev_std = (sum([(x - media) ** 2 for x in comp_times]) / len(comp_times)) ** 0.5

    print("\nMedia computation time: ", media)
    print("Deviazione standard: ", dev_std)
    print("All test passed")
