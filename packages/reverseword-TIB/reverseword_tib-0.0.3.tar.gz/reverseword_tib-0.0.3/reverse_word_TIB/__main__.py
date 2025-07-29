import sys

def reverse_word(word):
    return word[::-1]

def main():
    if len(sys.argv) < 2:
        print("Usage: reverseword <mot>")
        sys.exit(1)

    mot = sys.argv[1]
    print(reverse_word(mot))

if __name__ == "__main__":
    main()
