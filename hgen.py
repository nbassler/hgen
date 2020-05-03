import sys
import argparse
import logging

import numpy as np

logger = logging.getLogger(__name__)

__version__ = '0.1'


class Config:
    def __init__(self, fn):
        """
        """
        self.header_name = "_FOOBAR"
        self.max_line_length = 120
        self.nrows = 0
        self.ncols = 0
        self.types = []
        self.varnames = []
        self.digits_after_dot = 3
        self.read_config(fn)

    def read_config(self, fn):
        """
        """
        logger.info("Reading {}".format(fn))
        with open(fn, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            logger.debug("parsing >{}".format(line))
            if line[0] == '@':
                key, s = line[1:].split()[0:2]
                logger.debug("Found key {} with contents {}".format(key, s))

                if key.isdigit():
                    self.ncols += 1
                    # col = int(key)
                    _params = line[1:].split()[1:]
                    self.varnames.append(_params[-1])
                    _datatype = _params[:-1]
                    _space = ' '
                    self.types.append(_space.join(_datatype))
                else:
                    if key == "header_name":
                        self.header_name = s
                    if key == "max_line_length":
                        self.max_line_length = int(s)
                    if key == "digits_after_dot":
                        self.digits_after_dot = int(s)
                    if key == "indent_spaces":
                        self.indent_spaces = int(s)

        self.data = np.loadtxt(fn, comments=("#", "@"))
        self.nrows = len(self.data)

        logger.info("header_name = {}".format(self.header_name))
        logger.info("max_line_length = {}".format(self.max_line_length))
        logger.info("digits_after_dot = {}".format(self.digits_after_dot))
        logger.info("indent_spaces = {}".format(self.indent_spaces))
        logger.info("ncols = {}".format(self.ncols))
        logger.info("nrows = {}".format(self.nrows))

        for i, type in enumerate(self.types):
            logger.info("Col: {}   Type: {}   VarName: {}".format(i, self.types[i], self.varnames[i]))

    def write_data(self, fn):
        """
        """

        s = ""
        s += "#ifndef {}\n".format(self.header_name)
        s += "#define {}\n".format(self.header_name)
        s += "\n\n"

        for c in range(self.ncols):
            s += "{} {}[{}] = ".format(self.types[c], self.varnames[c], self.nrows) + "{"
            _s = ''
            _newline = True
            old_token = ''
            for r in range(self.nrows):
                token = "{val:.{precision}e}".format(val=self.data[r, c], precision=self.digits_after_dot)

                # if we start a new line _s, prepare it first with indention
                if(_newline):
                    _s = '\n'
                    _s += ' ' * (self.indent_spaces)
                    if old_token:
                        _s += old_token
                    _newline = False

                # keep adding tokens, until we exceed line limit
                _ss = ' ' + token

                if r != (self.nrows - 1):
                    _ss += ","

                if (len(_s) + len(_ss)) < self.max_line_length:
                    # there is still room to add this token to this line.
                    _s += _ss
                else:
                    # we need to start a new line
                    old_token = _ss
                    s += _s
                    _newline = True

            # add whatever there is left of unfinished lines
            s += _s

            s += "}\n\n"

        s += "#endif /* {} */".format(self.header_name)

        logger.info("Writing {}".format(fn))
        with open(fn, 'w') as f:
            f.write(s)


def main(args=sys.argv[1:]):
    """
    Main function
    """

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="input data filename, must contain a descriptive header", type=str)
    parser.add_argument("outfile", help="output .h filename", type=str)
    parser.add_argument("-v", "--verbosity", action='count', help="increase output verbosity", default=0)
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parsed_args = parser.parse_args(args)

    if parsed_args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    elif parsed_args.verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    c = Config(parsed_args.infile)
    c.write_data(parsed_args.outfile)
    # print(c.data)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
