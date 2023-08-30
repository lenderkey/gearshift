from Context import Context

def ingest_file(context:Context, filename:str, data:bytes=None):
    L = "Context.ingest_file"

    from structures import FileRecord

    if data is None:
        with open(filename, "rb") as fin:
            data = fin.read()
    
    data_hash = helpers.sha256_data(data)
    return

##    file_record = 

    link_filename = self.dst_link_path(data_hash)

    if os.path.exists(link_filename):
        logger.info(f"{L}: {link_filename=} already exists - no need to write")
        return ( data_hash, False )
    
    os.makedirs(os.path.dirname(link_filename), exist_ok=True)

    try:
        link_filename_tmp = link_filename + ".tmp"
        with open(link_filename_tmp, "wb") as fout:
            fout.write(data)
    except IOError as x:
        logger.error(f"{L}: {x} writing {link_filename_tmp=}")

        try: os.remove(link_filename_tmp)
        except: pass

        sys.exit(1)

    os.rename(link_filename_tmp, link_filename)
    logger.info(f"{L}: wrote {link_filename=}")

    return ( data_hash, True )

