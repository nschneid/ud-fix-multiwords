#!/usr/bin/env python3

from collections import defaultdict
import sys

from utils import colors



'''
    Utils for reading in UD trees, working with them, and outputting them in CoNLL-U format.
'''


COMMENT_START_CHAR = "#"

class DependencyGraph(object):

    def __init__(self, lines=None, is_enhanced=False):


        root_node = DependencyGraphNode("0", "ROOT")

        self.nodes = {"0": root_node}
        self.edges = set()
        self.outgoingedges = defaultdict(set)
        self.incomingedges = defaultdict(set)
        if not is_enhanced:
            self.enhancedgraph = DependencyGraph(is_enhanced=True)
        else:
            self.enhancedgraph = None
        self.comments = []


        if lines != None:
            self._parse_conllu(lines)


    def _parse_conllu(self, lines):

        #extract nodes
        for line in lines:
            line = line.strip()
            if line.startswith(COMMENT_START_CHAR):
                self.comments.append(line)
                continue

            idx, form, lemma, upos, pos, feats, _, _, deps, misc = line.split("\t")
            node = DependencyGraphNode(idx, form, lemma=lemma, upos=upos, pos=pos,
                                      features=feats, misc=misc, enhanced=deps)
            self.nodes[idx] = node
            self.enhancedgraph.nodes[idx] = node

        #extract edges
        for line in lines:
            line = line.strip()
            if line.startswith(COMMENT_START_CHAR):
                continue

            idx, _, _, _, _, _, gov, reln, enhanceddeps, _ = line.split("\t")


            if gov != "_" and reln != "_":
                self.add_edge(gov, idx, reln)

            if enhanceddeps != "_":
                for dep in enhanceddeps.split("|"):
                    egov, ereln = dep.split(":", 1)
                    self.enhancedgraph.add_edge(egov, idx, ereln)
            else:
                if reln != '_':
                    self.enhancedgraph.add_edge(gov, idx, reln)

    def add_node(self, idx, form, misc='_'):
        node = DependencyGraphNode(idx, form, lemma='_', upos='_', pos='_',
                                  features='_', misc=misc, enhanced='_')
        self.nodes[idx] = node
        self.enhancedgraph.nodes[idx] = node

    def parse_sdp(self, lines):

        predidx2graphidx = []

        #extract nodes
        for line in lines:
            line = line.strip()
            if line.startswith(COMMENT_START_CHAR):
                self.comments.append(line)
                continue

            idx, form, lemma, pos, top, is_pred, _  = line.split("\t", 6)
            node = DependencyGraphNode(idx, form, lemma=lemma, pos=pos)
            self.nodes[idx] = node
            self.enhancedgraph.nodes[idx] = node
            if is_pred == "+":
                predidx2graphidx.append(idx)

        #extract edges
        for line in lines:
            line = line.strip()
            if line.startswith(COMMENT_START_CHAR):
                continue

            deps = line.split("\t")
            idx = deps[0]
            is_root = deps[4] == "+"
            if is_root:
                self.enhancedgraph.add_edge("0", idx, "root")
            deps = deps[7:]
            for predidx, dep in enumerate(deps):
                if dep == "_":
                    continue
                gov = predidx2graphidx[predidx]
                self.enhancedgraph.add_edge(gov, idx, dep)




    def get_gov(self, dep):
        gov_edges = self.incomingedges[dep]
        if len(gov_edges) < 1:
            raise RuntimeError
        for edge in gov_edges:
            gov, reln = edge
            return gov

    def get_gov_reln(self, dep):
        gov_edges = self.incomingedges[dep]
        if len(gov_edges) < 1:
            raise RuntimeError
        for edge in gov_edges:
            gov, reln = edge
            return reln

    def add_edge(self, gov, dep, reln):
        edge = DependencyGraphEdge(gov, dep, reln)
        self.edges.add(edge)
        self.outgoingedges[gov].add((dep, reln))
        self.incomingedges[dep].add((gov, reln))

    def remove_edge(self, gov, dep, reln=None):
        if reln == None:
            to_remove = set()
            for edge in self.edges:
                if edge.gov == gov and edge.dep == dep:
                    to_remove.add(edge)
                    self.outgoingedges[gov].remove((dep, edge.relation))
                    self.incomingedges[dep].remove((gov, edge.relation))
            self.edges.difference_update(to_remove)
        else:
            edge = DependencyGraphEdge(gov, dep, reln)
            self.edges.remove(edge)
            self.outgoingedges[gov].remove((dep, reln))
            self.incomingedges[dep].remove((gov, reln))

    def has_edge(self, gov, dep, reln=None):
        if reln == None:
            for edge in self.edges:
                if edge.gov == gov and edge.dep == dep:
                    return True
        else:
            edge = DependencyGraphEdge(gov, dep, reln)
            return edge in self.edges


    '''
        Returns a list of node indices which are attached to gov via reln.
    '''
    def dependendents_with_reln(self, gov, reln):
        results = []
        for (dep, reln2) in self.outgoingedges[gov]:
            if reln == reln2:
                results.append(dep)
        return results;

    def to_enhanced_string(self, node):
        parents = self.enhancedgraph.incomingedges[node.index]
        if len(parents) < 1:
            return "_"
        else:
            relns = []
            # print(parents)
            # assert False
            parents = sorted(parents, key=lambda x: float(x[0]))
            for (gov, reln) in parents:
                relns.append("%s:%s" % (gov, reln))

            return "|".join(relns)


    def modified_float(self, x):
      # rank 3-4 before 3 before 3
      if '-' in x:
        return float(x.split('-')[0]) - 0.001
      else:
        return float(x)

    def print_conllu(self, f=sys.stdout, highlight=None):
          for comment in self.comments:
              print(comment, file=f)

          for idx in sorted(self.nodes.keys(), key=lambda x: self.modified_float(x)):
              node = self.nodes[idx]
              if idx != "0":
                  parents = self.incomingedges[node.index]
                  gov, reln = next(iter(parents)) if len(parents) > 0 else ("_", "_")
                  enhanced = self.to_enhanced_string(node)

                  col_begin = "" if highlight is None or highlight != node.index else colors.FAIL
                  col_end = "" if highlight is None or highlight != node.index else colors.ENDC # BLACKBACKGROUND


                  print("%s%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s" % (col_begin,
                                                                        node.index,
                                                                        node.form,
                                                                        node.lemma,
                                                                        node.upos,
                                                                        node.pos,
                                                                        node.features,
                                                                        gov,
                                                                        reln,
                                                                        enhanced,
                                                                        node.misc,
                                                                        col_end), file=f)

          print(file=f)



    def compare_stucture(self, other_tree):
        self_edges = sorted(self.edges, key=lambda x: x.dep)
        other_edges = sorted(other_tree.edges, key=lambda x: x.dep)
        differences = []
        for i, self_edge in enumerate(self_edges):
            other_edge = other_edges[i]
            if other_edge.gov != self_edge.gov or other_edge.dep != self_edge.dep:
                differences.append(self_edge.dep)

        return differences

    def compare_reln(self, other_tree):
        self_edges = sorted(self.edges, key=lambda x: x.dep)
        other_edges = sorted(other_tree.edges, key=lambda x: x.dep)
        differences = []
        for i, self_edge in enumerate(self_edges):
            other_edge = other_edges[i]
            if other_edge.relation != self_edge.relation:
                differences.append(self_edge.dep)

        return differences

    def compare_upos(self, other_tree):
        self_nodes = [self.nodes[idx] for idx in sorted(self.nodes.keys(), key=lambda x: float(x)) if "." not in idx]
        other_nodes = [other_tree.nodes[idx] for idx in sorted(other_tree.nodes.keys(), key=lambda x: float(x)) if "." not in idx]
        differences = []
        for i in range(1, len(self_nodes)):
            self_node = self_nodes[i]
            other_node = other_nodes[i]

            if self_node.upos == "_":
                continue

            if other_node.upos == "_":
                continue

            if self_node.upos  !=  other_node.upos:
                differences.append(i)

        return differences



class DependencyGraphNode(object):

    def __init__(self, index, form, lemma="_", upos="_", pos=None, features="_", enhanced=None, misc="_"):
        self.index = index
        self.form = form
        self.lemma = lemma
        self.upos = upos
        self.pos = pos
        self.features = features
        self.misc = misc
        self.enhanced = enhanced

    def __hash__(self):
        return self.index.__hash__() + \
                 self.form.__hash__() + \
                 self.lemma.__hash__() + \
                 self.upos.__hash__() + \
                 self.pos.__hash__() + \
                 self.features.__hash__() + \
                 self.misc.__hash__()

    def __eq__(self, other):
        return self.index == other.index and \
                 self.form == other.form and \
                 self.lemma == other.lemma and \
                 self.upos == other.upos and \
                 self.pos == other.pos and \
                 self.features == other.features and \
                 self.misc == other.misc

    def __str__(self):
        return self.form + "-" + str(self.index)



class DependencyGraphEdge(object):

    def __init__(self, gov, dep, relation):
        self.gov = gov
        self.dep = dep
        self.relation = relation

    def __hash__(self):
        return self.gov.__hash__() + self.dep.__hash__() + self.relation.__hash__()

    def __eq__(self, other):
        return self.gov == other.gov and self.dep == other.dep and self.relation == other.relation

    def __str__(self):
        return "(%s, %s, %s)" % (self.gov, self.dep, self.relation)
