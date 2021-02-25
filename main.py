from db.connection import connect
from util.queries import bradesco_portabilidade

session = connect()

query_delete = """
MATCH (n) DETACH DELETE n
"""

query1 = """
CREATE (tree:Tree { id: 'bar entrance' })
CREATE (over21_rule:Rule { name: 'Over 21?', parameter_names: 'age', parameter_types:'int', expression:'age >= 21' })
CREATE (gender_rule:Rule { name: 'Over 18 and female', parameter_names: 'age,gender', parameter_types:'int,String', expression:'(age >= 18) && gender.equals(\\"female\\")' })
CREATE (answer_yes:Answer { id: 'yes'})
CREATE (answer_no:Answer { id: 'no'})
CREATE (tree)-[:HAS]->(over21_rule)
CREATE (over21_rule)-[:IS_TRUE]->(answer_yes)
CREATE (over21_rule)-[:IS_FALSE]->(gender_rule)
CREATE (gender_rule)-[:IS_TRUE]->(answer_yes)
CREATE (gender_rule)-[:IS_FALSE]->(answer_no)
"""

query_ccg = """
CREATE (tree:Tree { id: 'venda_nova' , next_node: 'quantidade_vidas', relationships: ['HAS']})

CREATE (quantidade_vidas:Rule { id: 'quantidade_vidas', name: 'Quantidade de vidas?', parameter_names: 'qtde', 
expression:'qtde >= 30', end_node: false, node_when_true: 'true', node_when_false: 'false'})

CREATE (answer_true:Answer { id: 'true', end_node: true, response: 'é maior ou igual que 30'})
CREATE (answer_false:Answer { id: 'false', end_node: true, response: 'é menor que 30'})
CREATE (tree)-[:HAS]->(quantidade_vidas)
CREATE (quantidade_vidas)-[:IS_TRUE]->(answer_true)
CREATE (quantidade_vidas)-[:IS_FALSE]->(answer_false)
"""

query_example = """
MATCH (n) RETURN n
"""
session.run(query_ccg)

