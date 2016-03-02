#!/usr/bin/env python

import sys
import re
import argparse

def initialize_arguments(args):
  """ initilize translator arguments """
  parser = argparse.ArgumentParser(
    description = 'Translators from RTL Names to Gate-Level Names')
  parser.add_argument('--output', type=str, required=True, 
    help="""file: RTL name ===> Gate-level name""")
  parser.add_argument('--match', type=file,  required=True,
    help="""file: Match report from Snopsys formality(generated by 'match' and 'report_match_points' )""")

  """ parse the arguments """
  res = parser.parse_args(args)

  """ return: snapshot file, name matching file, force_reg.ucli, top component name, replay flag """
  return res.output, res.match, 


def read_gate_names(f):
  """ define reference(RTL) name regular expression """
  ref_regex = re.compile(r"""
    Ref\s+                             # is reference(RTL)?
    (DFF|BlPin|Port|BBox|BBPin)\w*\s+  # Type
    (?:[\w\(\)]*)\s                    # Matched by (e.g. name)
    r:/WORK/                           # name prefix
    ([\w/\[\]]*)                       # RTL(chisel) name 
   """, re.VERBOSE)

  """ define implemntation(gate-level designs) name regular expression """
  impl_regex = re.compile(r"""
    Impl\s+                               # is implementation(gate-level design)?
    (?:DFF|BlPin|Port|BBox|BBPin)\w*\s+   # Type
    (?:[\w\(\)]*)\s                       # Matched by (e.g. name)
    i:/WORK/                              # name prefix
    ([\w/\[\]]*)                          # gate-level name
   """, re.VERBOSE)

  ff_regex = re.compile(r"([\w.]*)_reg")
  reg_regex = re.compile(r"([\w.]*)_reg[_\[](\d+)[_\]]")
  mem_regex = re.compile(r"([\w.]*)_reg_(\d+)__(\d+)_")
  sram_regex = re.compile(r"([\w.]*).sram")
  bus_regex = re.compile(r"([\w.]*)[_\[](\d+)[_\]]")

  gate_names = dict()

  try:
    ref_was_matched = False
    ref_name = ""
    ref_idx = -1
    for line in f:
      if ref_was_matched:
        impl_matched = impl_regex.search(line)
        if impl_matched:
          gate_names[ref_name] = impl_matched.group(1).replace("/", ".")
          ref_was_matched = False

      else :
        ref_matched = ref_regex.search(line)
        if ref_matched:
          gate_type = ref_matched.group(1)
          gate_name = ref_matched.group(2)
          gate_name = gate_name.replace("/", ".")
          gate_name = gate_name.replace("[", "_")
          gate_name = gate_name.replace("]", "_")
          if gate_type == "DFF":
            """ D Flip Flops """
            ff_matched = ff_regex.match(gate_name)
            reg_matched = reg_regex.match(gate_name)
            mem_matched = mem_regex.match(gate_name)
            if mem_matched:
              ref_name = mem_matched.group(1) + "[" + mem_matched.group(2) + "]" +\
                   "[" + mem_matched.group(3) + "]"
            elif reg_matched:
              ref_name = reg_matched.group(1) + "[" + reg_matched.group(2) + "]"
            elif ff_matched:
              ref_name = ff_matched.group(1) 

          elif gate_type == "BBox": 
            """ SRAMs """
            sram_matched = sram_regex.search(gate_name)
            if sram_matched:
              ref_name = sram_matched.group(1)
 
          elif gate_type == "BlPin" or gate_type == "BBPin" or gate_type == "Port":
            """ Pins """
            bus_matched = bus_regex.search(gate_name)
            if bus_matched:
              ref_name = bus_matched.group(1) + "[" + bus_matched.group(2) + "]"
            else:
              ref_name = gate_name

          ref_was_matched = True

  finally:
    f.close()

  return gate_names

def write_output(output_file, gate_names):
  f = open(output_file, 'w')
  for ref_name in gate_names:
    f.write("%s %s\n" % (ref_name, gate_names[ref_name]))
  f.close()

  return

if __name__ == '__main__':
  """ parse the arguments and open files """
  output_file, match_file = initialize_arguments(sys.argv[1:])

  """ read gate-level names from the formality match file """
  gate_names = read_gate_names(match_file)

  """ write the output file """
  write_output(output_file, gate_names)
