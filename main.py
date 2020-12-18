import argparse

args__parser = argparse.ArgumentParser(description='A Matrix email to conversation bridge.')
args__parser.add_argument('--google-voice', action='store_true',
    help="""Enable the Google Voice text message module.
    In order to use it, you must configure Voice to forward text messages to your email address.""")

args = args__parser.parse_args()

print(args.google_voice)