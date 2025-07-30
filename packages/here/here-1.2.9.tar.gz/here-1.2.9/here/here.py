from pathlib import Path
from IPython import get_ipython
import inspect


def get_calling_script_file_path(print_debug_info=False):
    """
    Get the file path of the script that called this function.
    Handles cases where the function is called from a debugger or interactive environment.

    Args:
        print_debug_info (bool): If True, prints debug information about the call stack.

    Returns:
        str: The file path of the calling script.
    """
    stack = inspect.stack()

    # Filter out stack frames that belong to the Python interpreter or debugger
    relevant_stack = [
        frame
        for frame in stack
        if "__file__" in frame.frame.f_globals and "debugpy" not in frame.filename
    ]

    if not relevant_stack:
        # Fallback: If no relevant stack frames are found, assume interactive mode
        if print_debug_info:
            print("Debug Info: No relevant stack frames found. Assuming interactive mode.")
        return str(Path.cwd())

    # Iterate through the stack frames in reverse order
    # to find the first frame that does not contain "python.3" in its filename,
    # because those are likely to be internal Python frames or debugger frames.
    for frame in reversed(relevant_stack):
        if "python3" not in frame.filename.lower():
            initial_caller_frame = frame
            break
    else:
        # Fallback: If all frames contain "python.3", use the last frame
        initial_caller_frame = relevant_stack[-1]

    initial_caller_filename = initial_caller_frame.filename

    if print_debug_info:
        print(f"Debug Info: Found {len(relevant_stack)} relevant stack frames.")
        print(
            f"Debug Info: The function was originally called from this file: {initial_caller_filename}"
        )

    return str(Path(initial_caller_filename).resolve())


def get_file_working_directory(file=None):
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

    if file is None:
        file = get_calling_script_file_path()

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

    calling_file = get_calling_script_file_path()
    file_working_directory = Path(calling_file).parent

    # Split the input path on '/' and join it with the file working directory root
    resolved_path = file_working_directory.joinpath(*path.split("/")).resolve()
    return str(resolved_path)


if __name__ == "__main__":
    # Example usage
    print("File Working Directory:", get_file_working_directory())
    print("Resolved Path of subfolders data/output:", here("data/output"))
    print("Resolved Path with config folder parallel to Parent:", here("../config"))
