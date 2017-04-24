from XAFCM import XAFCM


def main():
    string_A = "AAAAABCAADABCACABDADBDACADADABDABCADBABDAAAACABDABDBADBABCA"
    string_B = "ADABDBADBABDABCABDBABDABDBABCAAAAAACABDBABDBABDACA"
    xafcm = XAFCM(alphab_size=4, k=3, d=1, alpha="auto")
    xafcm.learn_models_from_string(string_A)
    xafcm.print_models_learned()
    xafcm.print_details_of_models_learned()

    list_bps, bits_total = xafcm.compress_string_based_on_models(string_B)
    print("Needed %d bits to compress string B" % bits_total)
if __name__ == "__main__":
    main()
