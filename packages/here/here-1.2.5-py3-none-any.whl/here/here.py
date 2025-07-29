from pathlib import Path
from IPython import get_ipython
import inspect


def get_calling_script_file_path():
    # Get the stack frame of the caller
    caller_frame = inspect.stack()[1]

    # Get the file path of the caller
    caller_file = caller_frame.filename
    return caller_file


def get_file_working_directory(file=get_calling_script_file_path()):
    """
    Determines the root directory of the current file working directory.

    - If the code is being run in a Jupyter notebook, the root will be the current working directory.
    - If the code is being run in a .py script, the root will be the parent of the file's directory.
    - If neither case applies (e.g., interactive Python shell), the current working directory will be returned.

    Returns:
        Path: A Path object representing the file working directory's root.

    Example:
        >>> root = get_file_working_directory()
        >>> print(root)
        /Users/username/my_workspace
    """

    try:
        # Check if running in a Jupyter notebook
        if get_ipython() is not None and hasattr(get_ipython(), "config"):
            # Return current working directory
            file_path = Path.cwd()
        # could be a .py script or interactive in terminal.
        else:
            try:
                file_path = str(Path(get_calling_script_file_path()).parent)
            except NameError:
                print("error: Could not determine the calling script file path.")

    except NameError:
        # If __file__ is not defined (e.g., interactive shell), fallback to current working directory
        file_path = str(Path.cwd())

    return str(file_path)


def here(path=""):
    """
    Resolves a path relative to the file working directory's root.

    This function allows navigation to subfolders or parent folders of the root directory
    by accepting relative paths like "../data" or "data/output".

    Args:
        path (str): A string representing the relative path to resolve.

    Returns:
        Path: A Path object representing the resolved full path.

    Example:
        >>> file_working_directory = get_file_working_directory()
        >>> resolved_path = here("data/output")
        /Users/username/my_workspace

        >>> resolved_path = here("data/output")
        >>> resolved_path = here("../config")
        /Users/username/my_workspace/data/output

        >>> resolved_path = resolve_path("../config")
        >>> print(resolved_path)
        /Users/username/config
    """

    calling_file = inspect.stack()[2].filename
    file_working_directory = Path(calling_file)

    # Split the input path on '/' and join it with the file working directory root
    resolved_path = file_working_directory.joinpath(*path.split("/")).resolve()
    return str(resolved_path)


if __name__ == "__main__":
    # Example usage
    print("File Working Directory:", get_file_working_directory())
    print("Resolved Path of subfolders data/output:", here("data/output"))
    print("Resolved Path with config folder parallel to Parent:", here("../config"))
