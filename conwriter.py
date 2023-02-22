import transfer_tools as tls

server_host = "192.168.0.197\n"
server_port = "55\n"
server_delay = "0\n"
server_path = "C:\\Users\\STanch\\Desktop\\Surveys\\\n"
server_name = "server_config.txt"

source_host = "65.183.134.63\n"
source_port = "56\n"
source_delay = "30\n"
source_path = "/home/stanch/public/DZTs\n"
source_name = "source_config.txt"

tls.configWriter(server_name,server_host,server_port,server_delay,server_path)
tls.configWriter(source_name,source_host,source_port,source_delay,source_path)