import argparse
import bs4
import csv
import lxml
import requests
import sys
import urllib.parse
import validators

from util import Node, StackFrontier, QueueFrontier


def main():

    if len(sys.argv) == 3:
        (first_work, second_work) = parse_arguments()

    elif len(sys.argv) == 1:
        first_work = input("Link of the first work on the Crossover Wiki: ")
        second_work = input("Link of the second work on the Crossover Wiki: ")

    else:
        sys.exit("Invalid usage.")

    source = validate(first_work)

    if source is None:
        sys.exit("First work not found.")

    target = validate(second_work)

    if target is None:
        sys.exit("Second work not found.")

    path = shortest_path(source, target)
    
    print_result(path, source)


def shortest_path(source, target):
    """
    Returns the shortest list of articles
    that connect the source to the target.

    If no possible path, returns None.
    """

    # If source and target coincide, return empty path
    if source == target:
        return ""

    # Keep track of number of states explored
    num_explored = 0

    # Initialize frontier to just the starting position
    start = Node(state=source, parent=None, action=get_title_for_work(source))
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    # Keep looping until solution found
    while True:

        # If nothing left in frontier, then no path
        if frontier.empty():
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        num_explored += 1

        # Mark node as explored
        explored.add(node.state)

        # Add neighbors to frontier
        for state, title in neighbors_for_work(node.state):

            if not frontier.contains_state(state) and state not in explored:

                child = Node(state=state, parent=node, action=title)

                # If node is the goal, then we have a solution
                if child.state == target:
                    titles = []
                    ids = []
                    while child.parent is not None:
                        titles.append(child.action)
                        ids.append(child.state)
                        child = child.parent
                    titles.reverse()
                    ids.reverse()
                    solution = list(zip(titles, ids))
                    return solution
                
                frontier.add(child)


def parse_arguments():
    """
    Parses command-line arguments
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument("first_work", help="the URL of the first work on the Crossover wiki")
    parser.add_argument("second_work", help="the URL of the second work on the Crossover wiki")
    args = parser.parse_args()
    return (args.first_work, args.second_work)


def validate(url):
    res = requests.get(url)
    if res.status_code == 200:
        return url
    else:
        return None


def get_title_for_work(url):
    """
    Returns the title for the work provided as a parameter
    """

    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    title = soup.select("title")[0].getText().split(" |")[0]
    return title


def neighbors_for_work(work_url):
    """
    Returns (work_url, work_title) pairs for works
    which are connected with the work provided as a parameter.
    """
    base_url = "https://fictionalcrossover.fandom.com"
    res = requests.get(work_url)
    soup = bs4.BeautifulSoup(res.text, "lxml")

    works_urls = [base_url + work.attrs["href"] for work in soup.select("table a[href^='/wiki/']") if "#" not in str(work) and "?" not in str(work)]
    works_titles = [get_title_for_work(work_url) for work_url in works_urls]

    neighbors = list(zip(works_urls, works_titles))

    return neighbors


def print_result(path, source):
    """
    Prints the resulting path
    """

    if path is None:
        print("\nArticles are not connected.")
    elif path == "":
        print("\nThe two articles coincide.")
    else:
        degrees = len(path)
        if degrees == 1:
            print(f"\n{degrees} degree of separation.\n")
        else:
            print(f"\n{degrees} degrees of separation.\n")

        path = [(get_title_for_work(source), source)] + path

        for i in range(degrees + 1):
            print("-> ", end="")
            print(f"{path[i][0]} - {path[i][1]}")


if __name__ == "__main__":
    main()
