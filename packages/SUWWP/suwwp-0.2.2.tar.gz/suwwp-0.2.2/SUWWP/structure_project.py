import os

def structure_project(folder_path = ".", Mode="file", WMode=True):

    '''
        Returns all files or folders depending on the Mode\
        
        Parametrs:
        -folder_path (str): the path to the desired folder is passed automatically
        installed "."
        -Mode (str: "files" or "files-directory"): the mod is transmitted using 
            which folder will be opened, these are files or files with folders,
        "files"
        -WMode (bool) is automatically set: along with the folder/file data, Mode is also added to disable it. 
        WMode=False, automatically set to "True"
    '''

    returned = []
    if WMode: returned.append(f"MODE!: '{Mode}' TURN OFF THIS FUNCTION: 'WMode=False'")
    if Mode == "file":
        all_items = os.listdir(folder_path)
        files = [f for f in all_items if os.path.isfile(os.path.join(folder_path, f))]
        returned.append(files)
    if Mode == "file-directory":
        result = []
        for name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, name)
            if os.path.isfile(full_path):
                result.append((name, 'file'))
            elif os.path.isdir(full_path):
                result.append((name, 'dir'))
        returned.append(result)
    return returned

#Create by Xwared Team and Dovintc, Project SUWWP - Speeding up Work with Python (SUW2P)