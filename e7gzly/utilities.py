def row_to_number(row):
    row = row.lower()
    idx = 0
    for digit in row:
        idx *= 26
        idx += ord(digit) - ord('a') + 1
    return idx - 1
