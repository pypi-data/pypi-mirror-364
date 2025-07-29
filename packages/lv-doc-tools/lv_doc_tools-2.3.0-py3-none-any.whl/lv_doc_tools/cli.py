"""
The main lv_doc_tool
"""
import json
import argparse
import sys
from lv_doc_tools.generator import Doc_Generator
from lv_doc_tools.caraya_runner import Caraya_Runner
from lv_doc_tools.caraya_parser import Caraya_Parser
from lv_doc_tools.publisher import Publisher
from lv_doc_tools.cleaner import Cleaner

from lv_doc_tools.verifybranch import verify_and_update_branch

# asciidoctor-pdf -a pdf-themedir=../../../lv_doc_tools/src/lv_doc_tools --theme  ../../../lv_doc_tools/src/lv_doc_tools/RS_theme.yml hitachi-testing.adoc


def main():

    parser = argparse.ArgumentParser(
        description="Generate documentation for LabView projects using lv_doc_tools."
    )
    parser.add_argument(
        "--config",
        required=True,
        type=str,
        help="Path to the configuration JSON file.",
    )

    parser.add_argument(
        "--to-confluence",
        action="store_true",
        help="If set, publish generated files to Confluence.",
    )

    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="If set,the cleaner will not remove the files and folders from output folder.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging purposes.",
    )

    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip running tests. Documentation will build from previous results, if any.",
    )
    parser.add_argument(
        "--no-antidoc",
        action="store_true",
        help="If set, skip call to antidoc - just build docs from existing adoc files.",
    )
    parser.add_argument(
        "--no-uml-diags",
        action="store_true",
        help="If set, skip call to plant uml diags.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="skip verification and updating correct branch"
    )
    args = parser.parse_args()

    try:
        with open(args.config, "r", encoding="utf-8") as fh:
            config = json.load(fh)
            if args.verbose:
                print(f"Loaded configuration: {config}")

            expected_branch = config.get("Expected_branch")
            if not expected_branch:
                print("❌'expected_branch' not found in config.")
                sys.exit(1)

            # Branch check
            if not args.no_verify:
                verify_and_update_branch(expected_branch)
            
            # Run tests
            if not args.no_tests:
                mycaraya = Caraya_Runner(config)
                mycaraya.run_tests()

            # Only perform cleanup logic if --no-clean is NOT set
            # Perform partial cleaning if no_tests flag is set
            if not args.no_clean or args.no_tests:
                mycleaner = Cleaner(config)

                if args.no_clean and args.no_tests:
                    print("Skipping full clean due to --no-clean, but running partial clean due to --no-tests.")
                    mycleaner.clean_output_dir(partial_clean=True)
                elif not args.no_clean and args.no_tests:
                    print("Performing partial clean (keeping test results).")
                    mycleaner.clean_output_dir(partial_clean=True)
                elif not args.no_clean:
                    print("Performing full clean.")
                    mycleaner.clean_output_dir()
            else:
                print("Cleanup fully skipped due to --no-clean.")


            
            mycarayaparser = Caraya_Parser(config)
            mycarayaparser.process_xml_files()

            # Generate documentation
            dg = Doc_Generator(config)
            dg.build_docs(no_antidoc=args.no_antidoc, no_uml_diags=args.no_uml_diags)

            print("Documentation built successfully!")
            if args.to_confluence:
                if args.verbose:
                    print("Publishing to Confluence...")
                mypublisher = Publisher(config)
                mypublisher.publish_to_confluence()

            
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON in '{args.config}'.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
