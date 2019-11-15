def qta(instream,read=''):
    data_stream = instream.readlines()
    c=0
    line_counter=0
    for line in data_stream:
        try:
            line = line.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
        if line[0] == '+':
            c=0
        if c==2:
            yield '>'+str(line_counter)+read+'\n'
            line_counter += 1
            #+line[1:].replace(" ", "_"))
        if c==3:
            yield line
        c += 1
