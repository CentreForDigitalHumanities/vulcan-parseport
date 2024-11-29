import sys

from penman import load, encode

from vulcan.pickle_builder.pickle_builder import PickleBuilder


def main():
    little_prince_path = sys.argv[1]
    output_path = sys.argv[2]
    amrs = load(little_prince_path)

    pb = PickleBuilder({"Graph": "graph", "Sentence": "string"})
    for amr in amrs:
        sentence = amr.metadata["snt"]
        pb.add_instance_by_name("Graph", amr)
        pb.add_instance_by_name("Sentence", sentence)

    pb.write(output_path)


if __name__ == "__main__":
    main()
