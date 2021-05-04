from anytree import AnyNode, RenderTree, PreOrderIter
from anytree.exporter import JsonExporter

from flask import Flask, request, abort
from flask_restful import Api, Resource

import json

exporter = JsonExporter()

# Data generation
def load_data(data):
  root = AnyNode(validators=[None],name=None)
  for ligne in data:
      active_node = root
      for letter in ligne.split("."):
          need_new_node = True
          if active_node.children is not tuple(): # if node have a child
            for child in active_node.children:
              if child.name == letter: # if this child already exist don't create node
                need_new_node = False
                active_node = child
                break
              
          if need_new_node: # create node if needed
            new_node=AnyNode(name=str(letter), validators=None,parent=active_node)
            active_node = new_node

      # set validator
      node_json_type = data[ligne].split('|')
      if len(node_json_type)  == 2 and node_json_type[0] == "object": # if key:value value is "object"
        for key in node_json_type[1].split(':')[1].split(","):  # for each key add node
          AnyNode(name=str(key), validators=None,parent=active_node)
        active_node.validators = ["object"]
      else:
        active_node.validators = node_json_type

  # All node_json parsed to tree

  for node in PreOrderIter(root):
    for n in node.children:
      if not n.is_leaf and (n.validators is None or "array" in n.validators): # change validator for array and not set validator
        if n.children[0].name == "*": 
          n.validators = ["array"]
          n.children[0].name = "items"
          n.children[0].validators = ["object"]
        else:
          n.validators = ["object"]

    # set type
    if node.is_leaf:
      node.type = 'leaf'
    else:
      node.type = node.validators[0]
  
  return root

def dump_tree(node):
  node_data = json.loads(exporter.export(node))
  node_json = None
  child_node_json = {}
  if not node.is_leaf: # add child node inside
    for n in node.children: 
      child_node_json[n.name] = None
      child_node_json.update(dump_tree(n))
      if node_data["type"] == "array":
        node_json = {node_data["name"]:{"type" : node_data["type"],"validators" : node_data["validators"] or []}}
        node_json[node_data["name"]].update(child_node_json)
      elif node_data["type"] == "object":
        node_json = {node_data["name"]:{"type" : node_data["type"],"validators" : node_data["validators"] or [],"properties":child_node_json}}
      else:
        node_json = {node_data["name"]:{"type" : node_data["type"],"validators" : node_data["validators"] or []}}
  else:
    node_json = {node_data["name"]:{"type" : node_data["type"],"validators" : node_data["validators"] or []}}
  return node_json

def creation_json(root):
  node_json = {}
  for child in root.children:
    node_json.update(dump_tree(child))

  return node_json

#API
app = Flask(__name__)
api = Api(app)

class ExpandValidator(Resource):
    def post(self):

      request_content = request.get_json(force=True)
      if request_content is None:
        abort(422)

      return creation_json(load_data(request_content)), 200

api.add_resource(ExpandValidator,'/expand_validator')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)