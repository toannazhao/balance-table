import sys, getopt
from ATUSsample import atusSampleAnalysis

def main(argv):
    sex = float("nan")
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hs:i:o:",["sex=","ifile=","ofile="])
    except getopt.GetoptError:
        print ('BalanceAnalysis.py -s <sex> -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('BalanceAnalysis.py -s <sex> -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-s", "--sex"):
            sex = arg
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print ('Sex is ', sex)
    print ('Input file is ', inputfile)
    print ('Output file is ', outputfile)
    atusSampleAnalysis(sex, inputfile, outputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
