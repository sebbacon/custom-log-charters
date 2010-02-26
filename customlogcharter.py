#!/usr/bin/python

import sys
import re
from datetime import datetime, timedelta
skip_ips = ["93.97.158.26"]
html_template_head = """
  <head>
    <script type='text/javascript' src='http://www.google.com/jsapi'></script>
    <script type='text/javascript'>
      google.load('visualization', '1', {'packages':['annotatedtimeline']});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('datetime', 'Date');
        """

html_template_foot = """
        var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div'));
        chart.draw(data, {displayAnnotations: true});
      }
    </script>
  </head>

  <body>
    <div id='chart_div' style='width: 700px; height: 240px;'></div>

  </body>
</html>
"""
cols_html = """
        data.addColumn('number', '%s');
        data.addColumn('string', 'title1');
        data.addColumn('string', 'text1');"""
row_html = """
data.addRows([
          [new Date(%(year)s,%(month)s ,%(day)s, %(hour)s, 0, 0), %(value_seq)s],
        ]);
        """        
data_html = "%(count)s, undefined, undefined"

def get_data(file_handle):
    rows = []
    times = []
    buckets = {}
    start_date = None
    local_skip_ips = skip_ips[:]
    for line in file_handle:
        if not line.strip():
            continue
        ip = line.split()[0]
        if ip in local_skip_ips:
            continue
        local_skip_ips.append(ip)
        match = re.match(r".*\[([^\]]+).*", line)
        if match:
            when = datetime.strptime(match.group(1),
                                     "%d/%b/%Y:%H:%M:%S +0000")
            rounded = when.strftime("%d/%b/%Y:%H")
            when = datetime.strptime(rounded, "%d/%b/%Y:%H")
            if not start_date:
                start_date = when
            end_date = when
            val = buckets.setdefault(when, 0)
            buckets[when] = val + 1
    name = file_handle.name.split("/")[-1].split(".")[0]
    return name, start_date, end_date, buckets

def plot_data(sources):
    html = html_template_head
    for name, _, _, _ in sources:
        html += cols_html % name
    times = []
    start_date = min([x for _, x, _, _ in sources])
    end_date = max([y for _, _, y, _ in sources])
    when = start_date
    while when < end_date:
        times.append(when)
        when += timedelta(0,0,0,0,0,1)
    rows = []
    for when in times:
        value_seq = []
        for _, _, _, buckets in sources:
            values = {'year':when.year,
                      'month':when.month,
                      'day':when.day,
                      'hour':when.hour,
                      'count':buckets.get(when, 0)}
            value_seq.append(data_html % values)
        values['value_seq'] = ",".join(value_seq)
        rows.append(row_html % values)
    html += "\n".join(rows)
    html += html_template_foot
    print html

sources = [get_data(open(x, "r")) for x in sys.argv[1:]]
plot_data(sources)
