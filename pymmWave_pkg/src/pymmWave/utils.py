
def load_cfg_file(filepath: str) -> list[str]:
    """Loads a config file to a list of strings. Wrapper around readlines() with some simple verification.

    Args:
        filepath (str): Filepath, relative paths should be ok

    Returns:
        list[str]: List of lines as str
    """
    
    assert len(filepath) > 4
    assert filepath[-4:] == ".cfg"

    data: list[str]
    with open(filepath, 'r') as f:
        data = f.readlines()
    
    return data


