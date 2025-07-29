import random
def random_copy(l: list, repeats: int, Reverb=False):
    try: 
        random_repeat_list = [random.choice(l) for i in range(repeats)]
        if Reverb == True: random_repeat_list[::-1]
        return random_repeat_list
    except: 
        return "Error"
    
#Create by Xwared Team and Dovintc, Project SUWWP - Speeding up Work with Python (SUW2P)