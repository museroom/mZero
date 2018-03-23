import os
import subprocess
import threading
import logging
import argparse

logger = logging.getLogger('zero')


def count_zero(filename, chunksize=0):
    if os.path.getsize(filename) == 0:
        return 0
    if chunksize == 0:
        chunksize = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        zeros = 0
        while True:
            data = f.read(chunksize)
            if not data:
                break;
            zeros += len([b for b in data if b == 0])
    percent = zeros / os.path.getsize(filename) * 100
    logger.info("{:6.2f}% {}".format(percent, filename))
    return percent


def search_dir(dir='.', recursive=False):
    logger.info('folder={} recursive={}'.format(
        dir, recursive
    ))
    try:
        if not recursive:
            targets = [
                os.path.join(dir, file)
                for file in os.listdir(dir)
                if not os.path.isdir(os.path.join(dir, file))
            ]
        else:
            targets = []
            for path, dirs, files in os.walk(dir):
                for name in files:
                    targets.append(os.path.join(path, name))
    except Exception as e:
        logger.error('Open {} error'.format(dir))
        raise e
    finally:
        logger.debug('success open {}'.format(dir))
        logger.info('total targets:{}'.format(len(targets)))

    return targets


def main():
    argparser = argparse.ArgumentParser(
        description="Zero file detection after mDrive migration")
    argparser.add_argument(
        '-d', '--dir', action='store', dest='dir',
        help='Directory to search', default='.')
    argparser.add_argument(
        '-r', '--recursive', action='store_true', dest='recursive',
        help='Recusive search child', default=False)
    argparser.add_argument(
        '-t', '--threshold', action='store', dest='threshold',
        help='Zero detection threshold', default=50)
    argparser.add_argument(
        '-s', '--chunk_size', action='store', dest='chunksize',
        help='Chunk Size', default=0)
    args = argparser.parse_args()
    logger.debug('args: dir:"{}" / recursive:"{}"'.format(
        args.dir, args.recursive))

    try:
        targets = search_dir(args.dir, args.recursive)
    except Exception as e:
        logger.error('Error search_dir:{}'.format(e))

    threshold = float(args.threshold)
    for target in targets:
        try:
            percent_zero = count_zero(target, args.chunksize)
            if percent_zero > threshold:
                print("Not ok: {:6.2f}%\t{}".format(
                    percent_zero, target))
        except Exception as e:
            logger.error('{} error: {}'.format(target, e))


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    # logger.setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)

    # logging.basicConfig(
    #     level=logging.DEBUG,
    # )

    # log_fh = open('debug.log', 'w', encoding='utf-8')
    # ch = logging.StreamHandler(log_fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    # logging.basicConfig( level=logging.ERROR )

    main()
