use Time::HiRes qw(time);

if ( $#ARGV < 1 ) {
    print 'SYNTAX:
    perl move-it-lazy-pods.pl POD_PREFIX DELAY

PARAMETERS:
    POD_PREFIX    prefix of that pods name must match
    DELAY         minimal duration between two records

DESCRIPTION:
    This script prints a time series of CPU usage for group of pods selected
    with the prefix POD_PREFIX. This script relies on the Kubernetes CLI 
    command kubectl.
';
    exit 1;
}

$pod_prefix = $ARGV[0];
$delay = $ARGV[1];

$command = 'kubectl top pods';

@cpu_usage_history = ();
$origin            = time();

for ( my $n = 0 ; ( $n < 5 ) ; ++$n ) {
    my @output = `$command`;

    # Removes header
    shift @output;

    foreach my $line (@output) {
        my @states = split( ' ', $line );

        # Found a pod which name matches the prefix POD_PREFIX
        if ( $states[0] =~ m/^$pod_prefix/ ) {
            # print "@states\n";
            $pod_name = $states[0];
            $cpu_usage_int = $states[1];
            $cpu_usage_int =~ s/m$//;
            # push @cpu_usage_history, [$pod_name, time() - $origin, $cpu_usage_int ];
            print join(";", $pod_name, time() - $origin, $cpu_usage_int), "\n"
        }
    }
    sleep($delay)
}

# foreach my $step (@cpu_usage_history) {
#     @record = @$step;
#     print $record[0], ';', $record[1], ';', $record[2], "\n";
# }
