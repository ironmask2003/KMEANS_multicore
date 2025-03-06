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


def run_test(vers, test, comp_times):
    # Esecuzione della versione scelta per 100 volte
    sh_file = f"{vers}_run.sh"
    exec_file(sh_file, test)
    comp_times.append(take_num(f"comp_time/{vers}/comp_time{test}.txt"))

    return check_out(
        f"output_files/seq/output{test}.txt",
        f"output_files/{vers}/output{test}.txt",
    )
