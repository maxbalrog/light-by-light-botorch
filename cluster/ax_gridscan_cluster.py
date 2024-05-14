'''
Script for launching ax client gridscan on cluster 
(with submitit support)

Author: Maksim Valialshchikov, @maxbalrog (github)
'''
from lbl_botorch.optimization import run_axclient_gridscan_batch


def main(params_yaml):
    run_axclient_gridscan_batch(params_yaml)
    print('Script finished...')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimization specifications')
    parser.add_argument('--params_yaml', metavar='path', required=True,
                        help='the path to yaml with optimization details')
    args = parser.parse_args()
    
    main(params_yaml=args.params_yaml)