import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mailer', action='store_true')
    parser.add_argument('-c', '--certificates', action='store_true')
    namespace = parser.parse_args()

    if namespace.mailer and namespace.certificates:
        raise ValueError("--mailer and --certificates are mutually exclusive!")

    if namespace.mailer:
        from abstractd.mailer import main as mailer
        mailer()
    elif namespace.certificates:
        from abstractd.mailer import main as mailer
        mailer('certificates')
    else:
        from abstractd.frontend import main as abstracts
        abstracts()
