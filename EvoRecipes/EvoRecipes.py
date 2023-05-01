!pip install rdflib
!pip install pydotplus
!pip install graphviz
!pip install matplotlib

import io
import sys
import pydotplus
import numpy as np
import random
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot
from rdflib.plugins.sparql import prepareQuery
import random
import matplotlib.pyplot as plt
import rdflib
from rdflib import URIRef
from rdflib import Literal

# create a Graph object
g = rdflib.Graph()

# parse the Turtle file and add its contents to the Graph object
g.parse("https://mahgs.com/recipeon", format="turtle")
#g.parse("https://raw.githubusercontent.com/HajiraJabeen/EvoRecipesOntology/main/recipeon.owl", format="turtle")
#g.parse("https://mahgs.com/converter.owl", format="xml")
# define the namespace for the class you're interested in
recipeon = rdflib.Namespace("https://purl.org/net/recipeon#")
owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
seq = rdflib.Namespace("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#")
xml = rdflib.Namespace("http://www.w3.org/XML/1998/namespace")
xsd = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
qudt = rdflib.Namespace("http://qudt.org/2.1/schema/qudt/")
rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
schema = rdflib.Namespace("http://schema.org/")

class Recipe:
  def __init__(self, name,  tree, fitness):
    self.name = name
    self.tree = tree
    self.fitness  = fitness

offSprings = 0

def visualize(theGraph):
  stream = io.StringIO()
  rdf2dot(theGraph, stream, opts = {display})
  dg = pydotplus.graph_from_dot_data(stream.getvalue())
  png = dg.create_png()
  display(Image(png))

# A function that takes recipe root node as input and returns the complete recipe tree in rdf format (i.e. rdflib.Graph)
def getRecipe(recipeName):
  newG=rdflib.Graph()                     # Create a new graph instance to hold the recipe tree
  #newG.bind('recipeon', recipeon)         # Default namespace
                                        # Reads the root node of the recipe
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT (recipeon:"""+recipeName+""" as ?x) ?p ?y WHERE {
      recipeon:"""+recipeName+""" a ?y .
      recipeon:"""+recipeName+""" ?p ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
  
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT (recipeon:"""+recipeName+""" as ?x) (<http://schema.org/name> as ?p) ?y WHERE {
      recipeon:"""+recipeName+""" a <http://schema.org/Recipe> .
      recipeon:"""+recipeName+""" <http://schema.org/name> ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
  
                                        # Reads the Ingredients of the recipe
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT (recipeon:"""+recipeName+""" as ?x) (recipeon:hasIngredient as ?p) ?y WHERE {
      recipeon:"""+recipeName+""" recipeon:hasIngredient ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
  

  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
      recipeon:"""+recipeName+""" recipeon:hasIngredient ?x .
      ?x ?p ?y  .
      ?x <http://schema.org/name>|a ?y .

    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
                                        # Reads the Starting Action of the recipe
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasIngredient ?x .
    ?x recipeon:hasPreparatoryAction|recipeon:hasCookingAction|recipeon:hasPostCookingAction|recipeon:hasAction ?y .
    ?x ?p ?y .
    }"""
                                      
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
                                        # Reads the Names of Starting Action of the recipe 
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasIngredient ?a .
    ?a recipeon:hasPreparatoryAction|recipeon:hasCookingAction|recipeon:hasPostCookingAction|recipeon:hasAction ?x .
    ?x ?p ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
  

                                        # Reads the directly preceding Actions of the recipe
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasIngredient/(recipeon:hasPreparatoryAction|recipeon:hasCookingAction|recipeon:hasPostCookingAction|recipeon:hasAction)/seq:directlyPrecedes* ?y .
    ?x seq:directlyPrecedes ?y .
    ?x ?p ?y  .
    }"""

  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
                                      # Reads the names of the preceding actions of recipe

  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?y ?p ?z WHERE {
    recipeon:"""+recipeName+""" recipeon:hasIngredient/(recipeon:hasPreparatoryAction|recipeon:hasCookingAction|recipeon:hasPostCookingAction|recipeon:hasAction)/seq:directlyPrecedes* ?y .
    ?x seq:directlyPrecedes ?y .
    ?y ?p ?z .
    }"""

  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

  
                                      # Reads the Main/ Side Ingredient
  
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasIngredient ?x .
    ?x recipeon:hasType|<http://schema.org/name> ?y .
    ?x ?p ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

    # To get the procedures
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT (recipeon:"""+recipeName+""" as ?x) (recipeon:hasProcedure as ?p) ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasProcedure ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

    recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasProcedure ?x .
    ?x ?p ?y
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

  # To get the procedure Ingredients
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT ?x (recipeon:hasProcedureIngredient as ?p) ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasProcedure ?x .
    ?x recipeon:hasProcedureIngredient ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
  
  # To get the procedure Actions
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT ?x (recipeon:hasProcedureAction as ?p) ?y WHERE {
    recipeon:"""+recipeName+""" recipeon:hasProcedure ?x .
    ?x recipeon:hasProcedureAction ?y .
    }"""
  
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

  return newG

###   print(  getRecipe("Recipe-9014843").serialize(format="turtle")  )
#A= getRecipe("ROAST-BEEF-DIP-SANDWICH-WITH-HERBED-GARLIC-AU-JUS")
#getRecipe("Quorma")

def getAlternativeIngredient(ing, category):
  query = """
  SELECT ?z
  WHERE {
    ?s a recipeon:"""+category+""" .
    ?s <http://schema.org/name> ?z  .
    recipeon:"""+ing+""" <http://schema.org/name> ?y  .
    FILTER NOT EXISTS{
      ?s <http://schema.org/name> ?y .
      }
    }
    """
  #FILTER(?o = 'Liquids')
  #print(query)
  # execute the SPARQL query and iterate through the results
  results = g.query(query, initNs={"recipeon": recipeon})
  # convert the generator to a list so that it can be indexed
  results_list = list(results)
  #print('Length of results in function is '+str(len(results)))
  if len(results)==0:
    return 'Null'
  # pick a random row from the list
  random_row = random.choice(results_list)
  #print(str(random_row[0].split('#')[-1]))

  #t = rdflib.Graph()

  #for subj,  obj in results:
    #print(f"Subject: {subj}")
    #print(f"Predicate: {pred}")
    #print(f"Object: {obj}")
    #t.add((subj,obj)) 
  #visualize(t)
  #return str({random_row})
  return random_row[0].split('#')[-1]

### ingSubstitution("Alcohol")


def ingredientSubstitution(RecipeA: rdflib.Graph):
  #visualize(RecipeA)
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?y ?z WHERE {
      ?x recipeon:hasIngredient ?y  .
      ?y  a ?z   .
    }"""
  #print(recQry)
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  results_list = list(results)
  #print('length of alternatives is '+str(len(results)))
  # pick a random row from the list
  random_row = random.choice(results_list)
  sub,obj=random_row
  #print(sub,obj)
  #print(  sub.replace('https://purl.org/net/recipeon#','')  , obj.replace('https://purl.org/net/recipeon#','')  )
  alternate = getAlternativeIngredient(sub.replace('https://purl.org/net/recipeon#',''), obj.replace('https://purl.org/net/recipeon#',''))
  #print("The alternative is "+alternate)
  
  if alternate=='Null':
    return Recipe('orig', RecipeA, _fitnessFunction(RecipeA)  )
  
  if (sub.find('+')>0):
      s1 = (sub.split('+'))[0]  + '+'  + str(offSprings)
  else:
      s1  = sub   + '+'  + str(offSprings)
  
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x ?y ?z WHERE {
      VALUES ?x {recipeon:"""+  sub.replace('https://purl.org/net/recipeon#','')  +"""}
      ?x ?y ?z  .
    }"""
  #print(recQry)
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  
  for subj, pred, obj in results:
    if str(pred) ==  "http://schema.org/name":
      #print(  "Out----IF>>>     ", subj  ,  pred  ,  obj  )
      #print(  "In----IF>>>     ", s1  ,  pred  ,  alternate  )
      RecipeA.remove((subj  ,  pred  ,  obj))
      RecipeA.add((sub  ,  pred  ,  Literal(alternate) ) )
    #else:
    #  #print(  "Out----ELSE>>>     ", subj  ,  pred  ,  obj  )
    #  #print(  "In----ELSE>>>     ", s1  ,  pred  ,  obj  )
    #  RecipeA.remove((subj  ,  pred  ,  obj))
    #  RecipeA.add((s1  ,  pred  ,  obj))
    #visualize(RecipeA)
  return Recipe('New Machine Generated Recipe through Ingredient Substitution', RecipeA, _fitnessFunction(RecipeA)  )

#ingredientSubstitution(getRecipe("Recipe-9004025"))

def getAlternativeAction(act, category):
  query = """
  SELECT ?z
  WHERE {
    ?s a recipeon:"""+category+""" .
    ?s <http://schema.org/name> ?z  .
    recipeon:"""+act+""" <http://schema.org/name> ?y  .
    FILTER NOT EXISTS{
      ?s <http://schema.org/name> ?y .
      }
    }
    """
  #FILTER(?o = 'Liquids')
  #print(query)
  # execute the SPARQL query and iterate through the results
  results = g.query(query, initNs={"recipeon": recipeon})
  # convert the generator to a list so that it can be indexed
  results_list = list(results)
  # pick a random row from the list
  random_row = random.choice(results_list)
  #print(str(random_row[0].split('#')[-1]))

  #t = rdflib.Graph()

  #for subj,  obj in results:
    #print(f"Subject: {subj}")
    #print(f"Predicate: {pred}")
    #print(f"Object: {obj}")
    #t.add((subj,obj)) 
  #visualize(t)
  #return str({random_row})
  return random_row[0].split('#')[-1]

def actionSubstitution(RecipeA: rdflib.Graph):
  #visualize(RecipeA)
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?y ?z ?n WHERE {
      ?x seq:directlyPrecedes|recipeon:hasAction|recipeon:hasCookingAction|recipeon:hasPreparatoryAction|recipeon:hasPostCookingAction ?y  .
      ?y  a ?z   .
      ?y  <http://schema.org/name>  ?n  .
    }"""
  #print(recQry)
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  results_list = list(results)
  # pick a random row from the list
  random_row = random.choice(results_list)
  sub,obj,nam=random_row
  #print(  sub.replace('https://purl.org/net/recipeon#','')  , obj.replace('https://purl.org/net/recipeon#',''), nam  )
  alternate = getAlternativeAction(sub.replace('https://purl.org/net/recipeon#',''), obj.replace('https://purl.org/net/recipeon#',''))
  #print("The alternative is "+alternate)



  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x ?y ?z WHERE {
      VALUES ?x {recipeon:"""+  sub.replace('https://purl.org/net/recipeon#','')  +"""}
      ?x ?y ?z  .
    }"""
  #print(recQry)
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  
  for subj, pred, obj in results:
    if str(pred) ==  "http://schema.org/name":
      #print(  "Out----IF>>>     ", subj  ,  pred  ,  obj  )
      #print(  "In----IF>>>     ", s1  ,  pred  ,  alternate  )
      RecipeA.remove((subj  ,  pred  ,  obj))
      RecipeA.add((sub  ,  pred  ,  Literal(alternate) ) )



  #visualize(RecipeA)
  return Recipe('New Machine Generated Recipe through Action Substitution', RecipeA, _fitnessFunction(RecipeA)  )
#actionSubstitution( getRecipe('Recipe-9014958') )

def actionInterchange(  RecipeA: rdflib.Graph ) :
  #visualize(RecipeA)
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x ?y ?z ?w WHERE {
      ?x seq:directlyPrecedes ?y  .
      ?y seq:directlyPrecedes ?z  .
      OPTIONAL {?z seq:directlyPrecedes ?w  .}
      ?y a ?c .
      ?z a ?c .
    } LIMIT 1"""
  #print(recQry)
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for node1, node2, node3, node4 in results:
    #print(f" {node1}"+", "+f"{node2}"+", "+f" {node3}")
    RecipeA.remove((node1, URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes"), node2))
    RecipeA.remove((node2, URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes"), node3))

    RecipeA.add((node1, URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes"), node3))
    RecipeA.add((node3, URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes"), node2))

    RecipeA.remove((node3, URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes"), node4))
    RecipeA.add((node2, URIRef("http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes"), node4))

  #visualize(RecipeA)
  return Recipe('New Machine Generated Recipe through Action Interchange', RecipeA, _fitnessFunction(RecipeA)  )


RecipeA = getRecipe("Recipe-9000274")
RecipeA.bind('recipeon',recipeon)
RecipeA.bind('seq',seq)
RecipeA.bind('schema',schema)
#actionInterchange(RecipeA)
#print(RecipeA.serialize(format="turtle"))

# A function that takes recipe procedure node as input and returns the complete procedure tree in rdf format (i.e. rdflib.Graph)
def getProcedure(procedureName, theRecipe:  rdflib.Graph ):
  #print(  theRecipe.serialize(format="turtle")  )
  #print('Procedure name is' +procedureName)
  newG=rdflib.Graph()                     # Create a new graph instance to hold the recipe tree
  newG.bind(  "recipeon", recipeon )
  newG.bind(  "seq",  seq )
                                          # Reads the root node of the recipe
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT (recipeon:"""+procedureName+""" as ?x) ?p ?y WHERE {
      recipeon:"""+procedureName+""" a ?y .
      recipeon:"""+procedureName+""" ?p ?y .
    }"""
  #print(recQry)
  results = theRecipe.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  #print('I found procedure name '+str(len(results)))
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

                                          # Reads the procedure name
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT (recipeon:"""+procedureName+""" as ?x) (recipeon:hasProcedureName as ?p) ?y WHERE {
      recipeon:"""+procedureName+""" recipeon:hasProcedureName ?y .
    }"""
  
  results = theRecipe.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
                                        # Reads the Ingredients of the procedure
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT (recipeon:"""+procedureName+""" as ?x) (recipeon:hasProcedureIngredient as ?p) ?y WHERE {
      recipeon:"""+procedureName+""" recipeon:hasProcedureIngredient ?y .
    }"""
  
  results = theRecipe.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
                                    # Reads all triplets of ingredients.
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?y ?z WHERE {
      recipeon:"""+procedureName+""" recipeon:hasProcedureIngredient ?x .
      ?x ?y ?z  .
    }"""
    #?x <http://schema.org/name>|recipeon:hasAction|recipeon:hasPreparatoryAction|recipeon:hasCookingAction|recipeon:hasPostCookingAction|recipeon:hasType|a| ?z  .
  
  results = theRecipe.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
                                  # Reads actions of a procedure
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT (recipeon:"""+procedureName+""" as ?x) (recipeon:hasProcedureAction as ?p) ?y WHERE {
      recipeon:"""+procedureName+""" recipeon:hasProcedureAction ?y .
    }"""
  
  results = theRecipe.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))

                                  # Reads all triplets of actions
  recQry = """                          
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT DISTINCT ?x ?p ?y WHERE {
      recipeon:"""+procedureName+""" recipeon:hasProcedureAction ?x .
      ?x ?p ?y  .
    }"""
  #?x seq:directlyPrecedes|<http://schema.org/name>|a ?y  .
  results = theRecipe.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj, pred, obj in results:
    #print(f" {subj}"+", "+f"{pred}"+", "+f" {obj}")
    newG.add((subj,pred,obj))
    
  return newG

############ get Procedure
#print(  getProcedure('Proc-71068').serialize(format="turtle") )

def generateOffspring(  rec: rdflib.Graph,  pro: rdflib.Graph ):
  
  #print(  pro.serialize(format="turtle")  )

  # To get the root node of the recipe
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?x WHERE {
      ?x a <http://schema.org/Recipe> .
      }"""
  results = rec.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    recipeName  = subj
    #print(recipeName)
  
  # To get the root node of the new main procedure
  proQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?x WHERE {
      ?x a recipeon:Procedure .
      }"""
  results = pro.query(proQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    procedureName  = subj
    #print(recipeName[0]+'******************************'+procedureName[0])

  ###############
  rec.add(( URIRef(recipeName[0]),  URIRef("https://purl.org/net/recipeon#hasProcedure"), URIRef(procedureName[0])  ))
  ###############

  # To get the ingredients of the new main procedure
  proQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?y WHERE {
      ?x a recipeon:Procedure .
      ?x recipeon:hasProcedureIngredient ?y .
      }"""
  results = pro.query(proQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    ingredientName  = subj
    #print(ingredientName)
    ###############
    rec.add(( URIRef(recipeName[0]),  URIRef("https://purl.org/net/recipeon#hasIngredient"), URIRef(ingredientName[0])  ))
    ###############
  # To get the new name of the recipe after crossover
  proQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?y WHERE {
      ?x a recipeon:Procedure .
      ?x recipeon:hasProcedureName ?y .
      }"""
  results = pro.query(proQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    MainProName  = subj[0]
    #print(MainProName)

  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?y WHERE {
      ?x a recipeon:Procedure .
      ?x recipeon:hasProcedureName ?y .
      }"""
  results = rec.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    SideProName  = subj[0]
    #print(SideProName)
  
  newRecName  = MainProName+' w\ '+SideProName
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?x (<http://schema.org/name> as ?y) ?z WHERE {
      ?x a <http://schema.org/Recipe> .
      ?x <http://schema.org/name> ?z .
      }"""
  results = rec.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for s,p,o in results:
    #print(s+'  '+p+' '+str(o))
    rec.remove((s,p,o))
    rec.add(( s,  p, Literal(newRecName)  ))

  
  
  rec+=pro
  
  
  
  '''
  for s,p,o in rec:
    #Generating new id for obejct
    if (s.find('+')>0):
      s1 = (s.split('+'))[0]  + '+'  + str(offSprings)
    else:
      s1  = s   + '+'  + str(offSprings)
    #Generating new id for object
    if (o.find('+')>0):
      o1 = (o.split('+'))[0]  + '+'  + str(offSprings)
    else:
      o1=o    + '+'  + str(offSprings)
    rec.add((s1,p,o1))      # Add the triplet with modified ids
    rec.remove((s,p,o))     # Remove the triplet with corrsponding old ids
    '''

  #print(  rec.serialize(format="turtle")  )
  return rec

# A function that initializes the population by creating n recipe trees.
def initialization(category):
  global Population
  Population  = list()
  recQry=""
  if category ==  "Poultry":
    recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x WHERE {
      VALUES ?z {recipeon:Poultry }
      ?x a <http://schema.org/Recipe> .
      ?x recipeon:hasIngredient ?y  .
      ?y a  ?z  .
      ?y recipeon:hasType recipeon:MainIngredient .
    }"""
  if category ==  "Lamb":
    recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x WHERE {
      VALUES ?z {recipeon:Lamb }
      ?x a <http://schema.org/Recipe> .
      ?x recipeon:hasIngredient ?y  .
      ?y a  ?z  .
      ?y recipeon:hasType recipeon:MainIngredient .
    }"""
  if category ==  "Rice":
    recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x WHERE {
      VALUES ?z {recipeon:Rice }
      ?x a <http://schema.org/Recipe> .
      ?x recipeon:hasIngredient ?y  .
      ?y a  ?z  .
      ?y recipeon:hasType recipeon:MainIngredient .
    }"""
  if category ==  "AsianNoodle":
    recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT DISTINCT ?x WHERE {
      VALUES ?z {recipeon:AsianNoodle }
      ?x a <http://schema.org/Recipe> .
      ?x recipeon:hasIngredient ?y  .
      ?y a  ?z  .
      ?y recipeon:hasType recipeon:MainIngredient .
    }"""
  #print('Population size before initialization  '+  str(len(Population))  )
  results = g.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  #thePopulation  =   list()
  for subj in results:
    item  =   subj[0].replace('https://purl.org/net/recipeon#','')
    #print('For Recipe ---->>>>>>>   '+item)
    Population.append(  Recipe( item, getRecipe(item),  0.0 )                )  #_fitnessFunction( getRecipe(item)

  #print('Population size after initialization  '+ str(len(Population))  )
  for recipe in Population:
    recipe.fitness  = _fitnessFunction( recipe.tree )
  #print('Population size after fitness initialization  '+ str(len(Population))  )
    #rec =getRecipe(  subj[0].replace('https://purl.org/net/recipeon/','')  )
    #print (len(rec))
  #return Population
#initialization("Grains")

def pruneOffspring(rec: rdflib.Graph  , pro : rdflib.Graph  ):
  npro  = pro
  nrec  = rec
  # To get the root node of the recipe
  recQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?x WHERE {
      ?x a <http://schema.org/Recipe> .
      }"""
  results = nrec.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    recipeName  = subj
    #print('Heinnnnnnnnnnnnnnnn recipe name is ' + str(recipeName))
  
  recQry = """
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT ?y WHERE {
    ?x recipeon:hasProcedureIngredient ?y .
    }"""
  results = npro.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  #print('Total Procedure Ingredients to be pruned are    '+  str(len(results)))
  for subj in results:
    ingName  = subj
    #print(recipeName[0] + '   procedure ingredient pruned   '  + str(ingName[0]))
    ###############
    npro.add(( URIRef(recipeName[0]),  URIRef("https://purl.org/net/recipeon#hasIngredient"), URIRef(ingName[0])  ))
    ###############
  
  # To get the root node of the new main procedure
  proQry = """
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    SELECT ?x WHERE {
      ?x a recipeon:Procedure .
      }"""
  results = pro.query(proQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    procedureName  = subj
    #print(procedureName[0])
    ###############
    pro.add(( URIRef(recipeName[0]),  URIRef("https://purl.org/net/recipeon#hasProcedure"), URIRef(procedureName[0])  ))
    ###############


  rec-=pro
  return rec

def xover(RecipeA: rdflib.Graph ,  RecipeB: rdflib.Graph):  
  
  recQry = """
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT ?x WHERE {
    ?x recipeon:hasProcedureIngredient ?y .
    ?y recipeon:hasType recipeon:MainIngredient .
    }"""

  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  #print ( len(results) )
  for subj in results:
    #print('Main Procedure Recipe A---->>>>>>>   '+  (     subj[0].split('#')  )[1]     )
    aName = (subj[0].split('#'))[1]
  
  results = RecipeB.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  #print ( len(results) )
  for subj in results:
    #print('Main Procedure Recipe B---->>>>>>>   '+  (     subj[0].split('#'))[1]     )
    bName = (subj[0].split('#'))[1]
  
  ChildA=RecipeA
  ChildB=RecipeB
  MainA = getProcedure(aName, RecipeA)                   #   'Proc-53105'
  #visualize(MainA)
  MainB = getProcedure(bName, RecipeB)                   #   'Proc-71067'

  ChildA.bind("recipeon",recipeon)
  ChildA.bind("seq",seq)
  ChildB.bind("recipeon",recipeon)
  ChildB.bind("seq",seq)

  ChildA  =   pruneOffspring(ChildA,MainA)
  ChildA  =   generateOffspring(ChildA,MainB)
  
  ChildB  =   pruneOffspring(ChildB,MainB)
  ChildB  =   generateOffspring(ChildB,MainA)
  
  #ChildA  = generateOffspring(ChildB,MainA)


  #visualize(ChildA)
  #visualize(ChildB)
  #print(ChildB.serialize(format="turtle"))

  #return ChildA,  ChildB
  return Recipe('New Recipe through xover', ChildA, _fitnessFunction(ChildA)  ),  Recipe('New Recipe through xover', ChildB, _fitnessFunction(ChildB)  )
  

#c1,c2 = xover(  getRecipe("Recipe-9014843"), getRecipe("Recipe-9015983") )

#visualize(getRecipe("Recipe-9014843"))
#visualize(c1.tree)
#visualize(c2.tree)

def uniqueIngredients(RecipeA: rdflib.Graph , RecipeB: rdflib.Graph):
  ingA  = []
  ingB  = []
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  SELECT ?z WHERE {
    ?x  recipeon:hasIngredient  ?y  .
    ?y  <http://schema.org/name>  ?z  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    ingA.append(subj)
    #print('Ingredient>>>>>>>>>>> '+str(subj))
  
  results = RecipeB.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    ingB.append(subj)
  differenceRatio   =   (   len(ingA) - len(list( set(ingA) & set(ingB)  )  )   ) / len(ingA)
  #print ( differenceRatio)
  return  differenceRatio

def _NovelIngredients(RecipeA:  rdflib.Graph):
  uniqueness  = 0.0
  for recipe in Population:
    uniqueness  +=  uniqueIngredients(  RecipeA , recipe.tree  )
  return float(uniqueness / len(Population) )

#print ( "Ingredient Uniqueness Factor is      "   +         str(    _NovelIngredients(  getRecipe( 'Recipe-9014958' )  )    )  )

def uniqueActions(RecipeA: rdflib.Graph , RecipeB: rdflib.Graph):
  actionA  = []
  actionB  = []
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT distinct ?z WHERE {
    ?x  recipeon:hasAction | seq:directlyPrecedes  ?y  .
    ?y  <http://schema.org/name>  ?z  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    actionA.append(subj)
  
  results = RecipeB.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    actionB.append(subj)
  differenceRatio   =   (   len(actionA) - len(list( set(actionA) & set(actionB)  )  )   ) / len(actionA)
  #print ( differenceRatio)
  return  differenceRatio

def _NovelActions(RecipeA:  rdflib.Graph):
  uniqueness  = 0.0
  for recipe in Population:
    uniqueness  +=  uniqueActions(  RecipeA , recipe.tree  )
  return float( uniqueness / len(Population)  )
#print ( "Action Uniqueness Factor is      "   +         str(    _NovelActions(  getRecipe( 'Recipe-9014958' )  )    )  )

def _Novelty(RecipeA: rdflib.Graph):
  ni  = _NovelIngredients(  RecipeA )
  na  = _NovelActions(  RecipeA )
  novel = (ni+na)/2
  return    novel

#_Novelty( getRecipe( 'Recipe-9014958' ) )

def _depth(RecipeA: rdflib.Graph):
  leaves  = []
  RecipeA.bind('recipeon',recipeon)
  RecipeA.bind('seq',seq)
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT distinct ?y WHERE {
    ?x  seq:directlyPrecedes  ?y  .
    FILTER NOT EXISTS{
      ?y    seq:directlyPrecedes ?z
    }    
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    #print ( subj[0].replace('https://purl.org/net/recipeon#','')  )
    leaves.append(  subj[0].replace('https://purl.org/net/recipeon#','')  )
  for leaf in leaves:
    recQry='''
    PREFIX recipeon: <https://purl.org/net/recipeon#>
    PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
    select (count(?a) as ?pLength) WHERE{
      ?r  recipeon:hasIngredient  ?i  .
      ?i  recipeon:hasAction  ?a  .
      ?a  seq:directlyPrecedes*  recipeon:'''+leaf+'''  .
    }
    '''
    #?start (<>|!<>)* ?mid .
    #?mid (<>|!<>)+ ?end .
    #(count(?mid) as ?length)
    #print(recQry)
    results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
    #print(len(results))
    for pl in results:
    #  print (pl[0])
      return int(pl[0])
#_depth( getRecipe( 'Recipe-9014958' ) )
#visualize ( getRecipe( 'Recipe-9000274' )  )
#visualize ( getRecipe( 'Recipe-9014958' )  )

def _Simplicity(RecipeA: rdflib.Graph):
  # Find total number of ingredients
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT (count(?y) as ?ing) WHERE {
    ?x  recipeon:hasIngredient  ?y  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    Ir  =   int(subj[0])
    #print('Ir       '     +     str(Ir) )
  # Find total number of preparatory actions
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT (count(*) as ?act) WHERE {
    VALUES ?y {recipeon:Preparatory recipeon:Apply recipeon:Bend recipeon:Clean recipeon:Coat recipeon:Cut recipeon:Dip recipeon:Lubricate recipeon:MeatSpecific recipeon:Melt recipeon:Mix recipeon:Peel recipeon:Placement recipeon:Refine recipeon:Remove recipeon:Season recipeon:Soak}  
    ?x  a   ?y  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    aPrep  =   int(subj[0])
    #print('aPrep      '     +     str(aPrep)  )
  # Find total number of cooking actions
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT (count(*) as ?act) WHERE {
    VALUES ?y {recipeon:Cooking recipeon:Bake recipeon:Boil recipeon:Burn recipeon:DirectHeat recipeon:Fry recipeon:Microwave recipeon:Scramble}  
    ?x  a   ?y  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    aCook  =   int(subj[0])
    #print('aCook      '     +     str(aCook)  )
  # Find total number of post cooking actions
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT (count(*) as ?act) WHERE {
    VALUES ?y {recipeon:PostCooking recipeon:Cool recipeon:Finish recipeon:Storage}  
    ?x  a   ?y  .
  }'''
  results = RecipeA.query(  recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs} )
  for subj in results:
    aPostCook  =   int(subj[0])
    #print('aPostCook      '     +     str(aPostCook)  )
  d =   int(    _depth(RecipeA)   )
  #factor  =   int(  Ir  +   aCook + aPostCook + aPrep +   d   )
  factor  =   int(  aPrep +   d   )
  #print(    'factor is        '     +     str(  factor  )    )
  return   float( 10 / factor  )
#_Simplicity( getRecipe( 'Recipe-9014958' ) )

def _VisualAppeal(  RecipeA: rdflib.Graph ):
  # Find total number of post cooking actions
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT (count(*) as ?act) WHERE {
    VALUES ?y {recipeon:PostCooking recipeon:Cool recipeon:Finish recipeon:Storage}  
    ?x  a   ?y  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    aPostCook  =   int(subj[0])
    #print('aPostCook      '     +     str(aPostCook)  )
  if aPostCook == 0 :
    return 0.0


  # Find total number of finishing actions
  recQry='''
  PREFIX recipeon: <https://purl.org/net/recipeon#>
  PREFIX seq: <http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#>
  SELECT (count(*) as ?act) WHERE {
    VALUES ?y {recipeon:Finish}  
    ?x  a   ?y  .
  }'''
  results = RecipeA.query(recQry, initNs={"recipeon": recipeon, "owl": owl, "rdf": rdf, "seq": seq, "xml": xml, "xsd": xsd, "qudt": qudt, "rdfs": rdfs})
  for subj in results:
    aFinish  =   int(subj[0])
    #print('aFinish      '     +     str(aFinish)  )
  return  aFinish / aPostCook   #sys.float_info.epsilon  )
#_VisualAppeal(  getRecipe( 'Recipe-9000274' ) )

def _fitnessFunction( RecipeA: rdflib.Graph ):
  return   (    _Novelty( RecipeA ) + _VisualAppeal(  RecipeA ) + _Simplicity ( RecipeA )   )   /3
#_fitnessFunction(  getRecipe( 'Recipe-9000274' ) )

def tournamentSelection():
  #print('length of fahad current population is  '+  str(len(CurrentPopulation))  )
  s1  = random.randint(  0,  len(CurrentPopulation)-1 )
  s2  = random.randint(  0,  len(CurrentPopulation)-1 )
  if CurrentPopulation[s1].fitness  > CurrentPopulation[s1].fitness:
    p1  = s1
  else:
    p1  = s2

  s1  = random.randint(  0,  len(CurrentPopulation)-1 )
  s2  = random.randint(  0,  len(CurrentPopulation)-1 )
  if CurrentPopulation[s1].fitness  > CurrentPopulation[s1].fitness:
    p2  = s1
  else:
    p2  = s2

    #print ('value of p1'  + str(p1)  + 'value of p2'  + str(p2) + 'Population Length    '  +  str ( len(CurrentPopulation)  )  )
  
  return  p1, p2

def getFitness(rec: Recipe):
  return rec.fitness

def roulette_wheel_selection(population):
    # Computes the totallity of the population fitness
    population_fitness = sum([chromosome.fitness for chromosome in population])
    # Computes for each chromosome the probability 
    chromosome_probabilities = [chromosome.fitness/population_fitness for chromosome in population]
    # Selects one chromosome based on the computed probabilities
    return np.random.choice(population, p=chromosome_probabilities)

def GeneticAlgorithm( cr: float, mr:  float, category:  str, generations: int  ):
  print('Initializing!!!')
  initialization(category)
  n = len(Population)
  global CurrentPopulation
  CurrentPopulation   =   Population[0:n]
  global Childs
  Childs=list()
  #for recipe in CurrentPopulation:
    #print('fitness is   '+str(recipe.fitness) )
  #print('length of population is  '+  str(len(Population))      +     '   length of current population is  '+  str(len(CurrentPopulation))    )
  CurrentPopulation.sort(key=getFitness, reverse=True)
  #for recipe in CurrentPopulation:
    #print('modified fitness is   '+str(recipe.fitness)  )
  global avgFitness,  avgNovelty,   avgVisual, avgComplexity
  avgFitness  = list()
  avgNovelty  = list()
  avgComplexity  = list()
  avgVisual  = list()
  crossovers: int  = round( cr  * n )
  mutations:  int   = round(  mr  * n  )
  #print(  str(crossovers) + "      "  + str(mutations) )
  for i in range(generations):
    avgFitness.append( sum([recipe.fitness for recipe in CurrentPopulation]) / n  )
    avgNovelty.append( sum([_Novelty(recipe.tree) for recipe in CurrentPopulation]) / n  )
    avgComplexity.append( sum([_Simplicity(recipe.tree) for recipe in CurrentPopulation]) / n  )
    avgVisual.append( sum([_VisualAppeal(recipe.tree) for recipe in CurrentPopulation]) / n  )
    print('>>>>>>>>>>>>>>>>>> Generation  '+  str(i))
    Childs=list()
    k=0
    print('Crossovers!!!')
    for j in range(crossovers):
      p1,p2 = tournamentSelection()
      #print('p1 is '+str(p1)+'         p2 is '+str(p2))
      #xover(  getRecipe(currentPopulation[ random.randint(0,n-1) ]), getRecipe(currentPopulation[ random.randint(0,n-1) ]) )  #Select Randomly
      o1,o2 = xover(  CurrentPopulation[p1].tree  , CurrentPopulation[p1].tree )  #Select Randomly
      CurrentPopulation[p1] = o1
      CurrentPopulation[p2] = o2

      #Childs.append( o1  )
      #Childs.append( o2  )
      k+=1
      #print(  "Completed Crossover" +  str(k) )
    k=0
    print('Mutations!!!')
    for recipe in CurrentPopulation:
      #print('The curent iteration is '+ str(j) )
      # Randomly select a recipe for mutation
      #selRecipe = getRecipe(currentPopulation[ random.randint(0,n-1) ])
      # Randomly select mutation function
      r = random.randint(0,1)
      if r  ==  0  :
        CurrentPopulation.append(    ingredientSubstitution( recipe.tree )      )
        CurrentPopulation.remove(recipe)
      if  r ==  1  :
        CurrentPopulation.append(    actionSubstitution(recipe.tree)  )
        CurrentPopulation.remove(recipe)
        #CurrentPopulation.remove(    recipe      )
     # if  r ==  2  :
      #  Childs.append(   actionInterchange(recipe.tree)    )
        #CurrentPopulation.remove(    recipe      )
      k+=1
      #print ( 'Completed mutation' + str(k) )
    TempPopulation  = list()
    CurrentPopulation = CurrentPopulation + Childs[:]
    #CurrentPopulation.sort(key=getFitness, reverse=True)
    #CurrentPopulation = CurrentPopulation[0:n]
    for item in range(n):
      TempPopulation.append(  roulette_wheel_selection(CurrentPopulation)   )
    CurrentPopulation = TempPopulation[0:n]
    #print('modified current population size is '+str(len(CurrentPopulation)))
    
#GeneticAlgorithm(0.5, 0.5, "Poultry", 35)
#GeneticAlgorithm(0.5, 0.5, "Lamb", 35)
#GeneticAlgorithm(0.5, 0.5, "Rice", 35)
GeneticAlgorithm(0.5, 0.5, "AsianNoodle", 35)

for recipe in CurrentPopulation:
    print('fitness is   '+str(recipe.fitness) )

#visualize(CurrentPopulation[4].tree)
for fitn in avgFitness:
 print(fitn)
for fitn in avgNovelty:
 print(fitn)
for fitn in avgComplexity:
  print(fitn)
for fitn in avgVisual:
  print(fitn)

#print (   CurrentPopulation[4].tree.serialize(format="turtle")    )
Gens  = list( range (1,36,1) )
print(str(len(avgFitness))+  '         ' + str(len(Gens)))
plt.plot( Gens, avgFitness, color='green', label="Average Fitness")
plt.plot( Gens, avgNovelty , color='orange', label="Average Novelty")
plt.plot( Gens, avgComplexity, color='red', label="Average Complexity")
plt.plot( Gens, avgVisual, color='blue', label="Average Visual Appeal")
#plt.title('Average Fitness of Population across generations')
plt.xlabel('Generations')
plt.ylabel('Average Fitness')
#plt.legend(["Avg Fitness", "Avg Novelty", "Avg Simplicity", "Avg Visual Appeal"], loc ="upper center")
plt.legend(bbox_to_anchor=(1.02, 0.6), loc='upper left', borderaxespad=0)
plt.figure(figsize=(20,3))
plt.show()

#print(  getRecipe("Recipe-31001516").serialize(format="turtle")  )
#visualize(CurrentPopulation[4].tree)
for recipe in CurrentPopulation:
  print(recipe.tree.serialize(format="turtle"))

print(  CurrentPopulation[0].tree.serialize(format="turtle"))
