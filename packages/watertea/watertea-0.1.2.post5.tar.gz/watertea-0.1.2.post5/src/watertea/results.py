from datetime import datetime
import glob 
import os 
from shutil import copyfile
import warnings

def results():
    """
    Creates a directory structure for saving results, based on the current date.

    This function creates a 'results' directory and further subdirectories based on the current date and time, 
    where results from the experiment can be stored.

    Returns:
        str: The path of the created folder where results will be saved.
    """
    today = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Define the path for the results folder
    base_folder = "results"
    date_folder = os.path.join(base_folder, today)
    
    # Create 'results' folder if it doesn't exist
    os.makedirs(base_folder, exist_ok=True)
    
    # Create the date-specific folder if it doesn't exist
    os.makedirs(date_folder, exist_ok=True)
    os.makedirs(os.path.join(date_folder,"src"),exist_ok=True)
    os.makedirs(os.path.join(date_folder,"logs"),exist_ok=True)

    files = [os.path.basename(i) for i in glob.glob('*.py')]
    for src in files:
        copyfile(src, os.path.join(os.path.join(date_folder,"src"),src))
    files = [os.path.basename(i) for i in glob.glob('*.slurm')]
    for src in files:
        copyfile(src, os.path.join(os.path.join(date_folder,"src"),src))
    files = [os.path.basename(i) for i in glob.glob('*.sh')]
    for src in files:
        copyfile(src, os.path.join(os.path.join(date_folder,"src"),src))

    try:
        copyfile("logs/"+str(os.getenv("SLURM_JOB_ID"))+".err", os.path.join(os.path.join(date_folder,"logs"),str(os.getenv("SLURM_JOB_ID"))+".err"))
        copyfile("logs/"+str(os.getenv("SLURM_JOB_ID"))+".out", os.path.join(os.path.join(date_folder,"logs"),str(os.getenv("SLURM_JOB_ID"))+".out"))
                
    except:
        warnings.warn("Standard logs not found", UserWarning)
    try:
        copyfile("logs/debug.err", os.path.join(os.path.join(date_folder,"logs"),"debug.err"))
        copyfile("logs/debug.out", os.path.join(os.path.join(date_folder,"logs"),"debug.out"))
    except:
        warnings.warn("Debug logs not found", UserWarning)

    print(f"Folder created: {date_folder}")
    return date_folder  # Return the path for further use if needed
