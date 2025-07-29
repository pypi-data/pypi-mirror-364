import time
def time_now(format=None, sep=":", help=False):

    """
    Returns the current time in the specified format.

    Parameters:
    - format (str or None or ""): a format string containing the characters Y (year), H (hours),
            M (minutes), S (seconds). For example: 'YHMS'.
      if there is an error in the format such as "GHM", it will 
      return the error "ValueError("Invalid format character")"
    - sep (str): divider between time parts.
    - help (bool): If True, adds a signature to the values (for example, 'H' to the clock).

    Returns:
    - str: formatted time or timestamp (if format == None).
    """
    
    if format is not None and format != "":
        format_time = ""
        format = format.upper()
        for char in format:
            if char in "YHMS":
                help_s = ""
                if help:
                    help_s = f"{char}"
                format_time += f"%{char}{help_s}{sep}"
            else: raise ValueError("Invalid format character")
        formatatted_time = time.strftime(format_time, time.localtime())
        return formatatted_time[:-1*len(sep)]
    return time.time()

test = False
if test:
    try: 
        print(time_now(format="HM")) # output: 09:33
        print(time_now(format="HM", sep=" / ")) # changes the separator to /. output: 09/33
        print(time_now(format="YHMS", sep=":::")) # supports any formats. output: 2025:::09:::33:::53
        print(time_now(format="MS", help=True)) # support for auxiliary characters for more precise concepts of hours, minutes, etc. output: 33M:53S
        print(time_now(format="jHM")) #error "j" there is no such format will return "ValueError("Invalid format character")". output: "ValueError("Invalid format character")"
    except ValueError as e:
        print(f"Erorr: {e}")

#Create by Xwared Team and Dovintc, Project SUWWP - Speeding up Work with Python (SUW2P)