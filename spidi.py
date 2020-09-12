vals = "1, 2,4,9,56, 48,52, 3,11,357,5,7,6" #список значений
di = "2-6,8-9,12-54,87-90" #список диапазонов значений
vals_di = "" #список значений и диапазонов значений

def spidi(spidi:str,sep=",",sep_di="-"):
    print(spidi.split(sep))

print(vals)
spidi(vals)
