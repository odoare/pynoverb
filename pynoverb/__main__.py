# __main__.py

import sys, argparse
import pynoverb as pbv

def tuple_type(strings):
    strings = strings.replace("(", "").replace(")", "")
    mapped_int = map(int, strings.split(","))
    return tuple(mapped_int)

def main():
    argParser = argparse.ArgumentParser()
#    argParser.add_argument("-h", "--help", help="Print help message")
    argParser.add_argument("-od", "--output-dir", help="Output directory")
    argParser.add_argument("-dt", "--device-type", help="Device type, audio, ni, ps2000 or ps4000")
    argParser.add_argument("-d", "--device", help="Device number (default first present)")
    argParser.add_argument("-in", "--input", type=tuple_type, help="Inputs")
    argParser.add_argument("-out", "--output", type=tuple_type, help="Outputs")
    args = argParser.parse_args()
    print(args)

if __name__ == "__main__":
   main()
