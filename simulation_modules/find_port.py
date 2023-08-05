import psutil


def find_process_port(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.info['pid'])
            for conn in process.connections():
                return conn.laddr.port
    return None


if __name__ == "__main__":
    process_name_to_check = "opp_run_dbg"
    port = find_process_port(process_name_to_check)

    if port:
        print(port)
    else:
        print("shoot")