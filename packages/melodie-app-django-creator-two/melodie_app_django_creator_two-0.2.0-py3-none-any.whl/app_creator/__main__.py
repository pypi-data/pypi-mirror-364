from .core import main

if __name__ == '__main__':
    main()
    yy
if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
    sys.argv.insert(1, "create")
