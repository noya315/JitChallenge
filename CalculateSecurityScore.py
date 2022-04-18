import sys
import os
import subprocess
import itertools
from gtrending import fetch_repos
from git import Repo, GitCommandError

"Cloning repos from git and build array of repos with requirements file."


def get_repos_with_reqs_file(repos):
    reps = {}
    repos_path = os.path.join(os.getcwd(), "repos")
    os.mkdir(repos_path)
    os.chdir(repos_path)
    for repo in repos:
        try:
            repo_path = os.path.join(os.getcwd(), repo['name'])
            if not os.path.exists(repo_path):
                requirements_path = repo_path + f'\\requirements.txt'
                Repo.clone_from(repo['url'], repo['name'], depth=1)
                if os.path.exists(requirements_path):
                    reps[repo['name']] = repo_path
                os.chdir(repos_path)
        except TimeoutError as e1:
            print(e1)
        except ConnectionError as e2:
            print(e2)
        except GitCommandError as e3:
            print(e3)

    return reps


"Create filtered data dictioanry for repositories."


def create_repos_filtered_data(fetch_data, repos_reqs_path):
    repos_filtered_data = {}
    for data in fetch_data:
        if data["name"] in repos_reqs_path.keys():
            score = calculate_score(repos_reqs_path[data["name"]])
            repo_data = {'Repository name': f'{data["name"]}',
                         'Author': f'{data["author"]}',
                         'url': f'{data["url"]}',
                         'Security score': score}

            repos_filtered_data[data["name"]] = repo_data
    return repos_filtered_data


"Run on a repository files and calculates how many packages is unused. "


def calculate_score(repo_path):
    os.chdir(repo_path)
    packages = set()
    for item in os.listdir(repo_path):
        if os.path.isdir(item) or item.endswith('.py'):
            packages.update(get_unused_packages_for_item(repo_path, item))
    return len(packages)



"Get unused packcages for item in repository."


def get_unused_packages_for_item(repo_path, item):
    packs = set()
    try:
        os.chdir(repo_path)
        p = subprocess.run(["pip-extra-reqs", f"{item}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = p.stderr.splitlines()
        for line in lines:
            line = line.decode()
            if line.find("in requirements.txt") != -1:
                pack_name = line.split(' ')[0]
                packs.add(pack_name)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
    return packs


"Print the filtered data about the repositories."


def print_filtered_data(filtered_data):
    for data in filtered_data.keys():
        print(f'{data} \n')
        for key, value in filtered_data[data].items():
            print(f' {key} : {value} \n')


def main():
    num_of_repos = int(sys.argv[1])

    print("Get trending repositories...")
    repos_data = fetch_repos(language="python")

    print("filter repos without requirements.txt file")
    repos = get_repos_with_reqs_file(repos_data)

    if len(repos) < num_of_repos:
        print(f'There are no {num_of_repos} repositories with requirements.txt, Print data for existing repositories.')
    elif len(repos) > num_of_repos:
        print(
            f'There are more than {num_of_repos} repositories with requirements.txt,'
            f' Print data for the first {num_of_repos} repositories.')
        repos = dict(itertools.islice(repos.items(), num_of_repos))

    print("Calculate score for repos")
    filtered_data_repos = create_repos_filtered_data(repos_data, repos)
    print_filtered_data(filtered_data_repos)


if __name__ == "__main__":
    main()
