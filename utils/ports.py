def port_parse(port_range):
    if '-' in port_range:
        start_port, end_port = port_range.split('-')
        return range(int(start_port), int(end_port) + 1)
    else:
        return [int(port_range)]