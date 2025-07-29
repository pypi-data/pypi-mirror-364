import sys
from codepeek.extractor import RepoExtractor

def main():
    if len(sys.argv) < 3:
        print("Usage: codepeek <github_repo_url> <output_file>")
        print("Example: codepeek https://github.com/user/repo output.txt")
        sys.exit(1)

    repo_url = sys.argv[1]
    output_file = sys.argv[2]

    if not repo_url.startswith('https://github.com/'):
        print("Error: Only GitHub repositories are supported")
        sys.exit(1)

    try:
        extractor = RepoExtractor()
        file_size = extractor.extract_repo(repo_url, output_file)
        print(f"Extraction completed: {output_file} ({file_size:.1f}MB)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
