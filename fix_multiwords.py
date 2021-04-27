"""
Used to explore + fix multiword tokens (MWTs).

October 2020: Ethan Chi (ethanchi@cs.stanford.edu)
April 2021: Nathan Schneider (nathan.schneider@georgetown.edu)
  - revised to better handle MWTs adjacent to punctuation,
    to add CorrectSpaceAfter=Yes for missing spaces that are spelling errors, etc.
  - new CLI: single .conllu file arg. The modified file will be created with
    a .out extension and then will replace the original.
"""

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
manual_review = []  # the above cases (SpaceAfter=No at end of sentence) are now handled automatically


# puncts = ['.', ',', '!', ';', '"', ')', '?', '$', '0', '*', '(',
#           '&', '-', ':', '/', '<', '>', '…', '“', '”', '@', '[', ']']

#globals because we are not clean coders

# known_correct_suffixes = ["'ll", "'d", "n't", "s", "'s", "'re", "'ve"]

COLLOQUIAL_CONTRACTIONS = {'wanna', 'gotta', 'gonna', 'cannot', 'awhile', 'sorta', "c'mon", 'dunno', 'outta'}

guaranteed_correct = 0
possibly_correct = 0
form_dict = defaultdict(int)

def no_error_int(val):
  try:
    return int(val)
  except ValueError as err:
    if '.' in val or '-' in val: return 0
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
  while i < end:    # changed <= to < to keep SpaceAfter=No on the last word of the sentence (these were formerly manual_review sentences: see above)
    first = graph.nodes[str(i)]
    if 'SpaceAfter' not in first.misc or first.upos in ('PUNCT', 'SYM', 'NUM') or first.form in ('/', '&') or (first.lemma=='with' and first.form.lower()=='w/'): # or 'goeswith' in first.enhanced:
      i += 1
      continue

    span_end = i + 1   # first to not be SpaceAfter=no
    forms = [first.form]
    lemmas = [first.lemma]
    poses = [first.upos]
    misc_orig = [first.misc]
    candidate_mwt_nodes = [first]

    mwt_misc = '_'

    n = graph.nodes[str(span_end)]  # for the condition upon entry into the loop (walrus would be better)
    while span_end < end and 'SpaceAfter' in n.misc and n.upos not in ('PUNCT', 'SYM', 'NUM') and n.form not in ('/', '&') and 'goeswith' not in n.enhanced:
      forms.append(n.form)
      lemmas.append(n.lemma)
      poses.append(n.upos)
      misc_orig.append(n.misc)
      candidate_mwt_nodes.append(n)
      assert n.misc=='SpaceAfter=No',n.misc
      n.misc = '_'
      span_end += 1
      n = graph.nodes[str(span_end)]

    try:
        lastnode = graph.nodes[str(span_end)]
        if lastnode.upos not in ('PUNCT', 'SYM', 'NUM', 'DET') and lastnode.form not in ('/', '&') and 'goeswith' not in lastnode.enhanced:
            forms.append(lastnode.form)
            lemmas.append(lastnode.lemma)
            poses.append(lastnode.upos)
            misc_orig.append(lastnode.misc)
            candidate_mwt_nodes.append(lastnode)
            assert lastnode.misc=='_',(lastnode.misc,forms)
            #lastnode.misc = '_'
        else:
            span_end -= 1
            mwt_misc = 'SpaceAfter=No'
            if lastnode.upos=='DET':    # e.g. "is n't a"
                mwt_misc += '|CorrectSpaceAfter=Yes'

    except KeyError as err:
      graph.print_conllu()
      raise err

    # if ((not any(any(punct in form for punct in puncts) for form in forms)) and
    #     (not any(fuzzy_match(form, "'") for form in forms))):
    #   if (len(forms) == 2 and any(fuzzy_match(forms[-1], sfx) for sfx in known_correct_suffixes) or
    #        or
    #       fuzzy_match(''.join(forms), "i'm")):
    #    guaranteed_correct += 1
    if len(forms)>1:
        if any(p=='X' for p in poses):
            assert forms[0]=='Inter-',forms # spacial case: Inter-Services where Inter- is tagged as X
        if (poses[-1] in ('PART', 'AUX') or (poses[-1]=='VERB' and lemmas[-1]=='be' and forms[-1]=="'s")
            or ''.join(forms).lower() in COLLOQUIAL_CONTRACTIONS or forms[0].lower()=="d'"
            or any(p=='X' for p in poses)):
            pass    # +MWT, -err # These are standard contractions, not errors. (Note that annotation of 'awhile' is inconsistent.)
            # Create MWT
            assert first.misc=='SpaceAfter=No' or first.misc.endswith('|SpaceAfter=No'),first.misc
            first.misc = first.misc.replace('|SpaceAfter=No','').replace('SpaceAfter=No','_')
            graph.add_node(idx=str(i) + '-' + str(span_end), form=''.join(forms), misc=mwt_misc)
        else:   # Actually don't create an MWT

            if all(p=='PROPN' for p in poses) and all(f.endswith('.') for f in forms):
                # -MWT, -err # OK to omit space between initials in a name, e.g. "R.E. Glenn"
                # Restore the original MISC annotations
                for i in range(len(candidate_mwt_nodes)):
                    candidate_mwt_nodes[i].misc = misc_orig[i]
            else:   # Missing space: add CorrectSpaceAfter=Yes
                # -MWT, +err
                # Note: some space conventions are arguable: sometime, anymore, everyday, :sadface:
                # These count as spelling errors if annotated as 2 words.
                # Restore the original MISC annotations
                for i in range(len(candidate_mwt_nodes)):
                    m = misc_orig[i]
                    candidate_mwt_nodes[i].misc = m + '|CorrectSpaceAfter=Yes' if i<len(candidate_mwt_nodes)-1 else m
                print(' '.join(forms), ' '.join(poses))




    i = span_end + 1
        # graph.print_conllu(highlight=i)
        # possibly_correct += 1





#def load_graphs_from_file(base_path, filename):
def load_graphs_from_file(filename):
    read_filename = filename
    out_filename = read_filename+'.out'
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

    # print("Guaranteed correct:", guaranteed_correct)
    # print("Others:", possibly_correct)
    # print(form_dict)

#load_for_all_in_directory(sys.argv[1])

load_graphs_from_file(sys.argv[1])
