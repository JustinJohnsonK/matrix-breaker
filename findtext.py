original = "he enjoy to play cricket"
find_text = "enjoy to play"

i, j = 0, 0
start, end = 0, 0
while start < len(original):
    if j == len(find_text):
        print("start: ", start-1)
        print("end: ", end-1)
        break
    if find_text[i] == original[j]:
        end = j
        i += 1
        j += 1
    else:
        i = 0
        j = start
        start += 1
