import ___project_name___ as project
from j_vault_http_client_xethhung12 import jvault_http_client
def main():
    jvault_http_client.load_to_env()
    project.hello("user")
