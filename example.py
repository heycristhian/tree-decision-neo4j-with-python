from neo4j import GraphDatabase


class App:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._node_ids = []

    def close(self):
        self._driver.close()

    @property
    def node_ids(self):
        return self._node_ids

    def append_node_ids(self, node_id):
        self._node_ids.append(node_id)

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
        with self._driver.session() as session:
            tree = session.read_transaction(self._find_node_by_id, tree_id)
            self.append_node_ids(tree[0]['id'])
            if tree:
                next_node = tree[0]['next_node']
                node = session.read_transaction(self._find_node_by_id, next_node)
                self.append_node_ids(node[0]['id'])
                return self.decision_path(node[0], facts)
            return None

    def decision_path(self, node, facts):
        with self._driver.session() as session:
            parameter_names = node['parameter_names']

            if node['end_node']:
                self.create_final_query(self.node_ids)
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
            self.append_node_ids(result[0]['id'])
            return self.decision_path(result[0], facts)

    def create_final_query(self, node_ids):
        with self._driver.session() as session:
            quantity_node = len(self.node_ids)
            query = "MATCH "

            for index in range(quantity_node):
                query += f"(n{index}), "

            query = query[:-2] + " WHERE "

            for index in range(quantity_node):
                query += f"n{index}.id = '{node_ids[index]}' AND "

            query = query[:-4] + "RETURN "

            for index in range(quantity_node):
                query += f"n{index}, "

            query = query[:-2]

            print(f'Query: {query}')


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
