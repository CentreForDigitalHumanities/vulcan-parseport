import sys

from penman import load, encode

from vulcan.pickle_builder.pickle_builder import PickleBuilder


def main():
    little_prince_path = sys.argv[1]
    output_path = sys.argv[2]
    amrs = load(little_prince_path)

    pb = PickleBuilder({"Graph": "graph_string", "Sentence": "string"})
    for amr in amrs:
        sentence = amr.metadata["snt"]
        amr_string = encode(amr)
        pb.add_instance_by_name("Graph", amr_string)
        pb.add_instance_by_name("Sentence", sentence)

    pb.write_as_json(output_path)


if __name__ == "__main__":
    main()
