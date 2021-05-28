import wget

with open("./links", "r") as f:

    for i, line in enumerate(f):
        try:
            wget.download(line, f'icon_{i}.png')
        except:
            print(f"An error occured with {line}")
