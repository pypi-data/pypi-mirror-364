# 'init' subcommand: get user's preferences and write config file

import sys
import os
import importlib.metadata
import re
import logging
from . import ncbi_helper
from . import config


def get_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        sys.exit(1)


def prompt_int_choice(prompt, min_value=1, max_value=None):
    """Get an integer choice from the user, with optional min and max values.
    min_value will be presented as default in case of empty input."""
    while True:
        try:
            choice = get_input(f"{prompt} [{min_value}]: ")
            choice = int(choice) if choice else min_value
            if min_value <= choice and (max_value is None or choice <= max_value):
                return choice
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            if (re.match(r"^[Qq](uit)?", choice)):
                print("Exiting...")
                sys.exit(0)
            print("Invalid input. Please enter a number.")


def prompt_taxonomy_id(ncbi, species_name):
    """Prompt the user to select a Taxonomy ID from the list of matches for a given species name."""
    matches = ncbi.get_taxonomy_entries('"' + species_name + '"')
    if matches:
        print(f"\nFound the following Taxonomy IDs for '{species_name}':")
        for idx, entry in enumerate(matches):
            print(f"{idx+1}. {entry['sci_name']} (Taxonomy ID: {entry['tax_id']})")
        choice = prompt_int_choice("Select the correct species by number", 1, len(matches))
        return matches[choice-1]["tax_id"]
    else:
        print(f"\nNo matches found for '{species_name}'.")
        sys.exit(1)


def prompt_refseq_id(ncbi, taxid):
    """Prompt the user to select a RefSeq ID from the list of available IDs for a given Taxonomy ID."""
    refseq_entries = ncbi.get_refseqs_for_taxid(taxid)
    if refseq_entries:
        print(f"\nFound the following RefSeq IDs for Taxonomy ID {taxid}:")
        for idx, r in enumerate(refseq_entries):
            label = f"{r['accession']}: {r['title']}"
            if (r["strain"] and r["strain"] != "No strain"):
                label += f" ({r['strain']})"
            print(f"{idx+1}. {label}")
        choice = prompt_int_choice("Select the correct RefSeq ID by number", 1, len(refseq_entries))
        return refseq_entries[choice-1]['accession']
    else:
        print(f"\nNo RefSeq IDs found for Taxonomy ID {taxid}.")
        sys.exit(1)


def check_proportion(proportion):
    """Make sure the given value, while a string value, converts to a float between 0 and 1.  Empty/None is okay."""
    if proportion:
        try:
            value = float(proportion)
        except ValueError:
            return False, f"Sorry, need a value between 0 and 1, '{proportion}' doesn't parse"
        if value < 0:
            return False, "Sorry, need a value between 0 and 1, not a negative number"
        if value > 1.0:
            return False, f"Sorry, need a value between 0 and 1, {proportion} is too large"
    return True, None


def check_optional_file_readable(filename):
    """If filename is empty, that's fine; if non-empty, make sure it's a readable file"""
    if filename:
        if not os.path.exists(filename):
            return False, f"Sorry, file '{filename}' does not exist"
        if not os.path.isfile(filename):
            return False, f"Sorry, file '{filename}' does not appear to be a regular file"
        else:
            try:
                f = open(filename, "r")
                f.close()
            except IOError:
                return False, f"Sorry, unable to read file '{filename}'."
    return True, None


def check_dir_exists_or_creatable(dirname):
    """If dirname exists, all good; otherwise try to create it.  Return False and error message if unable."""
    if not os.path.exists(dirname):
        print(f"Creating directory {dirname}...")
        try:
            os.makedirs(dirname)
        except OSError:
            return False, f"Sorry, can't create directory path '{dirname}', please enter a different one."
    elif not os.path.isdir(dirname):
        return False, f"Sorry, '{dirname}' exists but is not a directory, please enter a different name."
    return True, None


def prompt_with_checker(prompt, default, check_function):
    """Prompt the user for a value and check their answer.  If there's a problem then explain
    and prompt again until their answer meets criteria."""
    ok = False
    answer = None
    while not ok:
        if default is not None:
            answer = get_input(f"\n{prompt} [{default}]: ")
            if not answer:
                answer = default
        else:
            answer = get_input(f"\n{prompt}: ")
        ok, error_message = check_function(answer)
        if not ok:
            print(error_message)
    return answer


def check_write_config(config_contents, config_path):
    """Return True if able to write config to config_path, False otherwise."""
    try:
        config.write_config(config_contents, config_path)
        return True
    except (NotADirectoryError, OSError):
        return False


def get_min_length_proportion(args_min_length_proportion, is_interactive):
    min_length_proportion = str(config.DEFAULT_MIN_LENGTH_PROPORTION)
    if args_min_length_proportion:
        min_length_proportion = args_min_length_proportion
        ok, error_message = check_proportion(min_length_proportion)
        if not ok:
            print(f"{error_message}\nPlease try again with a different value for --min_length_proportion", file=sys.stderr)
            sys.exit(1)
    elif is_interactive:
        min_length_proportion = prompt_with_checker("GenBank sequences will be filtered to retain only those whose length is at least this proportion of the RefSeq length",
                                                    min_length_proportion, check_proportion)
    return min_length_proportion


def get_max_N_proportion(args_max_N_proportion, is_interactive):
    max_N_proportion = str(config.DEFAULT_MAX_N_PROPORTION)
    if args_max_N_proportion:
        max_N_proportion = args_max_N_proportion
        ok, error_message = check_proportion(max_N_proportion)
        if not ok:
            print(f"{error_message}\nPlease try again with a different value for --max_N_proportion", file=sys.stderr)
            sys.exit(1)
    elif is_interactive:
        max_N_proportion = prompt_with_checker("GenBank sequences will be filtered to retain only those with at most this proportion of 'N' or ambiguous bases",
                                               max_N_proportion, check_proportion)
    return max_N_proportion


def get_user_fasta(args_fasta, is_interactive):
    fasta = ''
    if args_fasta is not None:
        fasta = args_fasta
        ok, error_message = check_optional_file_readable(fasta)
        if not ok:
            print(f"{error_message}\nPlease try again with a different file for --fasta.", file=sys.stderr)
            sys.exit(1)
    elif is_interactive:
        fasta = prompt_with_checker("If you have your own fasta file, then enter its path", "", check_optional_file_readable)
    return fasta


def get_workdir(args_workdir, is_interactive):
    if args_workdir:
        workdir = args_workdir
        ok, error_message = check_dir_exists_or_creatable(workdir)
        if not ok:
            print(f"{error_message}\nPlease try again with a different path for --workdir.", file=sys.stderr)
            sys.exit(1)
    else:
        workdir = prompt_with_checker("Enter directory where sequences should be downloaded and trees built", ".", check_dir_exists_or_creatable)
    return workdir


def make_config(config_contents, workdir, refseq_id, taxid, args_config, is_interactive):
    config_path_default = f"{workdir}/viral_usher_config_{refseq_id}_{taxid}.toml"
    if args_config:
        config_path = args_config
        if not check_write_config(config_contents, config_path):
            print(f"Unable to write to --config {config_path}.  Please try again with a different --config path.")
            sys.exit(1)
    elif is_interactive:
        config_ok = False
        while not config_ok:
            config_path = get_input(f"\nEnter path for config file [{config_path_default}]: ") or config_path_default
            config_ok = check_write_config(config_contents, config_path)
            if not config_ok:
                print(f"Unable to write config to {config_path}.")
            else:
                print(f"Wrote config file to {config_path}")
    else:
        config_path = config_path_default
        if not check_write_config(config_contents, config_path):
            print(f"Unable to write to default config path {config_path}.  Please try again with a different --config path.")
            sys.exit(1)
    return config_path


def handle_init(args):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    ncbi = ncbi_helper.NcbiHelper()
    if args.refseq:
        refseq_id = args.refseq
        taxid = str(ncbi.get_taxid_for_refseq(refseq_id))
        if args.taxonomy_id:
            if taxid != args.taxonomy_id:
                if taxid is None:
                    print(f"No taxid for refseq GI for {refseq_id}")
                # TODO: it's not a problem if the two taxids have an ancestor-descendant relationship -- look it up.
                print(f"\nNOTE: RefSeq ID {refseq_id} is associated with Taxonomy ID {taxid}, not the provided Taxonomy ID {args.taxonomy_id}.\n")
                taxid = args.taxonomy_id
    elif args.taxonomy_id:
        taxid = args.taxonomy_id
        refseq_id = prompt_refseq_id(ncbi, taxid)
    elif args.species:
        species = args.species
        taxid = prompt_taxonomy_id(ncbi, species)
        refseq_id = prompt_refseq_id(ncbi, taxid)
    else:
        species = get_input("\nEnter viral species name: ").strip()
        if not species:
            print("Can't proceed without a species name.")
            sys.exit(1)
        taxid = prompt_taxonomy_id(ncbi, species)
        refseq_id = prompt_refseq_id(ncbi, taxid)
    assembly_id = ncbi.get_assembly_acc_for_refseq_acc(refseq_id)
    if not assembly_id:
        print(f"Could not find assembly ID for RefSeq ID {refseq_id} -- can't download RefSeq.")
        sys.exit(1)

    # If --refseq and --workdir are given then accept defaults for other options
    is_interactive = not (args.refseq and args.workdir)

    min_length_proportion = get_min_length_proportion(args.min_length_proportion, is_interactive)
    max_N_proportion = get_max_N_proportion(args.max_N_proportion, is_interactive)
    fasta = get_user_fasta(args.fasta, is_interactive)
    workdir = get_workdir(args.workdir, is_interactive)

    viral_usher_version = importlib.metadata.version('viral_usher')
    config_contents = {
        "viral_usher_version": viral_usher_version,
        "refseq_acc": refseq_id,
        "refseq_assembly": assembly_id,
        "taxonomy_id": taxid,
        "min_length_proportion": min_length_proportion,
        "max_N_proportion": max_N_proportion,
        "extra_fasta": fasta,
        "workdir": os.path.abspath(workdir),
    }
    config_path = make_config(config_contents, workdir, refseq_id, taxid, args.config, is_interactive)

    print(f"\nReady to roll!  Next, try running 'viral_usher build --config {config_path}'\n")
