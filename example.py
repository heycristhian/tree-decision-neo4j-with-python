import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.node = {}


    def close(self):
        self.driver.close()

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_friendship, person1_name, person2_name)
            for record in result:
                print("Created friendship between: {p1}, {p2}".format(
                    p1=record['p1'], p2=record['p2']))

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        print('result')
        for record in result:
            print(record)
        try:
            return [{"p1": record["p1"]["name"], "p2": record["p2"]["name"]}
                    for record in result]

        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            for record in result:
                print("Found person: {record}".format(record=record))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [record["name"] for record in result]

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

    def execute_decision_tree(self, id, number):
        with self.driver.session() as session:
            tree = session.read_transaction(self._find_node_by_id, id)
            if tree:
                next_node = tree[0]['next_node']
                node = session.read_transaction(self._find_node_by_id, next_node)
                return self.decision_path(node[0], number)
            return None

    def decision_path(self, node, qtde):
        with self.driver.session() as session:
            if node['end_node']:
                return node['response']
            if eval(node['expression']):
                id_node = node['node_when_true']
            else:
                id_node = node['node_when_false']

            result = session.read_transaction(self._find_node_by_id, id_node)
            result = [record for record in result]

            return self.decision_path(result[0], qtde)

    @staticmethod
    def _get_nodes(tx):
        venda_nova = 'venda_nova'
        quantidade_vidas = '$quantidade_vidas'

        query = """
            MATCH (tree:Tree)-[r:HAS]->(rule:Rule)
            WHERE tree.id = 'venda_nova' AND rule.id = 'quantidade_vidas'
            return tree, rule, r
        """

        result = tx.run(query, venda_nova=venda_nova, quantidade_vidas=quantidade_vidas)
        print('_get_nodes')
        print(type(result))
        result = [record for record in result]
        return result[0]

    def decision_answer(self, tree, args):
        with self.driver.session() as session:
            pass


if __name__ == "__main__":
    scheme = "bolt"
    host_name = "localhost"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "4321"
    app = App(url, user, password)
    # app.create_friendship("Alice", "David")
    app.find_person("Alice")
    response = app.execute_decision_tree('venda_nova', 10)
    print(f'Result is: {response}')
    app.close()
