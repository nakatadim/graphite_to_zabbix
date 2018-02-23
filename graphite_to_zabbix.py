#!/usr/bin/python

import optparse
import sys
import urllib2

def usage():
    print 'Usage:'
    print '\tcheck_graphite_data <options>'
    print 'Options:'
    print '\t-u <url> --url=<url>\t\tGraphite graph URL'
    print '\t-U <user> --user=<username>\t\tBasic auth user'
    print '\t-P <password> --password=<password>\t\tBasic auth password'
    print '\t-R <ratio> --reduction=<number>\tIf we want to reduce the number of values to be calculated. For example 10 means calculating every tenth value'
    print '\t--d1 <url> --d2 <url>\t\tDiff the latest values between two graphs'
    print '\tExample: check_graphite_data_artirix -u "http://graphite.artirix.com/render?target=apache.response.200&from=-12hours" -U nasko -P xxx'
    


def pull_graphite_data(url, user=None, password=None):
    """Pull down raw data from Graphite"""
        
    # Make sure the url ends with '&format=raw'
    if not url.endswith('&format=raw'):
        url = url + '&format=raw'
    if user and password:
        authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
        authinfo.add_password(None, url, user, password)
        handler = urllib2.HTTPBasicAuthHandler(authinfo)
        myopener = urllib2.build_opener(handler)
        opened = urllib2.install_opener(myopener)
    data = urllib2.urlopen(url).read()
    # be session friendly
    data.close()
    return data

def eval_graphite_data(data, reduction_ratio):
    """Get the most recent correct value from the data"""
    total = 0
    count = 0

    sample_period = int(data.split('|')[0].split(',')[-1])
    all_data_points = data.split('|')[-1].split(',')
    for x in all_data_points[-len(all_data_points)::reduction_ratio]:
        try:
            if x != "None":
                count += 1
            total += float(x)
        except ValueError:
	    pass

    count -= 1
    if count != 0:
        data_value = float( total / count )
    else:
        data_value = 0.0
    return data_value

def get_value(url, reduction_ratio=1,  user=None, password=None):
    """Get the value from a Graphite graph"""

    data = pull_graphite_data(url, user, password)
    data_value = eval_graphite_data(data, reduction_ratio)
    return data_value


def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('-u', '--url', help='Graphite graph URL')
    parser.add_option('-R', '--reduction', type=int, default=1, help='If we want to reduce the number of values to be calculated. For example 10 means calculating every tenth value')
    parser.add_option('--d1', help='Diff the latest values between two graphs')
    parser.add_option('--d2')
    parser.add_option('-U', '--user', help='Username')
    parser.add_option('-P', '--password', help='Password')

    parser.set_usage("%prog [options]\n"
        '\tExample: %prog -u "http://graphite.sc.artirix.com/render?target=apache.response.200&from=-12hours" -U nasko -P xxx'
    )

    opts, args = parser.parse_args(argv)

    url = opts.url
    reduction_ratio = opts.reduction
    diff1 = opts.d1
    diff2 = opts.d2
    user = opts.user
    password = opts.password


    if (url == None) and not diff1 and not diff2:
        parser.print_usage()
        sys.exit(1)

    if (diff1 is None and diff2 is not None) or (diff1 is not None and diff2 is None):
        parser.print_usage()
        sys.exit(1)

    if diff1 or diff2:
        graphite_data1 = get_value(diff1, reduction_ratio, user, password)
        graphite_data2 = get_value(diff2, reduction_ratio, user, password)
        graphite_data = abs(graphite_data1 - graphite_data2)
    else:
        graphite_data = get_value(url, reduction_ratio, user, password)

    print graphite_data

if __name__ == '__main__':
    main(sys.argv[1:])
