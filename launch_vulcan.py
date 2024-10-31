from argparse import ArgumentParser


from vulcan.server_launcher import launch_server_from_file


def main():
    parser = ArgumentParser()
    parser.add_argument("pickle_filename", help="Path to the pickle file you want to visualize. You can specify"
                                                "a JSON file instead if you use the --json flag.")
    parser.add_argument("-pf", "--propbank-frames", type=str,
                        action="store", dest="propbank_frames", default=None,
                        help="Path to a folder containing XML files with Propbank frames, "
                             "such as data/frames/propbank-amr-frames-xml-2018-01-25 in the AMR3.0 corpus. "
                             "If given, vulcan will show frame definitions on node mouseover (only works for "
                             "propbank frames; designed to be used with AMR graphs)")
    parser.add_argument("-wiki", "--show-wikipedia-articles", action="store_true", dest="show_wikipedia_articles",
                        default=False, help="If given, vulcan will show Wikipedia articles for AMR graphs on node mouseover."
                                            "Can take quite a while to load in the beginning!")
    parser.add_argument("-p", "--port", type=int, action="store", dest="port", default=5050,
                        help="Specify the port to use for this visualization.")
    parser.add_argument("-a", "--address", action="store", dest="address", default="localhost",
                        help="""Specify the address to use for this visualization. Use localhost (default) if you want to
                                access the visualization only from your own computer. For hosting vulcan on a server,
                        specifics may differ, but 0.0.0.0 may be a good place to start.""")
    parser.add_argument("--json", action="store_true", dest="is_json_file", default=False,
                        help="Use this flag if your input file is a JSON file rather than a pickle.")
    parser.add_argument("--show-node-names", action="store_true", dest="show_node_names", default=False,
                        help="A graph or tree node with name `n` and label `label` will be shown as"
                             " `n / label` (per default, only `label` is shown).")
    args = parser.parse_args()

    if args.propbank_frames is not None:
        propbank_path = args.propbank_frames + "/"
    else:
        propbank_path = None

    launch_server_from_file(args.pickle_filename, port=args.port, address=args.address, is_json_file=args.is_json_file,
                            show_node_names=args.show_node_names, propbank_path=propbank_path,
                            show_wikipedia_articles=args.show_wikipedia_articles)


if __name__ == '__main__':
    main()
