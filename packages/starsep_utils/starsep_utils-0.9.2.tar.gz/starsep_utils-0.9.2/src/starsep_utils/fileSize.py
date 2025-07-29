def formatFileSize(size: int, precision: int = 0) -> str:
    if size < 1024:
        return f"{size}B"
    elif size < 1024**2:
        return f"{size / 1024:.{precision}f}kB"
    elif size < 1024**3:
        return f"{size / 1024**2:.{precision}f}MB"
    elif size < 1024**4:
        return f"{size / 1024**3:.{precision}f}GB"
    else:
        return f"{size / 1024**4:.{precision}f}TB"
