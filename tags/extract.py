#!/usr/bin/env python3

import os.path


def extract(name_of_tags):
    source_file = name_of_tags
    dest_file = os.path.join(os.pardir, name_of_tags + ".py")
    f = open(dest_file, "w")
    f.write("{} = {{\n".format(name_of_tags))
    for line in open(source_file):
        fields = line.split("\t")
        f.write("""    "{}": "{}",\n""".format(fields[1], fields[0]))
    f.write("}\n")
    f.close()
    return dest_file


if __name__ == "__main__":

    all_files = ["industrial_tags", "financial_tags", "data_point_tags", "screener_tags", "historical_data_tags"]
    for tag_file in all_files:
        extract(tag_file)
