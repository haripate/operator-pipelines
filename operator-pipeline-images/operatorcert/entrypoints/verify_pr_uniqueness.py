import argparse
import logging

from operatorcert import verify_pr_uniqueness


def setup_argparser() -> argparse.ArgumentParser:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Verify if submission is unique in the repository"
    )
    parser.add_argument("--pr-url", help="GitHub PR url")
    parser.add_argument(
        "--available-repositories",
        help="List of repository names (coma separated),"
        "with potentially duplicate PRs",
        default="redhat-openshift-ecosystem/operator-pipelines-test",
    )
    parser.add_argument("--bundle-name", help="Name of the bundle")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    return parser


def main() -> None:
    # Args
    parser = setup_argparser()
    args = parser.parse_args()

    # Logging
    log_level = "INFO"
    if args.verbose:
        log_level = "DEBUG"
    logging.basicConfig(level=log_level)

    # Logic
    # Verify, that there is no other PR opened for this Bundle
    repos = args.available_repositories.split(",")
    verify_pr_uniqueness(repos, args.pr_url, args.bundle_name)


if __name__ == "__main__":  # pragma: no cover
    main()
