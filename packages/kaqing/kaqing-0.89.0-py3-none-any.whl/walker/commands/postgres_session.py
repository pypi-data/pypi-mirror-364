import subprocess

from walker.config import Config
from walker.k8s_utils import create_pod, delete_pod, get_secret_data, in_cluster_namespace, is_pod_completed, list_secrets, pod_exec, wait_for_pod
from walker.repl_state import ReplState
from walker.utils import log2

class PostgresSession:
    def __init__(self, name: str):
        self.name = name
        self.conn_details = None

    def instances(state: ReplState):
        return list_secrets(state.namespace, name_pattern=Config().get('pg.name-pattern', '^{namespace}.*k8spg.*'))

    def run_sql(self, state: ReplState, sql: str):
        if in_cluster_namespace():
            cmd1 = f'env PGPASSWORD={self.password(state)} psql -h {self.endpoint(state)} -p {self.port(state)} -U {self.username(state)} postgres --pset pager=off -c'
            log2(f'{cmd1} "{sql}"')
            cmd = cmd1.split(' ') + [sql]
            subprocess.run(cmd)
        else:
            ns = state.namespace
            image = Config().get('pg.agent.image', 'seanahnsf/kaqing')
            pod_name = Config().get('pg.agent.name', 'kaqing-agent')
            timeout = Config().get('pg.agent.timeout', 3600)

            try:
                create_pod(ns, pod_name, image, None, {'NAMESPACE': state.namespace}, None, None, None, ['sleep', f'{timeout}'], sa_name='c3')
            except Exception as e:
                if e.status == 409:
                    if is_pod_completed(ns, pod_name):
                        try:
                            delete_pod(pod_name, ns)
                            create_pod(ns, pod_name, image, None, {'NAMESPACE': state.namespace}, None, None, None, ['sleep', f'{timeout}'], sa_name='c3')
                        except Exception as e2:
                            log2("Exception when calling BatchV1Api->create_pod: %s\n" % e2)

                            return
                    else:
                            log2(f"Pod {pod_name} already exists.")
                else:
                    log2("Exception when calling BatchV1Api->create_pod: %s\n" % e)

                    return

            wait_for_pod(ns, pod_name)

            cmd = f'PGPASSWORD={self.password(state)} psql -h {self.endpoint(state)} -p {self.port(state)} -U {self.username(state)} postgres --pset pager=off -c "{sql}"'
            pod_exec(pod_name, pod_name, state.namespace, cmd)

    def endpoint(self, state: ReplState):
        if not self.conn_details:
            self.conn_details = get_secret_data(state.namespace, state.pg)

        endpoint_key = Config().get('pg.secret.endpoint-key', 'postgres-db-endpoint')

        return  self.conn_details[endpoint_key]

    def port(self, state: ReplState):
        if not self.conn_details:
            self.conn_details = get_secret_data(state.namespace, state.pg)

        port_key = Config().get('pg.secret.port-key', 'postgres-db-port')

        return  self.conn_details[port_key]

    def username(self, state: ReplState):
        if not self.conn_details:
            self.conn_details = get_secret_data(state.namespace, state.pg)

        username_key = Config().get('pg.secret.username-key', 'postgres-admin-username')

        return  self.conn_details[username_key]

    def password(self, state: ReplState):
        if not self.conn_details:
            self.conn_details = get_secret_data(state.namespace, state.pg)

        password_key = Config().get('pg.secret.password-key', 'postgres-admin-password')

        return  self.conn_details[password_key]

    def db_name(self):
        return Config().get('pg.secret.default-db', 'postgres')