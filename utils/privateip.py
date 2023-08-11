from utils.subnet import subnet_parse

def is_private_ip(ip, exclusion_ranges):
    # Check if IP address falls into excluded IP ranges, including private IP ranges
    ip_parts = ip.split('.')

    # Check excluded IP ranges (individual IP ranges and subnet notation)
    for exclusion_range in exclusion_ranges:
        if '/' in exclusion_range:  # Check subnet notation
            if subnet_parse(ip, exclusion_range):
                return True
        else:  # Check individual IP range
            start, end = exclusion_range.split('-')
            start_parts = start.split('.')
            end_parts = end.split('.')
            ip_parts_int = list(map(int, ip_parts))
            start_parts_int = list(map(int, start_parts))
            end_parts_int = list(map(int, end_parts))

            if (
                start_parts_int[0] <= ip_parts_int[0] <= end_parts_int[0]
                and start_parts_int[1] <= ip_parts_int[1] <= end_parts_int[1]
                and start_parts_int[2] <= ip_parts_int[2] <= end_parts_int[2]
                and start_parts_int[3] <= ip_parts_int[3] <= end_parts_int[3]
            ):
                return True

    return False