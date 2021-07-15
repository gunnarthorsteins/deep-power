import subprocess


def kill(procs, filetype='exe'):
    """Kills all processes.

    Parameters:
        procs (list): The processes to be killed
        filetype (str): Defaults to exe
    """

    ft = filetype
    for proc in procs:
        comm = f'cmd /c "taskkill /IM {proc}.{ft} /F"'
        subprocess.call(comm,
                        shell=True,
                        stdout=subprocess.DEVNULL)
