import sys

from . import expand

def main():
  for filepath in sys.argv[1:]:
    expand.process_file(filepath)
  

if __name__ == '__main__':
  main()
