import os
import sys
import subprocess


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Absolute paths to the bundled Python and script
venv_python = os.path.join("DetectionEnvironment", "bin", "python")
detection_script = resource_path(os.path.join("DetectionScript", "Predict.py"))


def execute_sub_process(file, size, outputdir):
    """
    Runs the predict.py model using some args.
    """
    params = [
        "--input_file",
        file,
        "--input_size",
        size,
        "--snapshot_dir",
        outputdir]
    result = subprocess.run(
        [venv_python, detection_script] + params, capture_output=True, text=True)

    # Optional: print or log output
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    return result
