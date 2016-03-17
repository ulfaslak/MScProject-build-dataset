"""Run all functions that load and cache data from remote."""

from build_dataset.workers import load_sensible_data as lsd
from build_dataset.analysis import location_reference as locref
from build_dataset.analysis import timezone_reference as tzref


tc0 = {
	'hours': range(24),
	'days': range(7),
	'spans': [
		("06/01/14", "24/01/14"),
		("03/02/14", "16/05/14"),
		("01/09/14", "05/12/14"),
		("02/06/14", "20/06/14")
	]
}
tc1 = {
	'hours': range(24),
	'days': range(7),
	'spans': [
		("17/05/14", "01/06/14"),
		("06/12/14", "21/12/14")
	]
}
tc2 = {'hours': range(24),
	'days': range(7),
	'spans': [
		("01/01/14", "05/01/14"),
		("25/01/14", "02/02/14"),
		("14/04/14", "20/04/14"),
		("21/06/14", "30/08/14"),
		("22/12/14", "31/12/14")
	]
}

for i, tc in enumerate([tc0, tc1, tc2]):

    print "## ----------------- ##"
    print "## Building for tc%d ##" % i
    print "## ----------------- ##"

    print "Location Reference..."
    locref.Load_location_reference(tc, load_cached=False)
    print "success!\n"
    print "Timezone Reference..."
    tzref.Load_timezone_reference(time_constraint, load_cached=False)
    print "success!\n"

    print "Iterating over datasets:"
	for dataset in ["calllog", "sms", "screen", "stop_locations", "bluetooth"]:
        print "\tBuilding '%s'..." % dataset
        lsd.load(tc, dataset, load_cached=False)
        print "\tsuccess!\n"