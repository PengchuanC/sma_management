import click

from proc.commit.valuation_v2 import commit_valuation


@click.group()
def test():
    pass


@test.command()
def test_valuation():
    commit_valuation()


if __name__ == "__main__":
    test()
