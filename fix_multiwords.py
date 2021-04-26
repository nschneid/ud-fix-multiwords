# Used to explore + fix multiwords.
# October 2020: Ethan Chi (ethanchi@cs.stanford.edu)
# April 2021: Nathan Schneider (nathan.schneider@georgetown.edu)

import os
import sys
import io

from collections import defaultdict

from depgraph_utils import *

manual_review = ['answers-20111108101827AALT6Zq_ans-0022', #SA=no at EOS
                 'answers-20111108092029AAsHTYP_ans-0002', #SA=no at EOS
                 'email-enronsent07_01-0023',
                 'email-enronsent28_01-p0012',
                 'email-enronsent01_01-0043',
                 'email-enronsent28_02-0033',
                 'newsgroup-groups.google.com_humanities.lit.authors.shakespeare_0018a7697318f71f_ENG_20031006_163200-0090',
                 'newsgroup-groups.google.com_Meditation20052_06390a5f75b2e1f2_ENG_20050316_091700-0040',
                 'reviews-243799-0005']

puncts = ['.', ',', '!', ';', '"', ')', '?', '$', '0', '*', '(',
          '&', '-', ':', '/', '<', '>', '…', '“', '”', '@', '[', ']']

#globals because we are not clean coders

known_correct_suffixes = ["'ll", "'d", "n't", "s", "'s", "'re", "'ve"]

guaranteed_correct = 0
possibly_correct = 0
form_dict = defaultdict(int)

def no_error_int(val):
  try:
    return int(val)
  except ValueError as err:
    if '.' in val: return 0
    raise err

def fuzzy_match(string, comparison):
  string = string.lower()
  if string == comparison: return True
  if string == comparison.replace("'", "’"): return True
  if string == comparison.replace("'", "‘"): return True
  if string == comparison.replace("'", ""): return True
  if string == comparison.replace("'", "`"): return True
  return False

def fix_multiwords(graph, filename):
  global guaranteed_correct, possibly_correct, form_dict
  i = 0
  end = max([no_error_int(key) for key in graph.nodes.keys()])
  while i <= end:
    first = graph.nodes[str(i)]
    if 'SpaceAfter' not in first.misc:
      i += 1
      continue

    span_end = i + 1   # first to not be SpaceAfter=no
    forms = [first.form]

    while span_end < end and 'SpaceAfter' in graph.nodes[str(span_end)].misc:
      forms.append(graph.nodes[str(span_end)].form)
      span_end += 1

    try:
      forms.append(graph.nodes[str(span_end)].form)
    except KeyError as err:
      graph.print_conllu()
      raise err

    if ((not any(any(punct in form for punct in puncts) for form in forms)) and
        (not any(fuzzy_match(form, "'") for form in forms))):
      if (len(forms) == 2 and any(fuzzy_match(forms[-1], sfx) for sfx in known_correct_suffixes) or
          ''.join(forms) in ('wanna', 'gotta', 'cannot', 'awhile', 'sorta') or
          fuzzy_match(''.join(forms), "i'm")):
        guaranteed_correct += 1
        graph.add_node(idx=str(i) + '-' + str(span_end), form=''.join(forms))
        # graph.print_conllu()
        print(len(forms), forms)

        if len(forms) > 2:
          assert False
      else:
        # print(len(forms), forms)
        # graph.print_conllu()

        possibly_correct += 1

      form_dict[len(forms)] += 1

    i = span_end + 1
        # graph.print_conllu(highlight=i)
        # possibly_correct += 1





def load_graphs_from_file(base_path, filename):
    read_filename = os.path.join(base_path, filename)
    out_filename = os.path.join('/u/scr/ethanchi/tmp', filename)
    lines = []

    with open(read_filename, 'r') as f:
        with open(out_filename, 'w') as fout:
            for line in f:
                if line.strip() == "":
                    if len(lines) > 0:
                        graph = DependencyGraph(lines=lines)
                        if lines[0].split()[-1] in manual_review or lines[1].split()[-1] in manual_review:
                            print("Skipping for manual review:" + lines[0].strip())
                        else:
                            fix_multiwords(graph, filename)
                        graph.print_conllu(f=fout)
                    lines.clear()
                else:
                    lines.append(line)

    os.replace(out_filename, read_filename)

def load_for_all_in_directory(filepath):
    files = os.listdir(filepath)
    for filename in files:
        load_graphs_from_file(filepath, filename)

    print("Guaranteed correct:", guaranteed_correct)
    print("Others:", possibly_correct)
    print(form_dict)

load_for_all_in_directory(sys.argv[1])
