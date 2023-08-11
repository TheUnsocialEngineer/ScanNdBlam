
def exclusion_parse(file_path):
    exclusion_ranges = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('-')
            if len(parts) == 1:  # CIDR notation
                exclusion_ranges.append(parts[0])
            elif len(parts) == 2:  # Individual IP range
                exclusion_ranges.append((parts[0], parts[1]))
            else:
                print(f"Invalid exclusion range format in file: {line.strip()}")
    return exclusion_ranges