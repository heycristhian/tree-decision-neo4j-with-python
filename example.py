from neo4j import GraphDatabase


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.node = {}

    def close(self):
        self.driver.close()

    @staticmethod
    def _find_node_by_id(tx, id):
        query = (
            'MATCH (n) '
            'WHERE n.id = $id '
            'return n'
        )
        result = tx.run(query, id=id)
        result = [record['n'] for record in result]
        return result

    def execute_decision_tree(self, tree_id, facts):
        with self.driver.session() as session:
            tree = session.read_transaction(self._find_node_by_id, tree_id)
            if tree:
                next_node = tree[0]['next_node']
                node = session.read_transaction(self._find_node_by_id, next_node)
                return self.decision_path(node[0], facts)
            return None

    def decision_path(self, node, facts):
        with self.driver.session() as session:
            parameter_names = node['parameter_names']

            if node['end_node']:
                return node['response']

            for param in parameter_names:
                temp = param
                vars()[temp] = facts[param]

            if eval(node['expression']):
                id_node = node['node_when_true']
            else:
                id_node = node['node_when_false']

            result = session.read_transaction(self._find_node_by_id, id_node)
            result = [record for record in result]
            return self.decision_path(result[0], facts)


def bar_test():
    parameters = {
        'gender': 'female',
        'age': 20
    }
    result = app.execute_decision_tree('bar entrance', parameters)
    return result


def venda_test():
    parameters = {
        'qtde': 31
    }
    result = app.execute_decision_tree('venda_nova', parameters)
    return result


if __name__ == "__main__":
    scheme = "bolt"
    host_name = "localhost"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "4321"
    app = App(url, user, password)
    # response = bar_test()
    response = venda_test()
    print(f'Result is: {response}')
    app.close()
