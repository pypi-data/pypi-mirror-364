import argparse
from deckgen.decks.generator import DeckGen
from deckgen.reader.file_reader import FileReader
from deckgen.splitter.text_splitter import TextSplitter
from deckgen.pipelines.qa_pipeline import QAToolKit
from typing import Optional
import os

from deckgen.utils.cli import define_generate_parser
from deckgen.utils.cli import define_env_parser


def main():
    parser = argparse.ArgumentParser(
        prog="deckgen", description="Generate decks from text files."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_command = define_generate_parser(subparsers)
    env_command = define_env_parser(subparsers)

    # Parse the arguments
    args = parser.parse_args()

    if args.command == generate_command:
        print(f"Generating deck from {args.input_file} with name {args.name}")
        generate_deck_from_file(
            input_file=args.input_file,
            deck_name=args.name,
            dst=args.output,
            deck_description=None,  # Optional description can be added later
        )

    elif args.command == env_command:
        if not args.api_key:
            raise ValueError("API key is required for authentication.")

        if args.organization_id:
            print(f"Setting OpenAI organization ID to {args.organization_id}")
            os.environ["OPENAI_API_ORGANIZATION"] = args.organization_id

        if args.project_id:
            print(f"Setting OpenAI project ID to {args.project_id}")
            os.environ["OPENAI_API_PROJECT"] = args.project_id

        print(f"Setting OpenAI API key.")
        os.environ["OPENAI_API_KEY"] = args.api_key


def generate_deck_from_file(
    input_file: str,
    deck_name: str,
    dst: Optional[str] = None,
    deck_description: Optional[str] = None,
) -> None:
    """
    Generates a deck from the specified input file.

    :param input_file: Path to the input file.
    :param deck_name: Name of the deck to be generated.
    :param dst: Optional destination directory for the generated deck file.
        If not provided, the deck will be saved in the current directory.
    :param deck_description: Optional description for the deck.
    """
    reader = FileReader(input_file)
    content = reader.get_content()
    print("Content read from file:", content)
    text_splitter = TextSplitter(document=content)
    chunks = text_splitter.split_text(
        method="length", chunk_overlap=100, chunk_size=500
    )

    print("Content after splitting:", chunks)

    qa_list = []
    for chunk in chunks:
        print("Processing chunk:", chunk.get_content())
        qa_toolkit = QAToolKit(input_text=chunk.get_content())
        qa_list.extend(qa_toolkit.generate_qa())

    deck_gen = DeckGen(input_text=content)
    deck = deck_gen.generate_deck(
        qa_list=qa_list, deck_name=deck_name, deck_description=deck_description
    )

    print("Generated Deck:", deck.name)
    if not dst:
        dst = "output.apkg"
    deck.generate_anki_deck(dst)
