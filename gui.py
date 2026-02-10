import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mailer', action='store_true')
    namespace = parser.parse_args()

    if namespace.mailer:
        from abstractd.mailer import main as mailer
        mailer()
    else:
        from abstractd.frontend import main as abstracts
        abstracts()
