import fileinput

list_of_lists = []

        # Read in the file
# with open('./Sites/Quantcast-Top-Million8.txt', 'r') as file :
#   filedata = file.read()

# # Replace the target string
# filedata = filedata.replace('[\'\',', '')

with open('./Sites/Quantcast-Top-Million.txt') as f:
    for line in f:
        # inner_list = [elt.strip() for elt in line.split(',')]
        # in alternative, if you need to use the file content as numbers
        # inner_list = [int(elt.strip()) for elt in line.split(',')]
        list_of_lists.append(line)
        if line.startswith('[\'114005'):
            break


# Write the file out again
with open('./Sites/Quantcast-Top-Million2.txt', 'w') as file:
  file.write(str(list_of_lists))